# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 10:36:28 2019

@author: ariele
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from sklearn.impute import KNNImputer
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.tsa.stattools import pacf
import datetime

# suppress a warning
pd.options.mode.chained_assignment = None  # default='warn'


font = {'family' : 'STIXGeneral',
        'weight' : 'normal',
        'size'   : 22}
plt.rcParams['lines.linewidth'] = 1
plt.rc('font', **font)

plt.rcParams['mathtext.fontset'] = 'stix'


class Dataset_management():
    
    """inizializzazione della classe. L'ordine dei metodi è fondamentale
    per inizializzare bene il dataframe"""
    def __init__(self, string):
        self.string = string
     
        
    """Funzione per fare il parsing dei dati di consumo. genera il dataframe
    di base, con i dati grezzi"""
    def parsing_idro(self, start=None, end=None):
        try:
            self.df = pd.read_csv(self.string, sep=',')
            self.df.index = pd.to_datetime(self.df['index'],
                                            format="%Y-%m-%d %H:%M")
            self.df.drop(columns=self.df.columns[[0]], inplace=True)
            self.df = self.df.rename(columns = {'values': 'ts'}) 
        except KeyError:
            try:
                self.df = pd.read_csv(self.string, sep=',')
                self.df.index = pd.to_datetime(self.df['datetime'],
                                               format="%Y-%m-%d %H:%M:%S")
                self.df.drop(columns=self.df.columns[[0]], inplace=True)
                self.df = self.df.rename(columns = {'values': 'ts'}) 
            except KeyError:
                self.df = pd.read_csv(self.string, sep=';')
                self.df.index = pd.to_datetime(self.df['datetime'],
                                               format="%Y-%m-%d %H:%M:%S")
                self.df.drop(columns=self.df.columns[[0]], inplace=True)
                self.df = self.df.rename(columns = {'values': 'ts'}) 
        if start!=None and end!= None:
            self.df = self.df[start : end]
            #metto zeri fino alla data che desidero
            self.df.loc[end+ datetime.timedelta(hours=72)] = 0
            try: # serve per allungare la prediction
                self.df = pd.DataFrame(self.df.resample('H').bfill())
            except ValueError:
                self.df = self.df[~self.df.index.duplicated(keep='first')]
                self.df = pd.DataFrame(self.df.resample('H').bfill())
        return self.df
    
    """Funzione per fare il parsing dei dati di consumo. in questo caso da un
    dataset non clean in cui vanno specificati:
        - fname = nome del file con estensione e path
        - signal_name = nome della colonna nel file
        - time_name = nome della colonna contenente le date 
    sovrascrive direttamente il self.df """
    def signal_selector(self, fname, signal_name, time_name):
        self.string = fname
        self.df = pd.read_csv(self.string, sep=';')
        self.df.index = pd.to_datetime(self.df[time_name],
                                       format="%Y-%m-%d %H:%M:%S")
        self.df = pd.DataFrame(self.df[signal_name])
        self.df = self.df.rename(columns = {signal_name: 'ts'}) 
        return self.df
    
    """Funzione per plottare easy eassy la ts di partenza"""
    def plot_ts_basic(self, figsize, start_date, save=None):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        fig, ax = plt.subplots(figsize=figsize)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m')) 
        ax.format_xdata = mdates.DateFormatter('%Y-%m')
        ax.plot(self.df_hourly[start_date:], linewidth=1.5,
                label = 'Hourly data')   
        ax.plot(self.davg[start_date:], linewidth=1.5,
                label = 'Daily data') 
        ax.set_ylabel('(L/s)', fontsize=22)
        #ax.set_ylim((0.1,8.1))
        ax.grid(True)       
        fig.autofmt_xdate()
        fig.legend(bbox_to_anchor=(0.74,0.92), loc="center", bbox_transform=ax.transAxes,
            ncol=2)
        if save==True:
            plt.savefig('immagini/complete_ts200.png', dpi=200, bbox_inches='tight')
            plt.savefig('immagini/complete_ts400.png', dpi=400, bbox_inches='tight')
        plt.show()
        
    """Fuzione per fare i plot di solo una parte della time series"""    
    def plot_partial_prediction(self, start_date, n_days, figsize,
                                save=True):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + datetime.timedelta(days = n_days)
        fig, ax = plt.subplots(figsize=figsize)
        #ax.xaxis.set_major_locator(mdates.HourLocator(byhour=0))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d')) 
        ax.format_xdata = mdates.DateFormatter('%y-%m-%d')
        ax.plot(self.df_hourly[start_date:end_date], linewidth=1.5)
        ax.set_ylabel('(L/s)', fontsize=22)
        #•ax.set_ylim((0.5,4.9))
        ax.grid(True)          
        fig.autofmt_xdate()
        # fig.legend(bbox_to_anchor=(0.5,0.72), loc="center", bbox_transform=ax.transAxes,
        #     ncol=1)
        if save==True:
            plt.savefig('immagini/ts_partial200.png', dpi=200, bbox_inches='tight')
            plt.savefig('immagini/ts_partial400.png', dpi=400, bbox_inches='tight')
        plt.show()
        
    """Funzione per creare il dataframe con media giornaliera"""
    def daily_average(self):
        self.davg = self.df['ts'].resample('D').mean()
        self.davg = pd.DataFrame(self.davg)
        self.davg.index = pd.to_datetime(self.davg.index)
        self.davg = self.davg.rename(columns = {'ts': 'day average'})  
        if self.exclusion==True:
            self.davg = self.weekend_exclusion(self.exclusion, self.davg)
        if self.exclusion_bis == True:
            self.davg = self.year_exclusion(self.exclusion_bis,
                                            self.year_to_remove,
                                            self.davg)
        return self.davg
        
    """Funzione per creare il dataframe con media oraria"""
    def hourly_average(self):
        self.df_hourly = self.df['ts'].resample('h').mean() 
        self.df_hourly = pd.DataFrame(self.df_hourly)
        self.df_hourly.index = pd.to_datetime(self.df_hourly.index)
        self.df_hourly = self.df_hourly.rename(columns = {'ts': 'h average'}) 
        if self.exclusion==True:
            self.df_hourly = self.weekend_exclusion(self.exclusion, self.df_hourly)
        if self.exclusion_bis == True:
            self.df_hourly = self.year_exclusion(self.exclusion_bis,
                                                 self.year_to_remove,
                                                 self.df_hourly)
        return self.df_hourly
    
    """Filtro per lavorare sui nan presenti nel dataset. A seconda del metodo
    posso fare:
        fill with zeros -> li sostituisco con degli zeri che posso eliminare
        interpolat -> meh poco utile ma chissa
        rebuild -> se trovo un nan cerco valori storici simili"""
    def nan_filter(self, method):
        if method == 'fill with zero':
            self.df = self.df.fillna(value=0)
        elif method == 'interpolate':
            self.df = self.df.interpolate(method='cubic',
                                          limit_direction="both")
        elif method == 'rebuild':
            data = self.df.values
            self.imputer = KNNImputer(n_neighbors=24)
            self.imputer.fit(data)
            # Apply to data to have them
            self.imputed_data = self.imputer.fit_transform(data)
            # Create a df with imputed data
            self.df = pd.DataFrame(index = self.df.index,
                                   columns = ['ts'],
                                   data = self.imputed_data[:,0])
        return self.df
    
    """Uguale al precedente, solo che lavora sui resample dataframes"""
    def nan_filter2(self, method):
        if method == 'fill with zero':
            self.df_hourly = self.df_hourly.fillna(value=0)
            self.davg = self.davg.fillna(value=0)
        elif method == 'interpolate':
            self.df_hourly = self.df_hourly.interpolate(method='cubic',
                                          limit_direction="both")
            self.davg = self.davg.interpolate(method='cubic',
                                          limit_direction="both")
        elif method == 'rebuild':
            dataset_to_impute = self.df_hourly.copy()
            dataset_to_impute['hr'] = self.df_hourly.index.hour
            dataset_to_impute['day'] = self.df_hourly.index.dayofweek
            dataset_to_impute['month'] = self.df_hourly.index.month
            data1 = dataset_to_impute.values
            data2 = self.davg.values
            self.imputer1 = KNNImputer(n_neighbors=24)
            self.imputer2 = KNNImputer(n_neighbors=10)
            self.imputer1.fit(data1)
            self.imputer2.fit(data2)
            # Apply to data to have them
            self.imputed_data1 = self.imputer1.fit_transform(data1)
            self.imputed_data2 = self.imputer2.fit_transform(data2)
            # Create a df with imputed data
            self.df_hourly = pd.DataFrame(index = self.df_hourly.index,
                                          columns = ['h average'],
                                          data = self.imputed_data1[:,0])
            self.davg = pd.DataFrame(index = self.davg.index,
                                     columns = ['day average'],
                                     data = self.imputed_data2[:,0])
        return self.df
    
    """Filtro per eliminare i dati ripetuti in un lasso troppo breve.
    Inoltre vado a rimuovere gli zeri. Nel primo filtro ci metto anche 
    quello per i nan. AAndranno rivisti in futuro"""
    def first_filter(self, filter_zeros):
        delta = self.df.copy()
        delta['tvalue'] = self.df.index
        delta['delta'] = (delta['tvalue']-delta['tvalue'].shift(fill_value=0))
        cond = delta['delta']>np.timedelta64(30,'s')
        cond[0] = True
        self.df = self.df[cond]
        if filter_zeros==True:
            cond = self.df['ts']!=0
            self.df = self.df[cond]
        return self.df
    
    """Filtro per eliminare i dati di tipo -999"""
    def filter_999(self):
        df = self.df.copy()
        df[df.values==-999] = 0
        self.df = df
        return self.df
    
    """Filtro per eliminare i dati ripetuti in maniera esattamente identica
    dal sistema di acquisizione. Se il dato sucessivo è esattamente identico
    al precedente vado a filtrarlo"""
    def second_filter(self):
        self.df = self.df.fillna(value=0)
        delta = self.df.copy()
        delta_t1 = self.df.copy()
        last_val = delta[delta.index == delta.index[delta.size -1]]
        delta_t1 = delta_t1.drop(delta_t1.index[[0]])
        delta_t1 = delta_t1.append(last_val)
        #aggiungo al df delta il df delta_t1 con i valori shiftati
        delta['ts1'] = delta_t1['ts'].values
        cond = delta['ts'] != delta['ts1']
        self.df = self.df[cond]
        return self.df

    """voglio una function che mi standardizza il dataset"""
    def standardize_data(self, std):
        self.std = std
        if std==True:
            self.std_scaler = StandardScaler() #RobustScaler()
            values = self.df.values
            values = values.astype('float32')
            self.df['ts'] = self.std_scaler.fit_transform(values)

    """Filtro basato sul calcolo della mean-absolute-deviation, che io 
    faccio sia con aggregazione giornalera che oraria, per vedere se il 
    dato si allontana molto dalla mediana sia giornaliera che oraria"""
    def MAD_daily_filter(self, filtering, mad_val):
        if filtering==True:
            try:
                self.count = self.df.groupby(self.df.index.date).count()
                newdf = pd.DataFrame(np.repeat(self.davg['day average'],
                                               self.count['ts']))
                newdf.index = self.df.index
            except ValueError: 
                self.count = pd.DataFrame(index=self.davg.index, columns =['ts'])
                self.count['ts'] = self.df.groupby(self.df.index.date).count()
                self.count = self.count.fillna(value=0)
                newdf = pd.DataFrame(np.repeat(self.davg['day average'],
                                               self.count['ts']))
                newdf.index = self.df.index
            m_a_d = pd.concat([self.df, newdf] , axis=1)
            m_a_d['mad_mean'] = abs((m_a_d['ts'] - m_a_d['day average']))
            cond = m_a_d['mad_mean']<mad_val
            self.df = self.df[cond]
        return self.df
    
    """Filtro basato sul calcolo della mean-absolute-deviation con
    aggregazione oraria. devo ragionarci, perchè ho poche misure 
    per questo"""
    def MAD_hourly_filter(self):
        pass
    
    """Costruisce, a posteriori del filtraggio, il dataset. Vorrei renderlo
    flessibile, che si possa scegliere sia giorno che ora --> ex 15T"""
    def Temporal_aggregation(self, temporal_aggr, var_name=None):
        if temporal_aggr =='hourly':
            dataset = self.df_hourly
        elif temporal_aggr == 'daily':
            dataset = self.davg
        else:
            dataset = self.df['ts'].resample(temporal_aggr).mean() 
            dataset = pd.DataFrame(dataset)
            dataset.index = pd.to_datetime(dataset.index)
            if var_name==None:
                dataset = dataset.rename(columns = {'ts': 'h average'}) 
            else:
                dataset = dataset.rename(columns = {'ts': var_name}) 
            if self.exclusion==True:
                dataset = self.weekend_exclusion(self.exclusion, dataset)
            if self.exclusion_bis == True:
                dataset = self.year_exclusion(self.exclusion_bis,
                                              self.year_to_remove,
                                              dataset)
        if var_name!=None:
                dataset = dataset.rename(columns = {'h average': var_name}) 
        self.dataset = dataset
        return dataset
    
    """output deve essere il plot della PACF. Richiede in input il numero
    di lags da analizzare"""
    def Autocorrelation_analysis(self, nlags, figsize, save=None):
        fig, ax = plt.subplots(figsize=figsize)
        plot_pacf(self.dataset['h average'].fillna(method='ffill'),
                  lags=nlags, ax=ax)
        #plt.xlabel('lag')
        ax.set_xlabel('lag', fontsize=22)
        ax.set_title('')
        ax.grid(True)          
        if save==True:
            plt.savefig('immagini/pacf200.png', dpi=200, bbox_inches='tight')
            plt.savefig('immagini/pacf400.png', dpi=400, bbox_inches='tight')
        plt.show()
        plt.show()
        #Pacf = pacf(self.dataset['h average'].fillna(method='ffill'), nlags)
        #return Pacf
        
    """Funzione per riscalare i dati nel range 0 - 1. Flessibile. Devo poter
    scegliere di fare e o combinare scaling diversi. Care che lo scaler deve
    ritornarmi"""
    def Scaling(self, dataset, scaler_choice):
        try:
            values = dataset.values
            values = values.astype('float32')
        except AttributeError:
            values = dataset
            values = values.astype('float32')
        if scaler_choice == 'minmax':
            self.scaler =  MinMaxScaler(feature_range=(0, 1)) # StandardScaler() 
            self.scaler = self.scaler.fit(values)
        elif scaler_choice == 'standard':
            self.scaler =  StandardScaler() 
            self.scaler = self.scaler.fit(values)
        self.scaled = self.scaler.fit_transform(values)
        return self.scaled, self.scaler
        
    # """funzione per "sistemare" i dati in input per la lstm, in colonne
    # shiftate del time step. Il file data deve essere scalato"""
    # def series_to_supervised(self, data, n_in=1, n_out=1, dropnan=True):

    # 	n_vars = 1 if type(data) is list else data.shape[1]
    #     df = DataFrame(data)
    #     cols, names = list(), list()
    # 	# input sequence (t-n, ... t-1)
    # 	for i in range(n_in, 0, -1):
    # 		cols.append(df.shift(i))
    # 		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]

    # 	# forecast sequence (t, t+1, ... t+n)
    # 	for i in range(0, n_out):
    # 		cols.append(df.shift(-i))
    # 		if i == 0:
    # 			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
    # 		else:
    # 			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
    # 	# put it all together
    # 	self.reframed = concat(cols, axis=1)
    # 	self.reframed.columns = names
    # 	# drop rows with NaN values
    # 	if dropnan:
    # 		self.reframed.dropna(inplace=True)

    # 	return self.reframed
    
    """Funzione per rimuovere qualsiasi week-end dal dataset. Nel momento
    in cui exclusion viene settato su TRUE IL WEEK END VIENE RIMOSSO"""
    def weekend_exclusion(self, exclusion, dataset=None):
        self.exclusion = exclusion
        if isinstance(dataset, type(None)) == True and exclusion==True:
            self.df = self.df[self.df.index.dayofweek < 5]
            dataset = self.df
        elif isinstance(dataset, type(None)) == False and exclusion==True:
            dataset = dataset[dataset.index.dayofweek < 5]
        else:
            dataset = self.df
        return dataset
    
    """Funzione per rimuovere un determinato anno dal dataset. Nel momento
    in cui exclusion viene settato su TRUE IL WEEK END VIENE RIMOSSO"""
    def year_exclusion(self, exclusion_bis, year=None, dataset=None):
        self.exclusion_bis = exclusion_bis
        self.year_to_remove = year
        if isinstance(dataset, type(None)) == True and exclusion_bis==True:
            self.df = self.df[self.df.index.year != self.year_to_remove]
            dataset = self.df
        elif isinstance(dataset, type(None)) == False and exclusion_bis==True:
            dataset = dataset[dataset.index.year != self.year_to_remove]
        else:
            dataset = self.df
        return dataset
    
    

    
    
    
    
    
    
    
    
    
    
    
    
