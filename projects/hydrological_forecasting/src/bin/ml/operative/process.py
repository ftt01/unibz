#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser
from sys import path as syspath
from json import load
from numpy import arange
from random import choices

import matplotlib.pyplot as plt

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib/"
syspath.insert( 0, lib_dir )

from lib import instantiatePlot, mkNestedDir, getPathFromFilepath

def generate_colors(N):
    colors = {}
    for i in range(1, N+1):
        color = '#' + ''.join(choices('0123456789ABCDEF', k=6))
        colors[f"M{i}"] = color
    return colors

def plot_super_ens(df, patterns=[
    'M1','M2','M3','M4','M5','M6','M7','M8','M9','M10','M11','M12','M13','M14','M15','M16','M17','M18','M19','M20'],
    output_file="./superens_forecast.tiff"):

    colors = generate_colors(len(patterns))

    fig, axs = instantiatePlot("Time $[days]$", "Q $[m^3/s]$", output_format='tiff', width=400, height=250)

    for p in patterns:
        sel_cols = df.filter(regex=p+'_')
        median = sel_cols.median(axis=1)
        percentiles = sel_cols.quantile([0.25, 0.75],axis=1).T

        axs.plot(median, label=p, linestyle="solid", color=colors[p])
        axs.plot(percentiles, linestyle="--", color=colors[p])
        
    axs.legend(ncol=5)
    axs.xaxis.set_tick_params(labelrotation=90)
  
    fig.savefig( output_file, format='tiff', bbox_inches='tight', facecolor='w', dpi=300 )

