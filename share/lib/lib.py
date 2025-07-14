import logging
import argparse
import os
import subprocess

from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

import numpy as np
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import datetime as dt
from dateutil import parser as dt_parser
# from dateutil import tz
import pytz

import psycopg2

import time

import glob
import json

import shutil

import dask.dataframe as dd

def get_logging(basepath, logging_level):
    datetime = dt.datetime.now()
    log_filename = f"{basepath}logs/{datetime:%Y%m%dT%H%M%S}.log"

    head, tail = os.path.split(log_filename)
    mkNestedDir(head)

    logging.basicConfig(
        filename = log_filename,
        format = "%(asctime)s\t%(levelname)s\t%(module)s.%(funcName)s\t%(threadName)s\t%(message)s",
        filemode = "a",
        level = logging_level
    )

    logging.getLogger("matplotlib.font_manager").disabled = True
    return logging, datetime

def send_email(
    subject, body, receiver_email=["daniele.dallatorre@natec.unibz.it"],
    html=None, attachments=None, 
    cc_receiver_email=None, 
    sender_email = "pirlachilegge@yahoo.it", password = "scemochiscrive"):

    import mimetypes
    import smtplib
    import ssl

    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.mime.audio import MIMEAudio

    msg_alternative = MIMEMultipart('alternative')
    
    if body != None:
        part1 = MIMEText(body, "plain")
        msg_alternative.attach(part1)

    if html != None:
        part2 = MIMEText(html, "html")
        msg_alternative.attach(part2)

    msg_mixed = MIMEMultipart('related')
    msg_mixed.attach(msg_alternative)

    if attachments != None:

        for attachment in attachments:
            ctype, encoding = mimetypes.guess_type(attachment[0])
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"

            maintype, subtype = ctype.split("/", 1)

            if maintype == "text":
                fp = open(attachment[0])
                # Note: we should handle calculating the charset
                att = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == "image":
                fp = open(attachment[0], "rb")
                att = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == "audio":
                fp = open(attachment[0], "rb")
                att = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(attachment[0], "rb")
                att= MIMEBase(maintype, subtype)
                att.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(att)
            att.add_header("Content-Disposition", "attachment", filename=attachment[1])
            msg_mixed.attach(att)

    msg_mixed['From'] = sender_email
    msg_mixed['To'] = ', '.join(receiver_email)
    msg_mixed['Subject'] = subject
    if cc_receiver_email != None:
        msg_mixed["Cc"] = ', '.join(cc_receiver_email)

    smtp_server = "out.virgilio.it"

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    server = None
    try:
        server = smtplib.SMTP_SSL(smtp_server, 465, context=context, timeout=30)
        server.login(sender_email, password)
        # server.sendmail(sender_email,receiver_email,msg_mixed.as_string())
        server.send_message(msg_mixed)
    finally:
        if server != None:
            server.quit()

def is_connected(conn):
    try:
        status = conn.noop()[0]
    except:  # smtplib.SMTPServerDisconnected
        status = -1
    return True if status == 250 else False

def get_postgres_connection():

    db_name = 'meteo'
    db_user = 'postgres'
    db_password = 'postgres'
    db_host = '172.20.0.2'

    return psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host)

def query_meteo( query, mode, logging=None ):

    try:
        conn = get_postgres_connection()
        ccur = conn.cursor()
    except:
        if logging != None:
            logging.error("Connection error.")
        return None

    try:
        if mode == 'insert':
            ccur.execute( query )
            conn.commit()
            conn.close()
            return 0
        elif mode == 'select':
            ccur.execute("SELECT * FROM meteo.dwd_icond2eps_points")
            rows = ccur.fetchall()
            conn.close()
            return rows
        else:
            if logging != None:
                logging.error("Not a valid mode ['select','insert']")
            conn.close()
            return None
    except psycopg2.InterfaceError as ie:
        conn.close()
        query_postgis( query, mode, logging )
    except psycopg2.errors.UniqueViolation as uv:
        if logging != None:
            logging.error("Unique violation: " + str(uv))
    except psycopg2.errors.InFailedSqlTransaction:
        conn.close()
        query_postgis( query, mode, logging )

def query_postgis( query, mode, logging=None ):

    try:
        conn = psycopg2.connect(
        host="IP.3",
        database="gis",
        user="docker",
        password="docker")

        ccur = conn.cursor()
    except:
        if logging != None:
            logging.error("Connection error.")
        return None

    try:
        if mode == 'insert':
            ccur.execute( query )
            conn.commit()
            conn.close()
            return 0
        elif mode == 'select':
            ccur.execute("SELECT * FROM meteo.dwd_icond2eps_points")
            rows = ccur.fetchall()
            conn.close()
            return rows
        else:
            if logging != None:
                logging.error("Not a valid mode ['select','insert']")
            conn.close()
            return None
    except psycopg2.InterfaceError as ie:
        conn.close()
        query_postgis( query, mode, logging )
    except psycopg2.errors.UniqueViolation as uv:
        if logging != None:
            logging.error("Unique violation: " + str(uv))
    except psycopg2.errors.InFailedSqlTransaction:
        conn.close()
        query_postgis( query, mode, logging )

