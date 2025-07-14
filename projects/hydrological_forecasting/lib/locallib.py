from os import path as ospath
from os import makedirs as osmakedirs

import datetime as dt

import argparse

import json

from pandas import DataFrame, concat, date_range
from numpy import sqrt, array, NaN, roll
from random import sample
from math import ceil
from scipy import stats

from sklearn.metrics import r2_score, mean_squared_error

import torch
from torch.utils.data import DataLoader, Dataset
from torch.autograd import Function

import optuna

from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA

from matplotlib import pyplot as plt

from shapely.geometry import Polygon

from sklearn import preprocessing
from pickle import dump, load

import psycopg2

import logging

from database import extract_era5land, extract_pab, extract_cum_era5land, extract_cum_pab

def create_dir(filename):
    head, tail = ospath.split(filename)
    if not ospath.exists(head):
        osmakedirs(head)

def get_logging(basepath, logging_level):

    datetime = dt.datetime.now()

    ## setup logging
    log_filename = f"{basepath}logs/{datetime:%Y%m%dT%H%M%S}.log"
    create_dir(log_filename)

    logging.basicConfig(
        filename = log_filename,
        format = "%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s",
        filemode = 'a',
        level = logging_level)
    
    logging.getLogger('matplotlib.font_manager').disabled = True

    return logging, datetime


def plot_results(predictions, real, max_soil_loss=None, filename=None):

    x_data = predictions.squeeze().numpy()
    y_data = real.squeeze().numpy()

    if max_soil_loss is not None:
        tmp_df = DataFrame([x_data,y_data]).T
        tmp_df=tmp_df[tmp_df<=max_soil_loss].dropna()
        x_data = tmp_df[0].values
        y_data = tmp_df[1].values
    else:
        max_soil_loss = x_data.max()
        if max_soil_loss < y_data.max():
            max_soil_loss = y_data.max()

    RMSE = round(sqrt(mean_squared_error(x_data,y_data)),2)
    RRMSE = round(RMSE/y_data.mean()*100,2)
    # print(f"Root Mean Square Error: {RMSE}")
    R2 = round(r2_score(x_data,y_data),2)
    # print(f"R2 Error: {R2}")

    plt.figure(figsize=(10,10))
    plt.scatter(x_data,y_data)

    plt.plot( [0,max_soil_loss],[0,max_soil_loss], c='black',  )
    plt.grid(visible=True)

    plt.xlabel('Predictions')
    plt.ylabel('Real')
    plt.title(f"RMSE:{RMSE:.2f} | RRMSE:{RRMSE:.2f} | R2:{R2:.2f}")
    if filename is not None:
        plt.savefig(filename)
    else:
        plt.show()

def batch_data(df, start_date, lag_hours, lead_hours):
        
    start_data_date = df.index[0]
        
    ## lead hours
    lead_start_date = start_date + dt.timedelta(hours=1)
    lead_end_date = lead_start_date + dt.timedelta(hours=lead_hours-1)
    # lead_block = df[lead_start_date:lead_end_date]

    ## lag+lead hours
    lag_end_date = start_date
    lag_start_date = lag_end_date - dt.timedelta( hours = lag_hours-1 )
    if start_data_date > lag_start_date:
        first_available = start_data_date + dt.timedelta( hours = lag_hours )
        raise Exception(f"Start date not allowed: {start_date}, first available is {first_available}")
    lag_block = df[lag_start_date:lead_end_date]

    return lag_block

class Metadata():

    def __init__(self, json_meta) -> None:
        self.retrieveMetadata(json_meta)
    
    def retrieveMetadata(self, json_meta):

        # Load JSON data from file
        with open(json_meta, 'r') as file:
            data = json.load(file)
            file.close()
        
        self.basins = []
        basins_meta = data["basins"]
        for b in basins_meta:

            lon_min, lat_min = b["bbox"]['lon_min'], b["bbox"]['lat_min']
            lon_max, lat_max = b["bbox"]['lon_max'], b["bbox"]['lat_max']

            c_poly = Polygon([(lon_min, lat_min), (lon_min, lat_max), (lon_max, lat_max), (lon_max, lat_min)])
            station_id = [station['station_id'] for station in b['ground_stations'] if station['variable'] == 'streamflow'][0]

            new_basin = Basin( b["key"], b["name"], c_poly, station_id )
            self.basins.append(new_basin)

