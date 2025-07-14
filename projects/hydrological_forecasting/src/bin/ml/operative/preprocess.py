#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from argparse import ArgumentParser
from sys import path as syspath
from json import load
from os import remove

try:
    parser = ArgumentParser()
    parser.add_argument('--configuration_file', dest='configuration_file', type=str, required=True)
    parser.add_argument('--roi_config', dest='roi_config', type=str, required=True)
    parser.add_argument('--subbasin', dest='subbasin', type=str, required=True)
    parser.add_argument('--start_date', dest='start_date', type=str, required=False)
    parser.add_argument('--end_date', dest='end_date', type=str, required=False)
    args = parser.parse_args()
except:
    class local_args():

        def __init__(self) -> None:
            pass

        def add_conf_file(self,  conf_file):
            self.configuration_file = conf_file
        
        def add_subbasin(self,  subbasin):
            self.subbasin = subbasin

        def add_start_date(self,  start_date):
            self.start_date = start_date
        
        def add_end_date(self,  end_date):
            self.end_date = end_date
        
        def add_roi_config(self,  roi_config):
            self.roi_config = roi_config

    args = local_args()
    args.add_conf_file("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/ml/operative/vernago.json")
    args.add_subbasin("SB003")
    args.add_start_date("20211215")
    args.add_end_date("20211230")
    args.add_roi_config("/media/windows/projects/hydro_forecasting/vernago/training/output/metadata/20231214152330.json")

### load script libraries
with open(args.configuration_file) as config_file:
    configuration = load(config_file)
    lib_dirs = configuration["script_libs"]
    config_file.close()

for lib_dir in lib_dirs:
    syspath.insert( 0, lib_dir )   

from lib import *
from local_lib import *