def mkNestedDir(dirTree):
    # from pathlib import Path
    # Path(dirTree).mkdir(parents=True, exist_ok=True)
    os.makedirs(dirTree, exist_ok=True)

def parent_directory( f ):
    from pathlib import Path
    c_path = Path( f )
    return str( c_path.parent.absolute() ) + '/'

def extract_filename( f ):
    return str( os.path.basename(f) )

def copy_content(src, dst):

    from shutil import rmtree, copytree, copy

    try:
        #if path already exists, remove it before copying with copytree()
        if os.path.exists(dst):
            rmtree(dst)
        copytree(src, dst)

    except:
        # If the error was caused because the source wasn't a directory
        # if e.errno == errno.ENOTDIR:
        #     copy(source_dir_prompt, destination_dir_prompt)
        # else:
        raise

def getPathFromFilepath(existGDBPath):
    return os.path.dirname(os.path.abspath(existGDBPath))

def get_df_name(df):
    name = [x for x in globals() if globals()[x] is df][0]
    return name

def get_offset( timezone_str ):
    z_str = dt.datetime.now(pytz.timezone(timezone_str)).strftime('%z')
    hours = int(z_str[1:3])
    mins = int(z_str[4:5])

    offset = {}
    offset['hours'] = int(hours)
    offset['minutes'] = int(mins)
    
    if z_str[0] == '-':
        offset['hours'] = offset['hours']*-1
    
    return offset

###### SETUP PLOTS ###################################################################################

# plt.style.use('C:\\Users\\daniele\\Documents\\GitHub\\ftt01\\phd\\ITstuff\\python\\matplotlib\\template.mplstyle')
plt.style.use(
    "/home/host/GitHub/ftt01/phd/ITstuff/python/matplotlib/template.mplstyle")

#my_dpi = 600
output_format = 'tiff'

#width = 90
#height = 60

# tick_size=10
# label_size=10
# legend_fontsize=8
# ratio_width=190
# ratio=3740/500

######################################################################################################
# GIS TOOLS
######################################################################################################

def bbox_extraction( bbox_lat_min, bbox_lat_max, bbox_lon_min, bbox_lon_max, spatial_resolution, lon_factor=0 ):

    lat_min = round( spatial_resolution/2 + bbox_lat_min - bbox_lat_min % spatial_resolution, 2 )
    lat_max = round( spatial_resolution/2 + bbox_lat_max - bbox_lat_max % spatial_resolution + spatial_resolution, 2 )
    lon_min = round( bbox_lon_min - bbox_lon_min % spatial_resolution, 2 ) + lon_factor
    lon_max = round( bbox_lon_max - bbox_lon_max % spatial_resolution + spatial_resolution, 2 ) + lon_factor

    return lat_min, lat_max, lon_min, lon_max

# import shapely.geometry
# import pyproj

# # Set up transformers, EPSG:3857 is metric, same as EPSG:900913
# to_proxy_transformer = pyproj.Transformer.from_crs(crs_from='epsg:4326', crs_to='epsg:32632', always_xy=True)
# to_original_transformer = pyproj.Transformer.from_crs('epsg:32632', 'epsg:4326')

# # Create corners of rectangle to be transformed to a grid
# sw = shapely.geometry.Point((lon_min, lat_min))
# ne = shapely.geometry.Point((lon_max, lat_max))

# stepsize = 9000 # km grid step size

# # Project corners to target projection
# transformed_sw = to_proxy_transformer.transform(sw.x, sw.y) # Transform NW point to 32632
# transformed_ne = to_proxy_transformer.transform(ne.x, ne.y) # .. same for SE

# # Iterate over 2D area
# gridpoints = []
# x = transformed_sw[0]
# while x < transformed_ne[0]:
#     y = transformed_sw[1]
#     while y < transformed_ne[1]:
#         # p = shapely.geometry.Point(to_original_transformer.transform(x, y))
#         p = shapely.geometry.Point(x, y)
#         gridpoints.append(p)
#         y += stepsize
#     x += stepsize

# with open(output_path+'testout.csv', 'w+') as of:
#     of.write('lon;lat\n')
#     for p in gridpoints:
#         of.write('{:f};{:f}\n'.format(p.x, p.y))