class Basin():

    def __init__(self, key, name, polygon, station_id) -> None:
        self.key = key
        self.name =name
        self.polygon = polygon
        self.station_id = station_id

        self.sims = []
    
    def get_streamflow(self, start_date, end_date, station_id, dataset_name='PAB'):
        self.flow_station = station_id
        if dataset_name == "PAB":
            df = extract_pab(start_date, end_date, "streamflow", station_id=self.flow_station)
        else:
            raise Exception(f"Not available data {self.flow_station}")

        ## check the streamflow
        try:
            ### check if is void
            if df.shape[1] == 0:
                raise
            ### replace negative numbers
            df[df.columns[0]] = df[df.columns[0]].apply(lambda x: 0 if x < 0 else x)
        except Exception as e:
            m = f"Station {station_id} does not have data between {start_date} and {end_date}"
            self.logging.error(m)
            raise Exception(m)

        return df
    
    def get_data(self, start_data_date, end_data_date, variable, params=None, neighbors=1):
        
        var_type = params["type"]
            
        if var_type == "raw":
            if variable == "precipitation":
                
                if params["provider"] == "era5land":
                    v = "tp"
                    
                    df = extract_era5land(
                        start_data_date, end_data_date, v, poly=self.polygon, n=neighbors)

            elif variable == "temperature":
            
                if params["provider"] == "era5land":
                    v = "2t"
                    
                    df = extract_era5land(
                            start_data_date, end_data_date, v, poly=self.polygon, n=neighbors)

            elif variable == "streamflow":
            
                df = self.get_streamflow(
                    start_date=start_data_date,
                    end_date=end_data_date,
                    station_id=self.station_id)

        ## derivated variables
        elif params["type"] == "cumulative":
            
            if variable == "precipitation":
            
                if params["provider"] == "era5land":
                    v = "tp"
                    
                    df = extract_cum_era5land(
                        start_data_date, end_data_date, v, 
                        cum_lag=params["cum_interval"], poly=self.polygon, n=neighbors)

            elif variable == "temperature":
            
                if params["provider"] == "era5land":
                    v = "2t"
                    
                    df = extract_cum_era5land(
                        start_data_date, end_data_date, v, 
                        cum_lag=params["cum_interval"], poly=self.polygon, n=neighbors)
            
            elif variable == "streamflow":
            
                if params["provider"] == "PAB":
                    df = extract_cum_pab(
                        start_data_date, end_data_date, "streamflow",
                        cum_lag=params["cum_interval"], station_id=self.station_id)

            else:
                logging.error(f"Not a valid variable: {variable}")
                df = None
    
        else:
            if variable == "dummy":
                
                dr = date_range(start=start_data_date, end=end_data_date, freq='1H')
                df = DataFrame(index=dr)

                if params["type"] == "hourofday":
                    variable = "dummy_hour"
                    unique_values = set(df.index.hour.to_list())
                    for u in unique_values:
                        hours = [0 if i != u else 1 for i in df.index.hour]
                        df[f"{variable}_{u}"] = hours
                elif params["type"] == "dayofyear":
                    variable = "dummy_day"
                    unique_values = set(df.index.dayofyear.to_list())
                    for u in unique_values:
                        days = [0 if i != u else 1 for i in df.index.dayofyear]
                        df[f"{variable}_{u}"] = days
                elif params["type"] == "monthofyear":
                    variable = "dummy_month"
                    unique_values = set(df.index.month.to_list())
                    for u in unique_values:
                        months = [0 if i != u else 1 for i in df.index.month]
                        df[f"{variable}_{u}"] = months
            
            else:
                logging.error(f"Not a valid variable: {variable}")
                df = None

        return f"{variable}_{var_type}", df ## df with columns all the points [raw] or all the unique_values [dummy]