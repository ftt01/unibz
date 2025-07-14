from sys import path as syspath
# from os import remove
# import json
# import subprocess
# import logging

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
syspath.insert( 0, lib_dir )

from lib import send_email, mkNestedDir, parent_directory, createPlot
from lib import dt, pd, np, json, subprocess, logging, argparse, os

try:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--resource_path", type=str, required=True)
    parser.add_argument("-s","--season", type=str, required=False, default=None)
    parser.add_argument("-r","--roi", type=str)
    parser.add_argument('--gridsearch', action=argparse.BooleanOptionalAction)
    # parser.add_argument("-m","--model", type=str, required=False, default="MultiOutputSVR") ### to run the gridsearch with a specific model
    parser.add_argument("-n","--simulation_name", type=str)
    args = parser.parse_args()
except:
    class local_args():

        def __init__(self) -> None:
            pass

        def add_resource_path(self,  resource_path):
            self.resource_path = resource_path

        def add_season(self,  season):
            self.season = season
        
        def add_roi(self,  roi):
            self.roi = roi
        
        def add_gridsearch(self,  gridsearch):
            self.gridsearch = gridsearch

        def add_simulation_name(self,  simulation_name):
            self.simulation_name = simulation_name

    args = local_args()
    args.add_resource_path("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/resources/ml/training/")
    args.add_season(None)
    args.add_roi("/home/daniele/documents/github/ftt01/phd/metadata/basins/phd/B003.json")
    args.add_gridsearch(False)
    args.add_simulation_name("20231221105605")

syspath.insert( 0, args.resource_path )
from main_training_model import main_model

preprocess_conf = {
    "project_name": "hydrological_forecasting",
    "provider_name": "meteoaltoadige",
    "model": {
      "name": "ground_stations",
      "ensemble": 1,
      "lead_hours": -1,
      "releases": None
    },
    "input" : {
      "path": "/media/windows/projects/hydro_forecasting/vernago/data/meteo/",
      "datetime_format": "%Y-%m-%d %H:%M:%S",
      "timezone": "UTC"
    },
    "output" : {
      "path": "/media/windows/projects/hydro_forecasting/vernago/training/input/",
      "datetime_format": "%Y-%m-%d %H:%M:%S",
      "timezone": "UTC"
    },
    
    "log_path": "/media/windows/projects/hydro_forecasting/vernago/logs/training/",
    "start_date": "19850101",
    "start_time": None,
    "end_date": None,
    "end_time": None,
    "update_dates" : False,
    "delete_uncomplete" : False,

    "roi_config": None,
    "stations_to_extract" : None, 
    "variables_to_extract" : None, 
    
    "logging_level": "info",
    "script_version": "v0.4.0",
    "script_authors" : ["ftt01 (dallatorre.daniele@gmail.com)"],
    "email" : False
}

process_conf = {
    "project_name": "hydrological_forecasting",
    "historical_data": {
      "provider_name": "meteoaltoadige"
    },
    "forecasting_data": {
      "provider_name": "dwd",
      "model_name": "icon-d2-eps",
      "releases" : [6]
    },
    "ml_model": {
      "input": {
        "path": "/media/windows/projects/hydro_forecasting/vernago/training/input/",
        "datetime_format": "%Y-%m-%d %H:%M:%S",
        "timezone": "UTC"
      },
      "output": {
        "path": "/media/windows/projects/hydro_forecasting/vernago/training/output/",
        # "lead_hours": [18,24,30,36,42,48]
        "lead_hours": [48]
      }
    },
    "roi_config": None,
    "log_path": "/media/windows/projects/hydro_forecasting/vernago/logs/training/",
    "logging_level": "debug",
    "script_authors": [
      "ftt01 (dallatorre.daniele@gmail.com)"
    ],
    "script_version": "v0.1.0",
    "email": False
}

grid_search_meta = {
    "bests" : 10,
    "scorer" : "r2",
    "epochs" : 1000,
    "models" : [
        # {
        #     "name" : "MultiOutputSVR",
        #     "parameters" : {
            #     "estimator__kernel" : ["rbf","poly","sigmoid"],
            #     "estimator__epsilon" : np.arange(0.005,0.01,0.001),
            #     "estimator__C" : np.arange(0.1,12,0.1)
            # }
            #     "estimator__kernel" : ["rbf"],
            #     "estimator__epsilon" : [0.005,0.01],
            #     "estimator__C" : [0.1,1]
            # }
            
        # },
        {
            "name" : "Feed_forward",
            "parameters" : {
                'n_output' : [48],
                'n_node': [[10,10,10], [50,50,50], [120,200,120]],
                'act_function': ['relu', 'sigmoid']
            }
        }
    ]
}