######################################################################################################
# METEO TOOLS
######################################################################################################


def fill_metadata(metadata_template_path, _provider_name_, _provider_id_, _provider_notes_,
                  _station_id_, _station_name_, _x_, _y_, _z_,
                  _sensor_id_, _variable_, _units_, _format_, _quality_style_: dict, _datetime_format_, _datapath_,
                  path_to_save_metadata):

    if os.path.exists(path_to_save_metadata):
        # logging.debug( "Metadata file: " + path_to_save_metadata )
        # logging.debug( "Metadata: " + metadata )
        try:
            with open(path_to_save_metadata) as f:
                metadata = json.load(f)
                f.close()
            data_exist = True
        except:
            os.remove(path_to_save_metadata)
            data_exist = False
    
    else:
        data_exist = False

    if data_exist == True:
        
        sensors = metadata['sensors']

        new_sensors = []
        for item in sensors:
            if not(_sensor_id_ in item['id']):
                new_sensors.append(item)

        sensor = {}
        sensor["id"] = _sensor_id_
        sensor["status"] = None
        sensor["variable"] = _variable_
        sensor["units"] = _units_
        sensor["format"] = _format_
        sensor["quality"] = _quality_style_
        sensor["datetime_format"] = _datetime_format_
        sensor["datapath"] = _datapath_
        sensor['start_date'] = None
        sensor['end_date'] = None
        sensor['step_mins'] = None

        new_sensors.append(sensor)
        metadata['sensors'] = new_sensors
    else:
        with open(metadata_template_path) as f:
            metadata = json.load(f)
            f.close()

        metadata['provider']['name'] = _provider_name_
        metadata['provider']['id'] = _provider_id_
        metadata['provider']['notes'] = _provider_notes_

        metadata['id'] = _station_id_
        metadata['name'] = _station_name_
        metadata['location']['x'] = _x_
        metadata['location']['y'] = _y_
        metadata['location']['z'] = _z_

        sensors = []
        sensor = {}
        sensor["id"] = _sensor_id_
        sensor["status"] = None
        sensor["variable"] = _variable_
        sensor["units"] = _units_
        sensor["format"] = _format_
        sensor["quality"] = _quality_style_
        sensor["datetime_format"] = _datetime_format_
        sensor["datapath"] = _datapath_
        sensor['start_date'] = None
        sensor['end_date'] = None
        sensor['step_mins'] = None

        sensors.append(sensor)

        metadata['sensors'] = sensors

        # print(metadata)
        # print('HERE')

    if path_to_save_metadata != None:

        mkNestedDir( getPathFromFilepath(path_to_save_metadata) )

        with open(path_to_save_metadata, 'w') as fp:
            json.dump(metadata, fp, indent=4)
            fp.close()

######################################################################################################
# HYDROLOGICAL TOOLS
######################################################################################################

def evaluateNash(data_obs, data_sim, round_el=2):
    from numpy import nanmean, nansum
    num_nse = nansum((data_obs - data_sim)**2)
    den_nse = nansum((data_obs - nanmean(data_obs))**2)
    nse = 1 - num_nse/den_nse
    return round(nse, round_el)

def evaluateNNSE(nse, round_el=2):
    return round(1/(2-nse), round_el)

def evaluateECDF(data_to_use):
    data = np.sort(data_to_use)

    # calculate the proportional values of samples
    norm_cdf = 100. * np.arange(len(data)) / (len(data) - 1)

    data = pd.DataFrame(data, columns=["data"])
    cdf = pd.DataFrame(norm_cdf, columns=["cdf"])

    ecdf_frame = pd.concat([data, cdf], axis=1)
    ecdf_frame.set_index('data', inplace=True)

    return ecdf_frame


def flowDuration(data_to_use):
    data_to_use = data_to_use.dropna()
    data = np.sort(data_to_use)[::-1]

    norm_fd = []
    counter = 1
    # apply the rank
    for i in data:
        norm_fd.append(100 * counter / (len(data) + 1))
        counter = counter + 1

    norm_fd = np.array(norm_fd)
    data = pd.DataFrame(data, columns=["data"])
    fd = pd.DataFrame(norm_fd, columns=["fd"])

    fd_frame = pd.concat([fd, data], axis=1)
    fd_frame.set_index('fd', inplace=True)

    return fd_frame

######################################################################################################
# DATA COLLECTION
######################################################################################################