def prepare_streamflow_data(
    cc_date, fct_start_time, output_timezone, fct_model_input_tz, 
    rls, hist_model_lag_hours,
    log_path, roi_config,
    input_path, input_datetime_format, input_timezone_str,
    output_path, output_datetime_format, output_timezone_str, logging=logging):

    try:
        ### cut on the lead_hours requested
        fct_current_start_datetime = cc_date + dt.timedelta(
            hours=int(fct_start_time.split(':')[0]), 
            minutes=int(fct_start_time.split(':')[1]),
            seconds=int(fct_start_time.split(':')[2])
        )
    except:
        fct_current_start_datetime = cc_date + dt.timedelta(hours=int(rls))
        logging.debug("Full forecasting hours used!")

    fct_current_start_datetime = output_timezone.localize(
        fct_current_start_datetime).astimezone(fct_model_input_tz)

    flow_configuration = {
        "project_name": "hydrological_forecasting",
        "provider_name": "meteoaltoadige",
        "model": {
            "name": "ground_stations",
            "ensemble": 1,
            "lead_hours": -1,
            "releases": None
        },
        "input": {
            "path": None,
            "datetime_format": None,
            "timezone": None
        },
        "output": {
            "path": None,
            "datetime_format": None,
            "timezone": None
        },
        "start_date": None,
        "start_time": None,
        "end_date": None,
        "end_time": None,
        "update_dates": False,
        "delete_uncomplete": False,

        "log_path": None,

        "roi_config": None,
        "stations_to_extract": None,
        "variables_to_extract": [
            "streamflow"
        ],
        "logging_level": "info",
        "script_authors": [
            "ftt01 (dallatorre.daniele@gmail.com)"
        ],
        "script_version": "v0.5.0",
        "email": False
    }

        # flow_configuration = json.load(s_conf_file)

    flow_configuration["model"]['releases'] = [int(rls)]

    flow_configuration["input"]["path"] = input_path
    flow_configuration["input"]["datetime_format"] = input_datetime_format
    flow_configuration["input"]["timezone"] = input_timezone_str
    
    flow_configuration["output"]["path"] = output_path
    flow_configuration["output"]["datetime_format"] = output_datetime_format
    flow_configuration["output"]["timezone"] = output_timezone_str

    flow_configuration["start_date"] = (cc_date - dt.timedelta( hours=hist_model_lag_hours )).strftime("%Y%m%d")
    flow_configuration["start_time"] = cc_date.strftime("%H:%M")
    flow_configuration["end_date"] = cc_date.strftime("%Y%m%d")

    if fct_start_time == None:
        flow_configuration["end_time"] = (cc_date + dt.timedelta( hours=int(rls) )).strftime("%H:%M")
    else:
        flow_configuration["end_time"] = fct_start_time.split(':')[0] + ":" + fct_start_time.split(':')[1]

    flow_configuration["log_path"] = log_path

    flow_configuration["roi_config"] = roi_config

    tmp_streamflow_conf = output_path + "streamflow.json"
    with open(tmp_streamflow_conf, 'w') as json_file:
        json.dump(flow_configuration, json_file, indent=2)
        json_file.close()

    cmd = "cd /home/daniele/documents/github/ftt01/phd/data/meteo/providers/meteoaltoadige/src/bin/ && python3 extraction_data.py {streamflow_conf_file} {output_name}.csv"
    cmd = cmd.format(
        streamflow_conf_file=tmp_streamflow_conf,
        output_name=flow_configuration["end_date"])
    # print(cmd)
    process = subprocess.Popen( cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    remove(tmp_streamflow_conf)


# In[ ]:


with open(args.configuration_file) as config_file:
    configuration = json.load(config_file)

    project_name = configuration["project_name"]

    hist_model_provider_name = configuration["historical_data"]["provider_name"]
    hist_model_lag_hours = configuration["historical_data"]["lag_hours"]
    hist_model_input_path = configuration["historical_data"]["input_path"]
    hist_model_input_dt_format = configuration["historical_data"]["datetime_format"]
    hist_model_input_tz_str = configuration["historical_data"]["timezone"]
    hist_model_input_tz = pytz.timezone(hist_model_input_tz_str)

    fct_model_provider_name = configuration["forecasting_data"]["provider_name"]
    fct_model_model_name = configuration["forecasting_data"]["model_name"]
    fct_model_ensemble = configuration["forecasting_data"]["ensemble"]
    fct_model_releases = configuration["forecasting_data"]["releases"]
    fct_model_input_path = configuration["forecasting_data"]["path"]
    fct_model_input_dt_format = configuration["forecasting_data"]["datetime_format"]
    fct_model_input_tz_str = configuration["forecasting_data"]["timezone"]
    fct_model_input_tz = pytz.timezone(fct_model_input_tz_str)

    ml_input_path = configuration["ml_model"]["input"]["path"]
    mkNestedDir(ml_input_path)
    ml_input_datetime_format = configuration["ml_model"]["input"]["datetime_format"]
    ml_input_timezone_str = configuration["ml_model"]["input"]["timezone"]
    ml_input_timezone = pytz.timezone(ml_input_timezone_str)
    
    fct_start_time = configuration["ml_model"]["output"]["fct_start_time"]
    fct_lead_hours = configuration["ml_model"]["output"]["fct_lead_hours"]
    fct_output_type = configuration["ml_model"]["output"]["type"]

    roi_config_file = args.roi_config
    with open(roi_config_file) as roi_config_f:
        roi_configuration = json.load(roi_config_f)

        roi_key = roi_configuration["main"]["key"]
        roi_name = roi_configuration["main"]["name"]
        
        basins = roi_configuration["basins"]

    roi_config_f.close()

    if args.start_date != None:
        start_date = args.start_date
    else:
        start_date = configuration["start_date"]
    try:
        start_datetime = dt.datetime.strptime( start_date, "%Y%m%d" )
    except:
        start_datetime = dt.datetime.today()
        start_date = dt.datetime.strftime( start_datetime, format="%Y%m%d" )
    
    if args.end_date != None:
        end_date = args.end_date
    else:
        end_date = configuration["end_date"]
    try:
        end_datetime = dt.datetime.strptime( end_date, "%Y%m%d" )
    except:
        end_datetime = dt.datetime.today()
        end_date = dt.datetime.strftime( end_datetime, format="%Y%m%d" )
        
    update_start_date = configuration["update_start_date"]
    
    log_path = configuration["log_path"]
    mkNestedDir(log_path)

    email_notification = configuration["email"]
    script_version = configuration["script_version"]
    
    if configuration["logging_level"] == "info":
        logging_level = logging.INFO
    elif configuration["logging_level"] == "debug":
        logging_level = logging.DEBUG
    else:
        logging_level = logging.ERROR

config_file.close()


# In[ ]:

log_filename = str(log_path) + "module_ml_run_" +  dt.datetime.now().strftime("%Y%m%d") + ".log"
logging.basicConfig(
    filename = log_filename,
    format = '%(asctime)s - %(message)s',
    filemode = 'a',
    level = logging_level)


# In[ ]:

logging.info( "Project name: " + project_name )
logging.info( "Provider historical data from " + hist_model_provider_name +     ": " + hist_model_input_path )
logging.info( "Provider forecasting data from " + fct_model_provider_name+     ": " + fct_model_input_path )

logging.info( "Output path: " + ml_input_path )
logging.info( "Log filename path: " + str(log_path) )

logging.info( "### PREPROCESS ###" )


# In[ ]:

computation_start = dt.datetime.now()


# In[ ]:


start_datetime = dt.datetime.strptime( start_date + "T00:00:00" , "%Y%m%dT%H:%M:%S" )
end_datetime = dt.datetime.strptime( end_date + "T23:59:59" , "%Y%m%dT%H:%M:%S" )

dates = pd.date_range( start=start_datetime, end=end_datetime, freq='d' )


# In[ ]:


for subbasin in basins:

    logging.info("Current subbasin key: " + str(subbasin['key']))
    if (str(subbasin['key']) != str(args.subbasin)):
        logging.info("Skipping unrequested subbasin: " + str(subbasin['key']) )
        continue

    subbasin_df = pd.json_normalize(subbasin['ground_stations'])
    logging.debug("Subbasins ground stations list: " + str(subbasin_df))

    for rls in fct_model_releases:

        c_rls = "R" + str(rls).zfill(3)
        logging.debug("Current release: " + str(c_rls))

        variables_dirs = glob.glob( fct_model_input_path + roi_key + "/" + subbasin["key"] + "/R" + str(rls).zfill(3) + "/*/" )
        logging.debug("Variables list: " + str(variables_dirs))

        for var in variables_dirs:

            c_var = var.split('/')[-2]
            logging.info("Current variable: " + str(c_var))

            if (c_var != 'precipitation') and (c_var != 'temperature') and (c_var != 'streamflow'):
                continue

            # if c_var == 'streamflow':
            #     type_dirs = [var]
            #     skip_type = True
            # else:
            type_dirs = glob.glob( var + "*/")
            # skip_type = False

            used_fct_model_type = []
            for ty in type_dirs:
                logging.debug("Types: " + str(ty))

                # if skip_type == False:
                    # for point in point_dirs:
                fct_model_type = ty.split('/')[-2]

                # if fct_model_type != fct_output_type:
                #     continue

                if fct_model_type == "mean":
                    c_fct_model_ensemble = 1
                elif fct_model_type == "ensemble":
                    c_fct_model_ensemble = int(fct_model_ensemble)
                else:
                    logging.error("Not a valid type: " + fct_model_type)
                    continue
                # else:
                #     c_fct_model_ensemble = 1
                #     fct_model_type == "mean"

                ### read all the dates extracted in the forecasting directory
                all_dates = glob.glob( ty + "*.csv" )

                used_dates = []
                for c_date_path in all_dates:
                    c_date_str = c_date_path.split('/')[-1][:-4]
                    c_date = dt.datetime.strptime( c_date_str, '%Y%m%d' )

                    if not(c_date in dates):
                        continue

                    logging.debug("Processing date: " + c_date_str)
                    # fct_file = point + "{c_date}.csv".format( c_date=c_date_str )
                    fct_file = c_date_path
                    
                    # try:
                    c_fct_df = pd.read_csv( fct_file, header=None, skiprows=1, index_col=0 )
                    c_fct_df.index.name = "datetime"
                    c_fct_df.columns = [str(i).zfill(3) for i in range(1,c_fct_model_ensemble+1)]
                    c_fct_df.reset_index(inplace=True)
                    # except Exception as e:
                    #     logging.warning( "File not found: " + e )
                    #     continue

                    c_fct_df.loc[:,'datetime'] = pd.to_datetime( 
                        c_fct_df['datetime'], format=fct_model_input_dt_format )
                    c_fct_df.loc[:,'datetime'] = c_fct_df['datetime'].apply(
                        lambda i: fct_model_input_tz.localize(i) )
                    c_fct_df.set_index('datetime', inplace=True)

                    try:
                        ### cut on the lead_hours requested
                        fct_current_start_datetime = c_date + dt.timedelta(
                            hours=int(fct_start_time.split(':')[0]), 
                            minutes=int(fct_start_time.split(':')[1]),
                            seconds=int(fct_start_time.split(':')[2])
                        )
                    except:
                        fct_current_start_datetime = c_date + dt.timedelta(hours=int(rls))
                        logging.debug("Full forecasting hours used!")

                    fct_current_start_datetime = ml_input_timezone.localize(
                        fct_current_start_datetime).astimezone(fct_model_input_tz)
                    fct_current_end_datetime = fct_current_start_datetime + dt.timedelta( hours=int( fct_lead_hours ) )

                    c_fct_df = c_fct_df[fct_current_start_datetime:fct_current_end_datetime]
                    c_fct_df.index = [ c.astimezone(ml_input_timezone) for c in c_fct_df.index ]

                    ### historical    
                    # hist_file = hist_model_input_path + roi_key + \
                    #     '/' + subbasin['key'] + '/' + c_rls + '/' + c_var + '/' + \
                    #         subbasin_df[ subbasin_df["variable"] == c_var ]["station_id"].values[0] + '.csv'
                    hist_file = hist_model_input_path + c_var + '/' + subbasin_df[ subbasin_df["variable"] == c_var ]["station_id"].values[0] + '.csv'

                    try:
                        c_hist_df = pd.read_csv( hist_file )
                    except:
                        logging.warning( "File not found: " + hist_file )
                        continue   
                    
                    c_hist_df.loc[:,'datetime'] = pd.to_datetime( 
                        c_hist_df['datetime'], format=hist_model_input_dt_format )
                    try:
                        c_hist_df.loc[:,'datetime'] = c_hist_df['datetime'].apply(
                            lambda i: i.astimezone(hist_model_input_tz))
                    except:
                        c_hist_df.loc[:,'datetime'] = c_hist_df['datetime'].apply(
                            lambda i: hist_model_input_tz.localize(i))
                    
                    c_hist_df.set_index('datetime', inplace=True)

                    if c_var == "precipitation":
                        c_hist_df = c_hist_df.resample('h').agg(pd.Series.sum, min_count=1)
                    elif c_var == "temperature":
                        c_hist_df = c_hist_df.resample('h').agg(pd.Series.mean)
                    elif c_var == "streamflow":
                        c_hist_df = c_hist_df.resample('h').agg(pd.Series.mean)
                    else:
                        logging.error("Not implemented variable: " + c_var)
                        continue
                    
                    utc_end_date = c_fct_df.index[0].astimezone( pytz.utc ) - dt.timedelta( hours=1 )
                    utc_start_date = utc_end_date - dt.timedelta( hours=int(hist_model_lag_hours) )

                    c_index = pd.date_range( start=utc_start_date, end=utc_end_date, freq='1H' )
                    c_index = [ c.astimezone(ml_input_timezone) for c in c_index ]

                    full_hist_df = pd.DataFrame(index=c_index)
                    
                    h_current_end_datetime = utc_end_date.astimezone( hist_model_input_tz )
                    h_current_start_datetime = utc_start_date.astimezone( hist_model_input_tz )
                    
                    c_hist_df = c_hist_df[h_current_start_datetime:h_current_end_datetime]
                    c_hist_df.index = [ c.astimezone(ml_input_timezone) for c in c_hist_df.index ]

                    for ens in [str(i).zfill(3) for i in range(1,c_fct_model_ensemble+1)]:

                        full_hist_df = pd.merge(
                            full_hist_df, 
                            c_hist_df.rename(columns={'values':ens}), 
                            how='left', left_index=True, right_index=True)

                        # a = pd.concat([tmp_hist_df, c_hist_df], ignore_index=True)
                        # full_hist_df.loc[:,ens] = pd.merge(
                        #     tmp_hist_df , c_hist_df, how='left', on='index').rename(columns={'index':'datetime'}).set_index('datetime')
                        # del tmp_hist_df
                        
                        # try:
                        #     # full_hist_df.loc[:,ens] = round( c_hist_df['values'], 2 ).to_list()
                        #     full_hist_df.loc[:,ens] = pd.concat( [full_hist_df[[ens]], c_hist_df] )
                        # except ValueError as ve:
                        #     logging.error( "Error: " + str(ve) )
                        # except:
                        #     logging.error( "Not a valid historical date range: " + \
                        #         h_current_start_datetime.strftime(output_datetime_format) + " - " +\
                        #             h_current_end_datetime.strftime(output_datetime_format) )
                        #     continue

                    ### merge
                    merged_data = pd.concat( [full_hist_df, c_fct_df] )   
                                       
                    if fct_model_type == "mean":
                        merged_data = pd.DataFrame( merged_data.mean(axis=1), columns=['values'] )
                    
                    merged_data.index = [ m.strftime( ml_input_datetime_format ) for m in merged_data.index ]
                    merged_data.index.name = "datetime"

                    c_input_path = ml_input_path + roi_key + "/" + subbasin['key'] + "/R" + str(rls).zfill(3) +                         "/" + c_var + "/" + fct_model_type + "/"
                        # "/" + c_var + "/" + fct_model_type + "/" + point.split('/')[-2] + "/"
                    mkNestedDir(c_input_path)
                    
                    output_filename = c_input_path + c_date_str + ".csv"
                    merged_data.to_csv( output_filename, sep="," )

                    used_dates.append(c_date)


# In[ ]:


for rls in fct_model_releases:
    for cc_date in used_dates:
        prepare_streamflow_data(
            cc_date, fct_start_time, ml_input_timezone, fct_model_input_tz, 
            rls, hist_model_lag_hours,
            log_path, roi_config_file,
            hist_model_input_path, hist_model_input_dt_format, hist_model_input_tz_str,
            ml_input_path, ml_input_datetime_format, ml_input_timezone_str, logging=logging)


# In[ ]:


if update_start_date == True:
    new_start_date = (dt.datetime( 
        end_datetime.year,end_datetime.month,end_datetime.day )).strftime(format="%Y%m%d")

    logging.info("Set up the last date: " + str(new_start_date))

    configuration['start_date'] = new_start_date

    with open(args.configuration_file, 'w') as config_file:
        json.dump(configuration, config_file, indent=2)
        config_file.close()


# In[ ]:
logging.info( "### PREPROCESS ENDED ###" )


# In[ ]:
# if email_notification == True:
#     send_email(
#         subject="ML data ready",
#         body="Started at " + computation_start.strftime(format="%Y-%m-%dT%H:%M:%SZ%z") + 
#             "\nFinish at " + dt.datetime.now().strftime(format="%Y-%m-%dT%H:%M:%SZ%z") +
#             "\nJSON config: " + json.dumps( configuration, indent=4 )
#     )