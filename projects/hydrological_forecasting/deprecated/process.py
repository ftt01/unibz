#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser
from sys import path as syspath
# import plotly.graph_objs as go
# from plotly.subplots import make_subplots

parser = ArgumentParser()
parser.add_argument('repo_path', type=str)
parser.add_argument('configuration_file', type=str)
parser.add_argument('season', type=str)
args = parser.parse_args()
repo_path = args.repo_path
conf_file = args.configuration_file
season = args.season
# repo_path = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/"
# conf_file = "/media/windows/projects/hydro_forecasting/machine_learning/input/training/B001/SB001/20230316T120732.json"

ml_dir = repo_path + "resources/ml/training/"
syspath.insert( 0, ml_dir )
from main_training_model import main_model

lib_dir = repo_path + "resources/"
syspath.insert( 0, lib_dir )
from local_lib import *

################################################################################
if season == 'None':
    simulation_name = dt.datetime.now().strftime("%Y%m%d%H%M%S")
else:
    simulation_name = dt.datetime.now().strftime("%Y%m%d%H%M%S") + '_' + season

with open(conf_file) as config_file:
    configuration = json.load(config_file)

    input_data_path = configuration["ml_model"]["input"]["path"]
    output_path = configuration["ml_model"]["output"]["path"]
    mkNestedDir(output_path)

    releases = configuration["forecasting_data"]["releases"]

    roi_config_file = configuration["roi_config"]
    with open(roi_config_file) as roi_config_f:
        roi_configuration = json.load(roi_config_f)

        roi_key = roi_configuration["main"]["key"]
        roi_name = roi_configuration["main"]["name"]
        
        basins = roi_configuration["basins"]

        roi_config_f.close()
    
    log_path = configuration["log_path"]
    mkNestedDir(log_path)

    if configuration["logging_level"] == "info":
        logging_level = logging.INFO
    elif configuration["logging_level"] == "debug":
        logging_level = logging.DEBUG
    else:
        logging_level = logging.ERROR

    config_file.close()

log_filename = str(log_path) + "module_ml_training_" + simulation_name + ".log"
logging.basicConfig(
    filename = log_filename,
    format = '%(asctime)s - %(message)s',
    filemode = 'a',
    level = logging_level)

logging.info( "### Machine Learning TRAINING ###" )

### run on each basin/subbasin
# logging.debug( "Current basins: " + str(basins) )
trained_subbasins = []
for subbasin in basins:

    c_sb = str(subbasin['key'])
    logging.info( "Current subbasin: " + c_sb )

    subbasin_releases = []
    for rel in releases:

        # if not(c_sb in ['SB001']):
        #     continue
        c_rel = 'R' + str(rel).zfill(3)
        logging.info( "Current release: " + c_rel )

        c_output_path = output_path + roi_key + "/" + c_sb + "/" + c_rel + "/" + simulation_name + "/"

        # try:
        main_model(
            basin_id = c_sb,
            streamflow_path = subbasin['training_data']['streamflow']['path'],
            precipitation_path = subbasin['training_data']['precipitation']['path'],
            temperature_path = subbasin['training_data']['temperature']['path'],
            start_date = subbasin['training_data']['streamflow']['start_date'],
            end_date =  subbasin['training_data']['streamflow']['end_date'],
            split_point = subbasin['training_parameters']['split_point'],
            output_path = c_output_path,
            n_output = subbasin['training_parameters']['n_output'],
            lag_list_Q = subbasin['training_parameters']['lag_list_Q'],
            lag_list_P = subbasin['training_parameters']['lag_list_P'],
            lag_list_T = subbasin['training_parameters']['lag_list_T'],
            batch = subbasin['training_parameters']['batch'],
            starting_hour = rel
        )

        # ########## plot
        # file_to_read = c_output_path + "results.csv"
        # rain_to_read = subbasin['training_data']['precipitation']['path']

        # df = pd.read_csv(file_to_read,index_col=0, parse_dates=True, delimiter=';')
        # df_rain = pd.read_csv(rain_to_read,index_col=0, parse_dates=True, delimiter=',')

        # df['date'] = pd.to_datetime(df.index)
        # df_rain['datetime'] = pd.to_datetime(df_rain.index)

        # layout = go.Layout(title=c_sb,
        #                 xaxis=dict(title='Date'),
        #                 yaxis=dict(title='Value'))

        # trace0 = go.Scatter(x=df['date'], y=df['h average'], name='metered')
        # trace1 = go.Scatter(x=df['date'], y=df['train_forecast'], name='training')
        # trace2 = go.Scatter(x=df['date'], y=df['test_forecast'], name='testing')
        # trace3 = go.Scatter(x=df_rain['datetime'], y=df_rain['values'], name='precipitation')

        # fig = make_subplots(rows=2, cols=1)

        # fig.add_trace(
        #     trace0,
        #     row=1, col=1
        # )
        # fig.add_trace(
        #     trace1,
        #     row=1, col=1
        # )
        # fig.add_trace(
        #     trace2,
        #     row=1, col=1
        # )

        # fig.add_trace(
        #     trace3,
        #     row=2, col=1
        # )

        # # Add range slider
        # fig.update_layout(
        #     xaxis=dict(
        #         rangeselector=dict(
        #             buttons=list([
        #                 dict(count=1,
        #                     label="1m",
        #                     step="month",
        #                     stepmode="backward"),
        #                 dict(count=6,
        #                     label="6m",
        #                     step="month",
        #                     stepmode="backward"),
        #                 dict(count=1,
        #                     step="year",
        #                     stepmode="backward"),
        #                 dict(step="all")
        #             ])
        #         ),
        #         rangeslider=dict(
        #             visible=False
        #         ),
        #         type="date"
        #     )
        # )
        # fig.write_html(c_output_path + "results.html")

        # except Exception as ex:
        #     logging.error("ML crashed: " + str(ex))
        #     continue

        subbasin_releases.append({
            "key" : c_rel,
            "path" : c_output_path
        })

    new_subbasin = subbasin
    new_subbasin["releases"] = subbasin_releases
    trained_subbasins.append(
        new_subbasin
    )

mkNestedDir(output_path + roi_key + '/trained/')
with open(output_path + roi_key + '/trained/' + simulation_name + ".json", 'w') as out_config_f:
    out_config = {}
    out_config["main"] = roi_configuration["main"]
    out_config["basins"] = trained_subbasins

    json.dump(out_config, out_config_f, indent=4)
    out_config_f.close()

logging.info( "### Machine Learning TRAINING ENDED ###" )