class DataCollector():

    def __init__(self, configPath=None, config='config.json', sim_config='sim_config.json',
                 model_config='model_config.json', obs_config='observed_config.json'):

        with open(configPath + config) as config_file:
            self.config = json.load(config_file)

        with open(configPath + sim_config) as sim_config_file:
            self.sim_config = json.load(sim_config_file)

        with open(configPath + model_config) as model_config_file:
            self.model_config = json.load(model_config_file)

        with open(configPath + obs_config) as obs_config_file:
            self.obs_config = json.load(obs_config_file)

        self.model_flow = None
        self.model_precipitation = None
        self.model_temperature = None
        self.model_snow_we = None
        self.model_snow_we_plan = None
        self.model_sca_passirio = None
        self.model_swe_snowgauge = []

    def retrieve(self, filepath, start_date, end_date, config, current_node=None):

        noID = False

        if "nodes" in config.keys():
            for node in config["nodes"]:
                if node["name"] == current_node:
                    if "id" in node.keys():
                        id_node = node["id"]
                    else:
                        noID = True
                    output_filename = node["output_file"]

            fileFullPath = filepath + output_filename
            readed = self.readCSV(fileFullPath, config)
            if noID == True:
                return readed[start_date:end_date]
            else:
                return readed[start_date:end_date][id_node]
        else:

            output_filename = config["output_file"]
            fileFullPath = filepath + output_filename

            readed = self.readCSV(fileFullPath, config)

            if "id" in config.keys():
                return readed[start_date:end_date][config["id"]]
            else:
                return readed[start_date:end_date]

    def readCSV(self, fileName, fileConfig):
        ''' Using the config file the fileName is read by the pandas.read_csv package. '''

        header = 0
        index_col = None
        parse_dates = False
        skiprows = 0
        sep = ","
        names = None

        if "header" in fileConfig.keys():
            if fileConfig["header"] != None:
                if fileConfig["header"] == "None":
                    header = None
                else:
                    header = int(fileConfig["header"])

        if "index_col" in fileConfig.keys():
            if fileConfig["index_col"] != None:
                index_col = int(fileConfig["index_col"])

        if "parse_dates" in fileConfig.keys():
            if fileConfig["parse_dates"] != None and fileConfig["parse_dates"] == "True":
                parse_dates = True

        if "skiprows" in fileConfig.keys():
            if fileConfig["skiprows"] != None:
                skiprows = int(fileConfig["skiprows"])

        if "sep" in fileConfig.keys():
            if fileConfig["sep"] != None:
                sep = fileConfig["sep"]

        if "names" in fileConfig.keys():
            if fileConfig["names"] != None:
                from ast import literal_eval
                names = literal_eval(fileConfig["names"])

        from pandas import read_csv
        return read_csv(fileName, header=header, index_col=index_col,
                        parse_dates=parse_dates, skiprows=skiprows, sep=sep, names=names)

    def retrieveData(self, current_phase, current_basin, current_type, current_node):

        for basin in self.sim_config:
            if basin["basin"] == current_basin:
                for sim in basin["simulations"]:
                    if sim["phase"] == current_phase:
                        for sim_type in sim["type"]:

                            from datetime import datetime
                            start_date = datetime.strptime(
                                sim["start_date"], '%Y-%m-%dT%H:%M:%S')
                            end_date = datetime.strptime(
                                sim["end_date"], '%Y-%m-%dT%H:%M:%S')

                            if sim_type["name"] == current_type:

                                model_output_filepath = basin["sim_path"] + \
                                    basin["output_path"] + \
                                    sim_type["output_specific_path"]

                                # simulated flow
                                self.model_flow = self.retrieve(model_output_filepath, start_date, end_date,
                                                                self.model_config["discharge"], current_node=current_node)

                                # simulated precipitation
                                self.model_precipitation = self.retrieve(model_output_filepath, start_date, end_date,
                                                                         self.model_config["precipitation"])

                                # simulated temperature
                                self.model_temperature = self.retrieve(model_output_filepath, start_date, end_date,
                                                                       self.model_config["temperature"])

                                # simulated swe
                                self.model_snow_we = self.retrieve(model_output_filepath, start_date, end_date,
                                                                   self.model_config["snow_we"])

                                # simulated snow_we_plan
                                self.model_snow_we_plan = self.retrieve(model_output_filepath, start_date, end_date,
                                                                        self.model_config["snow_we_plan"])

                                # simulated sca passirio
                                self.model_sca_passirio = self.retrieve(model_output_filepath, start_date, end_date,
                                                                        self.model_config["sca_passirio"])

                                # simulated swe snow gauge
                                self.model_swe_snowgauge.append(self.retrieve(model_output_filepath, start_date, end_date,
                                                                              self.model_config["swe_niv1"]))

                                self.model_swe_snowgauge.append(self.retrieve(model_output_filepath, start_date, end_date,
                                                                              self.model_config["swe_niv2"]))

                                self.model_swe_snowgauge.append(self.retrieve(model_output_filepath, start_date, end_date,
                                                                              self.model_config["swe_niv3"]))

                                self.model_swe_snowgauge.append(self.retrieve(model_output_filepath, start_date, end_date,
                                                                              self.model_config["swe_niv4"]))

                                self.model_swe_snowgauge.append(self.retrieve(model_output_filepath, start_date, end_date,
                                                                              self.model_config["swe_niv5"]))

        # observed flow
        obs_flow_filepath = self.obs_config["discharge"]["output_path"]
        obs_flow_conf = self.obs_config["discharge"]
        self.obs_flow = self.retrieve(
            obs_flow_filepath, start_date, end_date, obs_flow_conf, current_node=current_node)
        self.obs_flow[self.obs_flow == -999] = None

        # observed temperature
        obs_temperature_filepath = self.obs_config["temperature"]["output_path"]
        obs_temperature_conf = self.obs_config["temperature"]
        self.obs_temperature = self.retrieve(
            obs_temperature_filepath, start_date, end_date, obs_temperature_conf, current_node=current_node)