## update configuration paths
# drop NaN and create the fake timeseries to train the model, starting from the first not null value and filling the gaps
def process_timeseries(filepath, c_season=None):

    logging.info(f"Process {filepath}..")
    
    if c_season == None:
        ## drop NaN
        try:
            df = pd.read_csv(filepath,index_col=0,parse_dates=True)
            df.dropna(inplace=True)
            ## read first date
            first_date = df.index[0]
            ## read last date
            last_date = df.index[-1]
            ## create timeseries and new_dataframe
            dates = pd.date_range(first_date, last_date, freq="1H")
            new_dataframe = pd.DataFrame(index=dates)
            new_dataframe.index.name = "datetime"
            new_dataframe.reset_index(inplace=True)
            ## join the date
            new_dataframe = pd.merge(df, new_dataframe, on="datetime", how="left")
            new_dataframe.set_index("datetime", inplace=True)
            ## fill gaps TODO
            ##########################################
            if "streamflow" in filepath:
                new_dataframe["values"] = [np.nan if d < 0 else d for d in new_dataframe["values"]]
            ##########################################
            ## save the new_dataframe
            new_path = parent_directory(filepath) + first_date.strftime(format="%Y%m%d") + last_date.strftime(format="%Y%m%d") + ".csv"
            # print(new_path)
            new_dataframe.to_csv( new_path )
            new_path_plot = parent_directory(filepath) + first_date.strftime(format="%Y%m%d") + last_date.strftime(format="%Y%m%d") + ".pdf"

            plots = []
            plt_conf = {}
            plt_conf["color"] = "#e66101"
            plots.append( (new_dataframe, plt_conf) )
            createPlot(plots,  "Time [hours]", "Streamflow $[m^3/day]$", new_path_plot, output_format="pdf", my_dpi=600)

            if filepath != new_path:
                os.remove(filepath)

            return first_date.strftime(format="%Y%m%d"), last_date.strftime(format="%Y%m%d"), new_path
        except:
            return None,None,None
    
    else:
        df = pd.read_csv(filepath,index_col=0,parse_dates=True)
        df.dropna(inplace=True)
        ## slice to seasons
        if c_season == "winter":
            df_sliced = df.loc[df.index.month.isin([11,12,1,2])]
        elif c_season == "spring":
            df_sliced = df.loc[df.index.month.isin([3,4,5,6])]
        elif c_season == "summer":
            df_sliced = df.loc[df.index.month.isin([7,8,9,10])]
        ## read last date
        last_date = df.index[-1]
        ## count hours
        hours_sliced = df_sliced.shape[0]
        ## create timeseries and new_dataframe
        fake_start_date = last_date-dt.timedelta(hours=hours_sliced-1)
        dates = pd.date_range(fake_start_date, last_date, freq="1H")
        new_dataframe = pd.DataFrame(index=dates)
        new_dataframe.index.name = "datetime"
        ## add values sliced
        new_dataframe["values"] = df_sliced["values"].values
        ## fill gaps TODO
        ## save the new_dataframe
        new_path = parent_directory(filepath) + fake_start_date.strftime(format="%Y%m%d") + last_date.strftime(format="%Y%m%d") + "_" + c_season + ".csv"
        # print(new_path)
        new_dataframe.to_csv( new_path )

        return fake_start_date.strftime(format="%Y%m%d"), last_date.strftime(format="%Y%m%d"), new_path

if args.season == None:
    basepath = preprocess_conf["output"]["path"]
else:
    basepath = preprocess_conf["output"]["path"] + args.season + "/"

basedate = dt.datetime.now().strftime("%Y%m%dT%H%M%S")

with open(args.roi) as roi_config_f:
    roi_configuration = json.load(roi_config_f)
    main_key = roi_configuration["main"]["key"]
    basins = roi_configuration["basins"]
    roi_config_f.close()

# if process_conf_file == None:

preprocess_conf_file = basepath + "tmp_conf_preprocess.json"

if (args.gridsearch == True) or (args.simulation_name is None):
    simulation_name = dt.datetime.now().strftime("%Y%m%d%H%M%S")
else:
    simulation_name = args.simulation_name