def createBoxPlot(df, x_label, y_label, output_file, label=None,
                  x_major_locator=None, x_major_formatter=None,
                  output_format="png", xscale="linear", yscale="linear",
                  width=190, height=90, scale_factor=1,
                  tick_size=10, label_size=10, legend_fontsize=8,
                  ratio_width=190, ratio=3740/500, my_dpi=500):
    
    df_reset = df.reset_index()
    df_reset.drop(columns=['datetime'], inplace=True)

    plot_x_inches = ratio / ratio_width * width
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(
        1,
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
    
    sns.boxplot(data=df_reset.T, ax=axs, dodge=False, **PROPS)

    axs.tick_params(labelsize=tick_size/scale_factor)

    axs.set_xscale(xscale)
    axs.set_yscale(yscale)

    axs.set_ylabel(y_label, fontsize=label_size/scale_factor)
    axs.set_xlabel(x_label, fontsize=label_size/scale_factor)

    axs.set_xticklabels(df.index)
    axs.xaxis.set_tick_params(labelrotation=90)

    axs.set(ylim=(df.min().min() - 0.1, df.max().max() + 0.1))
    axs.set_xticks(range(len(df.index)), labels=df.index)

    if label != None:
        axs.text(0, 0, label, transform=fig.dpi_scale_trans,
                 fontsize=label_size/scale_factor, va='bottom', ha='left')

    if x_major_locator != None:
        axs.xaxis.set_major_locator(x_major_locator)

    if x_major_formatter != None:
        axs.xaxis.set_major_formatter(x_major_formatter)

    axs.axhline(linewidth=0.5, linestyle="--", color="k")

    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig(output_file, format=output_format,
                bbox_inches='tight', facecolor='w', dpi=my_dpi)


    # plt.show()
    # plt.close(fig=fig)

try:
    parser = ArgumentParser()
    parser.add_argument('repo_path', type=str)
    parser.add_argument('configuration_file', type=str)
    parser.add_argument('--roi_config', dest='roi_config', type=str, required=True)
    parser.add_argument('--subbasin', dest='subbasin', type=str, required=True)
    parser.add_argument('--start_date', dest='start_date', type=str, required=False)
    parser.add_argument('--end_date', dest='end_date', type=str, required=False)
    args = parser.parse_args()
except:
    class local_args():

        def __init__(self) -> None:
            pass

        def add_repo_path(self,  repo_path):
            self.repo_path = repo_path

        def add_conf_file(self,  conf_file):
            self.configuration_file = conf_file
        
        def add_roi_config(self,  roi_config):
            self.roi_config = roi_config
        
        def add_subbasin(self,  subbasin):
            self.subbasin = subbasin

        def add_start_date(self,  start_date):
            self.start_date = start_date
        
        def add_end_date(self,  end_date):
            self.end_date = end_date

    args = local_args()
    args.add_repo_path("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/")
    args.add_conf_file("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/ml/operative/vernago.json")
    args.add_roi_config("/media/windows/projects/hydro_forecasting/vernago/training/output/metadata/20231214152330.json")
    args.add_subbasin("SB003")
    args.add_start_date("20211215")
    args.add_end_date("20211230")

repo_path = args.repo_path
conf_file = args.configuration_file
req_subbasin = args.subbasin

### load script libraries
with open(conf_file) as config_file:
    configuration = load(config_file)
    lib_dirs = configuration["script_libs"]
    config_file.close()

for lib_dir in lib_dirs:
    syspath.insert( 0, lib_dir )   

from main_flow_forecast import main
from local_lib import *

################################################################################

with open(conf_file) as config_file:
    configuration = json.load(config_file)

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

    dates = pd.date_range( start=start_datetime, end=end_datetime, freq='d' )

    update_start_date = configuration["update_start_date"]

    input_data_path = configuration["ml_model"]["input"]["path"]
    output_path = configuration["ml_model"]["output"]["path"]
    output_type = configuration["ml_model"]["output"]["type"]

    fct_model_releases = configuration["forecasting_data"]["releases"]
    roi_config_file = args.roi_config
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

log_filename = str(log_path) + "module_ml_run_" +  dt.datetime.now().strftime("%Y%m%d") + ".log"
logging.basicConfig(
    filename = log_filename,
    format = '%(asctime)s - %(message)s',
    filemode = 'a',
    level = logging_level)

logging.info( "### Machine Learning PROCESS ###" )
logging.info( "Output type: " + output_type )

start_datetime = dt.datetime.strptime( start_date + "T00:00:00" , "%Y%m%dT%H:%M:%S" )
end_datetime = dt.datetime.strptime( end_date + "T23:59:59" , "%Y%m%dT%H:%M:%S" )

dates = pd.date_range( start=start_datetime, end=end_datetime, freq='d' )

### run over each date
for c_date in dates:

    ### run on each basin/subbasin
    logging.debug( "Current basins: " + str(basins) )
    for subbasin in basins:

        c_sb = str(subbasin['key'])
        logging.debug( "Current subbasin: " + c_sb )

        for rls in fct_model_releases:

            c_rls = "R" + str(rls).zfill(3)
            logging.debug( "Current release: " + c_rls )

            model_path = None
            for trained_releases in subbasin["trained"]:
                if trained_releases['release'] == c_rls:
                    models_path = trained_releases['models']
                else:
                    continue
                
                c_rel_output_path = output_path + roi_key + "/" + c_sb + "/" + c_rls + "/"
                full_df = pd.DataFrame()
                for models_trained in models_path:
                    c_id = f"M{str(models_trained['key']).zfill(3)}"
                    c_output_path = c_rel_output_path + c_id + "/" + output_type + "/"
                    mkNestedDir(c_output_path)

                    try:
                        main(
                            start_date = c_date.strftime("%Y%m%d"), 
                            model_path = models_trained["path"],
                            input_data_path = input_data_path + roi_key + "/" + c_sb + "/" + c_rls + "/",
                            output_path = c_output_path,
                            type_of_simulation = output_type
                        )
                    except Exception as ex:
                        logging.error("ML crashed: " + str(ex))
                        continue

                    if output_type == 'ensemble':
                        ## read the CSV in output to concatenate in a single df
                        c_df = pd.read_csv(
                            c_output_path + dt.datetime.strftime(c_date,'%Y%m%d') + "/ens_forecast.csv", index_col=0,
                            skiprows=1, header=None, names=['datetime']+[f"{str(c_id).zfill(3)}.{str(i)}" for i in arange(1,21,1)])
                    elif output_type == 'mean':
                        c_df = pd.read_csv(
                            c_output_path + dt.datetime.strftime(c_date,'%Y%m%d') + "/forecast.csv", index_col=0,
                            skiprows=1, header=None, names=['datetime']+[f"{str(c_id).zfill(3)}"])
                    else:
                        continue
                    full_df = pd.concat([full_df,c_df],axis=1)
                
                if full_df.shape[1] > 0:
                    ## save complete df to main directory
                    if output_type == 'ensemble':
                        suffix = "super"
                    elif output_type == 'mean':
                        suffix = ""
                    
                    output_path_summary = c_rel_output_path + "00_summary/" + dt.datetime.strftime(c_date,'%Y%m%d') + "/"
                    mkNestedDir(output_path_summary)
                    full_df.to_csv( output_path_summary + f"{suffix}ens_forecast.csv")
                    plot_super_ens(full_df,output_file=output_path_summary + f"{suffix}ens_forecast.tiff")
                    createBoxPlot(
                        full_df,"Time $[days]$", "Q $[m^3/s]$", 
                        output_path_summary + f"{suffix}ens_forecast_boxplot.tiff", height=200)

logging.info( "### Machine Learning PROCESS ENDED ###" )

if update_start_date == True:
    new_start_date = ( start_datetime + dt.timedelta(days=1) ).strftime(format="%Y%m%d")

    logging.info("Set up the last date: " + str(new_start_date))

    configuration['start_date'] = new_start_date

    with open(conf_file, 'w') as config_file:
        json.dump(configuration, config_file, indent=2)
        config_file.close()
    
    del configuration