######################################################################################################
# PLOT TOOLS
######################################################################################################


def createBoxPlot(df_in, x_label, y_label, output_file, label=None,
                  x_major_locator=None, x_major_formatter=None,
                  output_format="png", xscale="linear", yscale="linear",
                  width=190, height=90, period="MS", scale_factor=1,
                  tick_size=10, label_size=10, legend_fontsize=8,
                  ratio_width=190, ratio=3740/500, my_dpi=500):

    if period == "MS":
        import matplotlib.ticker as ticker
        x_major_locator = ticker.MultipleLocator(1)
        x_labels = range(1, 12+1)
        x_major_formatter = ticker.FuncFormatter(lambda x, _: dict(
            zip(range(len(x_labels)), x_labels)).get(x, ""))
    elif period == "H":
        import matplotlib.ticker as ticker
        x_major_locator = ticker.MultipleLocator(2)
        x_labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                    13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        x_major_formatter = ticker.FuncFormatter(lambda x, _: dict(
            zip(range(len(x_labels)), x_labels)).get(x, ""))

    plot_x_inches = ratio / ratio_width * width
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
                            figsize=[plot_x_inches, plot_y_inches],
                            tight_layout={'pad': 0},
                            dpi=my_dpi
                            )

    # add data and data_label to legend
    import seaborn as sns
    PROPS = {
        'boxprops': {'facecolor': 'none', 'edgecolor': 'black', 'linewidth': '1'},
        'medianprops': {'color': 'black', 'linewidth': '1.5'},
        'whiskerprops': {'color': 'black', 'linewidth': '0.75'},
        'capprops': {'color': 'black', 'linewidth': '0.75'}
    }
    # sns.set_style({'style':"whitegrid", 'axes.grid': True})

    if period == "MS":
        sns.boxplot(x=df_in.index.month, y=df_in.values,
                    ax=axs, **PROPS)
        # sns.stripplot(x=df_in.index.month, y=df_in.values, marker='o', alpha=0.5, color='#e66101')
    elif period == "D":
        sns.boxplot(x=df_in.index.daily, y=df_in.values,
                    ax=axs, **PROPS)
        # sns.stripplot(x=df_in.index.month, y=df_in.values, marker='o', alpha=0.5, color='#e66101')
    elif period == "H":
        sns.boxplot(x=df_in.index.hour, y=df_in.values,
                    ax=axs, **PROPS)
        # sns.stripplot(x=df_in.index.month, y=df_in.values, marker='o', alpha=0.5, color='#e66101')

    axs.tick_params(labelsize=tick_size/scale_factor)

    axs.set_xscale(xscale)
    axs.set_yscale(yscale)

    axs.set_ylabel(y_label, fontsize=label_size/scale_factor)
    axs.set_xlabel(x_label, fontsize=label_size/scale_factor)

    if label != None:
        axs.text(0.15, 0.15, label, transform=fig.dpi_scale_trans,
                 fontsize=label_size/scale_factor, va='bottom', ha='left')

    if x_major_locator != None:
        axs.xaxis.set_major_locator(x_major_locator)

    if x_major_formatter != None:
        axs.xaxis.set_major_formatter(x_major_formatter)

    axs.axhline(linewidth=0.5, linestyle="--", color="k")

    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig(output_file, format=output_format,
                bbox_inches='tight', facecolor='w', dpi=my_dpi)

    plt.close(fig=fig)