for subbasin in basins:
    
    c_sub = subbasin["key"]
    preprocess_conf = preprocess_conf.copy()
    preprocess_conf["output"]["path"] = basepath + main_key + "/" + c_sub + "/" + basedate + "/"
    mkNestedDir( preprocess_conf["output"]["path"] )
    new_end_date = ( dt.datetime.today() - dt.timedelta(days=1) ).strftime(format="%Y%m%d")
    preprocess_conf["end_date"] = new_end_date

    for station in subbasin["ground_stations"]:
        preprocess_conf["stations_to_extract"] = station["station_id"]
        preprocess_conf["variables_to_extract"] = station["variable"]

        with open(preprocess_conf_file, "w") as config_file:
            json.dump(preprocess_conf, config_file, indent=2)
            config_file.close()

        cmd = "cd /home/daniele/documents/github/ftt01/phd/data/meteo/providers/meteoaltoadige/src/bin/ && python3 extraction_data.py {preprocess_conf_file} dates"
        process = subprocess.Popen(cmd.format(preprocess_conf_file=preprocess_conf_file), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

    ## add the roi_config path (that will be created later) to the process configuration file
    c_process_conf_file = preprocess_conf["output"]["path"] + "process.json"
    process_conf["roi_config"] = preprocess_conf["output"]["path"] + "roi.json"
    with open(c_process_conf_file, "w") as config_file:
        json.dump(process_conf, config_file, indent=2)
        config_file.close()

    ##precipitation
    c_training_data = {}
    c_start_date, c_end_date, file_path = process_timeseries( preprocess_conf["output"]["path"] + "precipitation/" + preprocess_conf["start_date"] + preprocess_conf["end_date"] + ".csv", c_season=args.season )

    if file_path == None:
        print("Missing precipitation data for " + c_sub)
        continue 
    
    c_prec_data = {}
    c_prec_data["path"] = file_path
    c_prec_data["start_date"] = c_start_date
    c_prec_data["end_date"] = c_end_date
    c_training_data["precipitation"] = c_prec_data
    del [c_start_date, c_end_date, file_path]

    ##temperature
    c_start_date, c_end_date, file_path = process_timeseries( preprocess_conf["output"]["path"] + "temperature/" + preprocess_conf["start_date"] + preprocess_conf["end_date"] + ".csv", c_season=args.season )   

    if file_path == None:
        print("Missing temperature data for " + c_sub)
        continue   
    
    c_prec_data = {}
    c_prec_data["path"] = file_path
    c_prec_data["start_date"] = c_start_date
    c_prec_data["end_date"] = c_end_date
    c_training_data["temperature"] = c_prec_data

    del [c_start_date, c_end_date, file_path]

    ##streamflow
    c_start_date, c_end_date, file_path = process_timeseries( preprocess_conf["output"]["path"] + "streamflow/" + preprocess_conf["start_date"] + preprocess_conf["end_date"] + ".csv", c_season=args.season )   

    if file_path == None:
        print("Missing streamflow data for " + c_sub)
        continue    
    
    c_prec_data = {}
    c_prec_data["path"] = file_path
    c_prec_data["start_date"] = c_start_date
    c_prec_data["end_date"] = c_end_date
    c_training_data["streamflow"] = c_prec_data

    del [c_start_date, c_end_date, file_path]

    ## add training_data to the current subbasin
    subbasin["training_data"] = c_training_data

    ## save the basins with preprocessed updates
    with open(process_conf["roi_config"], "w") as config_file:
        roi_configuration["basins"] = [subbasin]
        json.dump(roi_configuration, config_file, indent=2)
        config_file.close()
    
    ### HERE starts the process to train - taking the inputs
    with open(c_process_conf_file) as config_file:
        configuration = json.load(config_file)
    config_file.close()

    if args.season == None:
        output_path = configuration["ml_model"]["output"]["path"]
    else:
        output_path = configuration["ml_model"]["output"]["path"] + args.season + "/"
    mkNestedDir(output_path)

    lead_times = configuration["ml_model"]["output"]["lead_hours"]
    releases = configuration["forecasting_data"]["releases"]
    
    log_path = configuration["log_path"]
    mkNestedDir(log_path)

    if configuration["logging_level"] == "info":
        logging_level = logging.INFO
    elif configuration["logging_level"] == "debug":
        logging_level = logging.DEBUG
    else:
        logging_level = logging.ERROR

    log_filename = str(log_path) + "module_ml_training_" + simulation_name + ".log"
    logging.basicConfig(
        filename = log_filename,
        format = "%(asctime)s - %(message)s",
        filemode = "a",
        level = logging_level)

    logging.info( "### Machine Learning TRAINING ###" )

    for lead_time in lead_times:

        c_lead_time = "H" + str(lead_time).zfill(3)
        logging.info( "Current lead time: " + c_lead_time )

        trained_releases = []
        for rel in releases:
            
            # if not(c_sub in ["SB001"]):
            #     continue
            c_rel = "R" + str(rel).zfill(3)
            logging.info( "Current release: " + c_rel )

            specific_output_path = output_path + main_key + "/" + c_sub + "/" + c_rel + "/" + simulation_name + "/" + c_lead_time + "/"
            mkNestedDir(specific_output_path)

            if args.gridsearch == True:
                
                gridsearch_json = []
                for model in grid_search_meta['models']:

                    bests = main_model(
                        c_sub,
                        subbasin["training_data"]["streamflow"]["path"],
                        subbasin["training_data"]["precipitation"]["path"],
                        subbasin["training_data"]["temperature"]["path"],
                        subbasin["training_data"]["streamflow"]["start_date"],
                        subbasin["training_data"]["streamflow"]["end_date"],
                        specific_output_path,
                        subbasin["training_parameters"]["n_output"],
                        subbasin["training_parameters"]["lag_list_Q"],
                        subbasin["training_parameters"]["lag_list_P"],
                        subbasin["training_parameters"]["lag_list_T"],
                        subbasin["training_parameters"]["batch"],
                        subbasin["training_parameters"]["split_point"],
                        rel,
                        model['name'],
                        grid_search=args.gridsearch,
                        grid_search_epochs=grid_search_meta['epochs'],
                        grid_search_scorer=grid_search_meta['scorer'],
                        model_params=model['parameters'],
                        n=grid_search_meta['bests']
                    )    
                    
                    logging.info(f"Top {grid_search_meta['bests']} Parameter Sets:")
                    
                    i=0
                    for param_set, score in bests:
                        i=i+1
                        logging.info(param_set, " - Score:", score)
                        gridsearch_json.append({
                            "id" : i,
                            "model" : model['name'],
                            "scorer" : grid_search_meta['scorer'],
                            "score" : score,
                            "parameters" : param_set
                        })

                c_json = specific_output_path+"conf.json"
                with open(c_json,"w") as json_file:
                    json.dump(gridsearch_json, json_file, indent=2)
            
            else:

                logging.info("#################### TRAINING ####################")

                try:
                    c_json = specific_output_path + 'conf.json'
                    with open(c_json) as json_file:
                        models_to_train = json.load(json_file)
                        json_file.close()
                except:
                    logging.info(f"Not a valid JSON config: {c_json}")
                    continue
                
                ################## RUN the TRAINING over all JSON model parameters
                trained_models = []
                for model_to_train in models_to_train:

                    c_id = "M"+str(model_to_train["id"]).zfill(3)
                    
                    c_output_path = specific_output_path + "/trained/" + c_id + "/"
                    mkNestedDir(c_output_path)
                
                    bests = main_model(
                        c_sub,
                        subbasin["training_data"]["streamflow"]["path"],
                        subbasin["training_data"]["precipitation"]["path"],
                        subbasin["training_data"]["temperature"]["path"],
                        subbasin["training_data"]["streamflow"]["start_date"],
                        subbasin["training_data"]["streamflow"]["end_date"],
                        c_output_path,
                        subbasin["training_parameters"]["n_output"],
                        subbasin["training_parameters"]["lag_list_Q"],
                        subbasin["training_parameters"]["lag_list_P"],
                        subbasin["training_parameters"]["lag_list_T"],
                        subbasin["training_parameters"]["batch"],
                        subbasin["training_parameters"]["split_point"],
                        rel,                                        ## starting hour
                        model_to_train["model"],                    ## model name from JSON
                        model_params=model_to_train["parameters"]   ## params to train
                    )

                    trained_models.append({
                        "key" : c_id,
                        "path" : c_output_path
                    })

                trained_releases.append({
                    "release" : c_rel,
                    "models" : trained_models
                })
        
        if args.gridsearch == False:
            subbasin["trained"] = trained_releases

if args.gridsearch == False:
    ### save the training metadata with the paths of trained models
    roi_configuration['basins'] = basins
    output_path_metadata = output_path + "metadata/"
    mkNestedDir(output_path_metadata)
    with open(output_path_metadata + simulation_name + ".json", "w") as config_file:
        json.dump(roi_configuration, config_file, indent=2)
        config_file.close()