def instantiatePlot(x_label, y_label,
                    output_format='png', plot_legend=True, 
                    xscale="linear", yscale="linear",
                    width=190, height=90, scale_factor=1,
                    tick_size=10, label_size=10, legend_fontsize=8,
                    ratio_width=190, ratio=3740/500, my_dpi=600):

    plot_x_inches = ratio / ratio_width * width
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
                            figsize=[plot_x_inches, plot_y_inches],
                            tight_layout={'pad': 0},
                            dpi=my_dpi
                            )

    axs.tick_params(labelsize=tick_size/scale_factor)

    axs.set_xscale(xscale)
    axs.set_yscale(yscale)

    axs.set_ylabel(y_label, fontsize=label_size/scale_factor)
    axs.set_xlabel(x_label, fontsize=label_size/scale_factor)

    if plot_legend == True:
        axs.legend(fontsize=legend_fontsize/scale_factor, bbox_to_anchor=None)

    return fig, axs


def createPlot(plots, x_label, y_label, output_file, xticks=None, yticks=None, label=None,
               x_lim_min=None, x_lim_max=None, y_lim_min=None, y_lim_max=None,
               x_major_locator=None, x_major_formatter=None,
               y_major_locator=None, y_major_formatter=None,
               output_format='png', plot_legend=True, xscale="linear", yscale="linear",
               x_rot=None, y_rot=None, no_xaxis=False, no_yaxis=False, 
               width=190, height=90, scale_factor=1,
               tick_size=10, label_size=10, legend_fontsize=8, bbox_to_anchor=None, loc=None,
               ratio_width=190, ratio=3740/500, my_dpi=600):

    plot_x_inches = ratio / ratio_width * width
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
                            figsize=[plot_x_inches, plot_y_inches],
                            tight_layout={'pad': 0},
                            dpi=my_dpi
                            )

    axs.tick_params(labelsize=tick_size/scale_factor)

    axs.set_xscale(xscale)
    axs.set_yscale(yscale)

    if no_xaxis == False:
        axs.set_xlabel(x_label, fontsize=label_size/scale_factor)
    if no_yaxis == False:
        axs.set_ylabel(y_label, fontsize=label_size/scale_factor)

    if label != None:
        axs.text(0.15, 0.15, label, transform=fig.dpi_scale_trans,
                 fontsize=label_size/scale_factor, va='bottom', ha='left')

    if x_lim_min != None:
        axs.set_xlim([x_lim_min, x_lim_max])
    if y_lim_min != None:
        axs.set_ylim([y_lim_min, y_lim_max])

    if x_major_locator != None:
        axs.xaxis.set_major_locator(x_major_locator)

    if x_major_formatter != None:
        axs.xaxis.set_major_formatter(x_major_formatter)

    if y_major_locator != None:
        axs.yaxis.set_major_locator(y_major_locator)

    if y_major_formatter != None:
        axs.yaxis.set_major_formatter(y_major_formatter)

    if x_rot != None:
        axs.xaxis.set_tick_params(labelrotation=x_rot)

    if y_rot != None:
        axs.yaxis.set_tick_params(labelrotation=y_rot)

    if no_xaxis == False:
        if xticks != None:
            axs.set_xticks(xticks)
    else:
        axs.set_xticks([])
    
    if no_yaxis == False:
        if yticks != None:
            axs.set_yticks(yticks)
    else:
        axs.set_yticks([])

    # add data and data_label to legend
    for tp in plots:

        label = None
        linestyle = "solid"
        color = None
        marker = None

        if "label" in tp[1].keys():
            label = tp[1]["label"]

        if "linestyle" in tp[1].keys():
            linestyle = tp[1]["linestyle"]

        if "color" in tp[1].keys():
            color = tp[1]["color"]

        if "marker" in tp[1].keys():
            color = tp[1]["marker"]
        
        if "linewidth" in tp[1].keys():
            linewidth = float(tp[1]["linewidth"])*1.2
        else:
            linewidth = 1.2

        axs.plot(tp[0], label=label, linestyle=linestyle,
                 color=color, marker=marker, linewidth=linewidth/scale_factor)

    if (plot_legend == True) and ("label" in tp[1].keys()):
        axs.legend(fontsize=legend_fontsize/scale_factor,
                bbox_to_anchor=bbox_to_anchor, loc=loc)

    axs.axhline(linewidth=0.5, linestyle="--", color="k")

    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig(output_file, format=output_format,
                bbox_inches='tight', facecolor='w', dpi=my_dpi)
    plt.close(fig=fig)

    del [fig,axs]

# def createPlotWithInset(x_label, y_label, output_format='png', xscale="linear", yscale="linear",
#                     width=190, height=90, scale_factor=1,
#                     tick_size=10, label_size=10, legend_fontsize=8,
#                     inset_width='30%', inset_height='30%',
#                     ratio_width=190, ratio=3740/500, my_dpi=600):

#     from mpl_toolkits.axes_grid1.inset_locator import inset_axes

#     plot_x_inches = ratio / ratio_width * width
#     plot_y_inches = ratio / ratio_width * height

#     fig, (axs, axs2) = plt.subplots(1, 2,
#                             figsize=[plot_x_inches, plot_y_inches],
#                             tight_layout={'pad': 0},
#                             dpi=my_dpi
#                             )

#     axs.tick_params(labelsize=tick_size/scale_factor)

#     axs.set_xscale(xscale)
#     axs.set_yscale(yscale)

#     axs.set_ylabel(y_label, fontsize=label_size/scale_factor)
#     axs.set_xlabel(x_label, fontsize=label_size/scale_factor)
#     axs.legend(fontsize=legend_fontsize/scale_factor)

#     # Create inset of width 1.3 inches and height 0.9 inches
#     # at the default upper right location
#     axins = inset_axes(axs, width=inset_width, height=inset_height)
#     axins.tick_params(labelleft=False, labelbottom=False)

#     # # Create inset of width 30% and height 40% of the parent axes' bounding box
#     # # at the lower left corner (loc=3)
#     # axins2 = inset_axes(axs, width="30%", height="40%", loc=3)

#     # # Create inset of mixed specifications in the second subplot;
#     # # width is 30% of parent axes' bounding box and
#     # # height is 1 inch at the upper left corner (loc=2)
#     # axins3 = inset_axes(ax2, width="30%", height=1., loc=2)

#     # # Create an inset in the lower right corner (loc=4) with borderpad=1, i.e.
#     # # 10 points padding (as 10pt is the default fontsize) to the parent axes
#     # axins4 = inset_axes(ax2, width="20%", height="20%", loc=4, borderpad=1)

#     # Turn ticklabels of insets off
#     # for axi in [axins, axins2, axins3, axins4]:
#     #     axi.tick_params(labelleft=False, labelbottom=False)

#     plt.show()


# def read_timeseries_dd(standard_df, input_dt_format, datetime_col='datetime',
#                     output_dt_format=None, from_timezone=None, to_timezone='no'):

#     datetime_idx = dd.to_datetime(standard_df[datetime_col], format=input_dt_format)

#     if from_timezone != None:
#         if to_timezone == 'no':
#             datetime_idx = [idx.replace(tzinfo=ZoneInfo(from_timezone)).replace(
#                 tzinfo=None) for idx in datetime_idx]
#         else:
#             datetime_idx = [idx.replace(tzinfo=ZoneInfo(from_timezone)).astimezone(
#                 tz=ZoneInfo(to_timezone)) for idx in datetime_idx]
#     else:
#         if to_timezone == 'no':
#             datetime_idx = [idx.replace(tzinfo=None) for idx in datetime_idx]
#         else:
#             datetime_idx = [idx.astimezone(tz=ZoneInfo(
#                 to_timezone)) for idx in datetime_idx]

#     if output_dt_format != None:
#         datetime_idx = [dt.datetime.strftime(
#             idx, format=output_dt_format) for idx in datetime_idx]

#     # standard_df[datetime_col] = datetime_idx

#     # return standard_df
#     return datetime_idx

### read dataframe from CSV with a specific format of datetime as column

def append_data(current_data, additional_data):

    current_data = current_data.reset_index()
    additional_data = additional_data.reset_index()

    current_data = pd.concat([current_data[current_data['datetime'].isin(
        additional_data['datetime']) == False], additional_data], ignore_index=True)

    # print(data)
    current_data.dropna(subset=['datetime'], inplace=True)
    current_data.sort_values(by=['datetime'], inplace=True)

    current_data = current_data.set_index('datetime')
    current_data = current_data[current_data.index.notnull()]

    return current_data

###########################################
### DATA ANALYSIS TOOLS
###########################################

def resample_timeseries( df, res_type='mean', step='1H', offset=True ):

    df_copy = df.copy()
    if res_type == 'sum':
        df_copy = df_copy.resample(step).sum(min_count=1)
    elif res_type == 'mean':
        df_copy = df_copy.resample(step).mean()
    else:
        return None

    if offset == True:
        from pandas.tseries.frequencies import to_offset
        df_copy.index = df_copy.index + to_offset('1H')

    return df_copy

def data_check( df, style=None, threshold=1.5, method='max_min' ):

    try:
        if style == 'temperature':

            max_percentile = df['values'].quantile(0.75)
            min_percentile = df['values'].quantile(0.25)
            iqr = max_percentile-min_percentile

            to_drop_indexes = (df['values'] < min_percentile - 1.5*iqr) | (df['values'] > max_percentile + 1.5*iqr)
            checked_data = df.copy()
            checked_data[to_drop_indexes] = np.nan
        
        elif style == 'precipitation':

            ### threshold: percentage of the maximum [e.g., 1.1]
            if method == 'max_min':
                fct = threshold * float( df['values'].max() )
                to_drop_indexes = (df['values'] > fct) & (df['values'] < 0.0)
            ### threshold: value of the percentile that must be considered [e.g., 1]
            elif method == 'percentile':
                prec_ecdf = evaluateECDF( df['values'] )
                trim_ecdf = prec_ecdf[(prec_ecdf['cdf'] >= threshold) & (prec_ecdf['cdf'] <= 100-threshold)]
                prec_thr_max = trim_ecdf.index.max()
                prec_thr_min = trim_ecdf.index.min()

                to_drop_indexes = (df['values'] < prec_thr_min) & (df['values'] > prec_thr_max)
            else:
                print("Not implemented method [max_min,percentile]: " + method)
            
            checked_data = df.copy()
            checked_data[to_drop_indexes] = np.nan

        elif style == 'streamflow':

            df.index = pd.to_datetime(df.index)

            monthly_data = df.resample('MS').mean()
            monthly_mean = monthly_data.apply( lambda g: g.groupby(g.index.month).mean() )['values'].to_list()
            monthly_std = monthly_data.apply( lambda g: g.groupby(g.index.month).std() )['values'].to_list()
            monthly_stats = pd.DataFrame( {'mean':monthly_mean, 'std':monthly_std}, index=range(1,13), columns=['mean','std'] )

            to_drop_indexes = []

            checked_data = df.copy()

            for idx in checked_data.index:
                ## drop the index with a mounth 
                if float(checked_data.loc[idx]) >= monthly_stats.iloc[idx.month-1]['mean'] + threshold*monthly_stats.iloc[idx.month-1]['std']:
                    to_drop_indexes.append(idx)
                if float(checked_data.loc[idx]) <= monthly_stats.iloc[idx.month-1]['mean'] - threshold*monthly_stats.iloc[idx.month-1]['std']:
                    to_drop_indexes.append(idx)
            
            for i in to_drop_indexes:
                checked_data.loc[i, 'values'] = np.nan
                        
        else:
            print("Not a valid style!! [valid: temperature,precipitation,streamflow]")
    
    except ValueError:
        print("Not a valid length. Check of data ABORTED!")
        checked_data = df.copy()
    
    return checked_data


def impute_data(file_in, file_out=None):

    cmd = "python3 /home/daniele/documents/github/ftt01/phd/data/meteo/tools/imputation/WD-IMPUTER/Main.py {file_in} {file_out}"

    if file_out == None:
        process = subprocess.Popen(cmd.format(file_in=file_in, file_out=file_in), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen(cmd.format(file_in=file_in, file_out=file_out), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr

###########################################
### STATITISTICAL TOOLS
###########################################

# import numpy
# import scipy.special

# def peirce_dev(N: int, n: int, m: int) -> float:
#     """Peirce's criterion
    
#     Returns the squared threshold error deviation for outlier identification
#     using Peirce's criterion based on Gould's methodology.
    
#     Arguments:
#         - int, total number of observations (N)
#         - int, number of outliers to be removed (n)
#         - int, number of model unknowns (m)
#     Returns:
#         float, squared error threshold (x2)
#     """
#     # Assign floats to input variables:
#     N = float(N)
#     n = float(n)
#     m = float(m)

#     # Check number of observations:
#     if N > 1:
#         # Calculate Q (Nth root of Gould's equation B):
#         Q = (n ** (n / N) * (N - n) ** ((N - n) / N)) / N
#         #
#         # Initialize R values (as floats)
#         r_new = 1.0
#         r_old = 0.0  # <- Necessary to prompt while loop
#         #
#         # Start iteration to converge on R:
#         while abs(r_new - r_old) > (N * 2.0e-16):
#             # Calculate Lamda
#             # (1/(N-n)th root of Gould's equation A'):
#             ldiv = r_new ** n
#             if ldiv == 0:
#                 ldiv = 1.0e-6
#             Lamda = ((Q ** N) / (ldiv)) ** (1.0 / (N - n))
#             # Calculate x-squared (Gould's equation C):
#             x2 = 1.0 + (N - m - n) / n * (1.0 - Lamda ** 2.0)
#             # If x2 goes negative, return 0:
#             if x2 < 0:
#                 x2 = 0.0
#                 r_old = r_new
#             else:
#                 # Use x-squared to update R (Gould's equation D):
#                 r_old = r_new
#                 r_new = numpy.exp((x2 - 1) / 2.0) * scipy.special.erfc(
#                     numpy.sqrt(x2) / numpy.sqrt(2.0)
#                 )
#     else:
#         x2 = 0.0
#     return x2