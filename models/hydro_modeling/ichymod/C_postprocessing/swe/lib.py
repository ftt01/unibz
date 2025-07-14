import datetime as dt
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

###### BASE PATHS ####################################################################################

configPath = "C:\\Users\\daniele\\Documents\\GitHub\\ftt01\\phd\\hydro_modeling\\C_postprocessing\\swe\\"

with open(configPath + 'config.json') as config_file:
    config = json.load(config_file)

###### SETUP PLOTS ###################################################################################
 
plt.style.use('C:\\Users\\daniele\\Documents\\GitHub\\ftt01\\phd\\ITstuff\\python\\matplotlib\\template.mplstyle')

#my_dpi = 600
output_format = 'png'

#width = 90
#height = 60

#tick_size=10
#label_size=10
#legend_fontsize=8
#ratio_width=190
#ratio=3740/500

######################################################################################################

def mkNestedDir(dirTree):
    from pathlib import Path
    Path(dirTree).mkdir(parents=True, exist_ok=True)

def getPathFromFilepath(existGDBPath):
    import os
    return os.path.dirname(os.path.abspath(existGDBPath))

def evaluateNash(data_obs, data_sim, round_el=5):
    from numpy import nanmean, nansum
    num_nse = nansum((data_obs - data_sim)**2)
    den_nse = nansum((data_obs - nanmean(data_obs))**2)
    nse = 1 - num_nse/den_nse
    return round(nse, round_el)

def readCSV(fileName, fileConfig):

    header=0
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
    return read_csv(fileName, header=header, index_col=index_col, \
        parse_dates=parse_dates, skiprows=skiprows, sep=sep, names=names)

def retrieveData(filepath, start_date, end_date, config, current_node=None):

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
        readed = readCSV(fileFullPath, config)
        if noID == True:
            return readed[start_date:end_date]
        else:
            return readed[start_date:end_date][id_node]
    else:

        output_filename = config["output_file"]
        fileFullPath = filepath + output_filename

        readed = readCSV(fileFullPath, config)

        if "id" in config.keys():
            return readed[start_date:end_date][config["id"]]
        else:
            return readed[start_date:end_date]

def retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node):
    
    with open(configPath + 'sim_config.json') as sim_config_file:
        sim_config = json.load(sim_config_file)

    with open(configPath + 'model_config.json') as model_config_file:
        model_config = json.load(model_config_file)

    with open(configPath + 'observed_config.json') as obs_config_file:
        obs_config = json.load(obs_config_file)

    from datetime import datetime

    for basin in sim_config:
        if basin["basin"] == current_basin:
            for sim in basin["simulations"]:
                if sim["phase"] == current_phase:
                    for sim_type in sim["type"]:

                        start_date = datetime.strptime(sim["start_date"], '%Y-%m-%dT%H:%M:%S')
                        end_date = datetime.strptime(sim["end_date"], '%Y-%m-%dT%H:%M:%S')

                        if sim_type["name"] == current_type:

                            model_output_filepath = basin["sim_path"] + \
                                basin["output_path"] + \
                                    sim_type["output_specific_path"]

                            # simulated flow
                            model_flow_conf = model_config["discharge"]
                            model_flow = retrieveData( model_output_filepath, start_date, end_date, model_flow_conf, current_node=current_node )
#                            model_flow_daily_mean=model_flow.resample('D').mean()
#                            model_flow_monthly_mean=model_flow.resample('MS').mean()

                            # simulated precipitation
                            model_precipitation_conf = model_config["precipitation"]
                            model_precipitation = retrieveData( model_output_filepath, start_date, end_date, model_precipitation_conf )
                            # model_precipitation = model_precipitation.iloc[:, 0]
#                            model_precipitation_daily_sum=model_precipitation.resample('D').sum()
#                            model_precipitation_daily_mean=model_precipitation.resample('D').mean()
#                            model_precipitation_monthly_sum=model_precipitation.resample('MS').sum()

                            # simulated temperature
                            model_temperature_conf = model_config["temperature"]
                            model_temperature = retrieveData( model_output_filepath, start_date, end_date, model_temperature_conf )
                            # model_temperature = model_temperature.iloc[:, 0]
                            
                            # simulated swe
                            model_snow_we_conf = model_config["snow_we"]
                            model_snow_we = retrieveData( model_output_filepath, start_date, end_date, model_snow_we_conf )
                            # model_snow_we = model_snow_we.iloc[:, 0]

                            # simulated snow_we_plan
                            model_snow_we_plan_conf = model_config["snow_we_plan"]
                            model_snow_we_plan = retrieveData( model_output_filepath, start_date, end_date, model_snow_we_plan_conf )
                            # model_snow_we_plan = model_snow_we_plan.iloc[:, 0]

                            # simulated sca passirio
                            model_sca_passirio_conf = model_config["sca_passirio"]
                            model_sca_passirio = retrieveData( model_output_filepath, start_date, end_date, model_sca_passirio_conf )

                            # simulated swe nivometro 1
                            model_swe_niv1_conf = model_config["swe_niv1"]
                            model_swe_niv1 = retrieveData( model_output_filepath, start_date, end_date, model_swe_niv1_conf )

                            # simulated swe nivometro 2
                            model_swe_niv2_conf = model_config["swe_niv2"]
                            model_swe_niv2 = retrieveData( model_output_filepath, start_date, end_date, model_swe_niv2_conf )

                            # simulated swe nivometro 3
                            model_swe_niv3_conf = model_config["swe_niv3"]
                            model_swe_niv3 = retrieveData( model_output_filepath, start_date, end_date, model_swe_niv3_conf )

                            # simulated swe nivometro 4
                            model_swe_niv4_conf = model_config["swe_niv4"]
                            model_swe_niv4 = retrieveData( model_output_filepath, start_date, end_date, model_swe_niv4_conf )

                            # simulated swe nivometro 5
                            model_swe_niv5_conf = model_config["swe_niv5"]
                            model_swe_niv5 = retrieveData( model_output_filepath, start_date, end_date, model_swe_niv5_conf )

    # observed flow
    obs_flow_filepath = obs_config["discharge"]["output_path"]
    obs_flow_conf = obs_config["discharge"]
    obs_flow = retrieveData( obs_flow_filepath, start_date, end_date, \
        obs_flow_conf, current_node=current_node )
    obs_flow[obs_flow == -999] = None
    #obs_flow_daily_mean=obs_flow.resample('D').mean()
    #obs_flow_monthly_mean=obs_flow.resample('MS').mean()

    # observed temperature
    obs_temperature_filepath = obs_config["temperature"]["output_path"]
    obs_temperature_conf = obs_config["temperature"]
    obs_temperature = retrieveData( obs_temperature_filepath, \
        start_date, end_date, obs_temperature_conf, current_node=current_node )
    #obs_temperature_daily_mean=obs_temperature.resample('D').mean()
    #obs_temperature_monthly_mean=obs_temperature.resample('MS').mean()

    return model_flow, model_precipitation, model_temperature, \
        obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, model_sca_passirio, \
            model_swe_niv1, model_swe_niv2, model_swe_niv3, model_swe_niv4, model_swe_niv5

def createBoxPlot( df_in, x_label, y_label, output_file, \
    x_major_locator=None, x_major_formatter=None, \
    output_format="pdf", xscale="linear", yscale="linear", \
    width=190, height=90, period="MS", scale_factor=1, \
    tick_size=10, label_size=10, legend_fontsize=8, \
    ratio_width=190, ratio=3740/500, my_dpi=500 ):

    if period == "MS":
        import matplotlib.ticker as ticker
        x_major_locator=ticker.MultipleLocator(1)
        x_labels = range(1,12+1)
        x_major_formatter=ticker.FuncFormatter(lambda x, _: dict(zip(range(len(x_labels)), x_labels)).get(x, ""))
    elif period == "H":
        import matplotlib.ticker as ticker
        x_major_locator=ticker.MultipleLocator(2)
        x_labels = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
        x_major_formatter=ticker.FuncFormatter(lambda x, _: dict(zip(range(len(x_labels)), x_labels)).get(x, ""))
        
    plot_x_inches = ratio / ratio_width * width
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
        figsize = [plot_x_inches, plot_y_inches],
        tight_layout = {'pad': 0},
        dpi=my_dpi
    ) 

    #add data and data_label to legend
    from seaborn import boxplot
    if period == "MS":
        boxplot(x=df_in.index.month, y=df_in.values, ax=axs)
    elif period == "D":
        boxplot(x=df_in.index.daily, y=df_in.values, ax=axs)
    elif period == "H":
        boxplot(x=df_in.index.hour, y=df_in.values, ax=axs)

    axs.tick_params( labelsize=tick_size/scale_factor )

    axs.set_xscale( xscale )
    axs.set_yscale( yscale )

    axs.set_ylabel( y_label, fontsize=label_size/scale_factor )
    axs.set_xlabel( x_label, fontsize=label_size/scale_factor )
    
    if x_major_locator != None:
        axs.xaxis.set_major_locator(x_major_locator)

    if x_major_formatter != None:
        axs.xaxis.set_major_formatter(x_major_formatter)

    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=my_dpi )

    plt.close(fig=fig)

def instantiatePlot( x_label, y_label, \
    output_format='png', xscale="linear", yscale="linear", \
    width=190, height=90, scale_factor=1, \
    tick_size=10, label_size=10, legend_fontsize=8, \
    ratio_width=190, ratio=3740/500, my_dpi=600 ):

    plot_x_inches = ratio / ratio_width * width 
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
        figsize = [plot_x_inches, plot_y_inches],
        tight_layout = {'pad': 0},
        dpi = my_dpi
    )

    axs.tick_params( labelsize=tick_size/scale_factor )
    
    axs.set_xscale( xscale )
    axs.set_yscale( yscale )

    axs.set_ylabel( y_label, fontsize=label_size/scale_factor )
    axs.set_xlabel( x_label, fontsize=label_size/scale_factor )
    axs.legend(fontsize=legend_fontsize/scale_factor)

    return fig, axs

def createPlot( plots, x_label, y_label, output_file, \
    x_major_locator=None, x_major_formatter=None, \
    output_format='png', xscale="linear", yscale="linear", \
    width=190, height=90, scale_factor=1, \
    tick_size=10, label_size=10, legend_fontsize=8, \
    ratio_width=190, ratio=3740/500, my_dpi=600 ):

    plot_x_inches = ratio / ratio_width * width 
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
        figsize = [plot_x_inches, plot_y_inches],
        tight_layout = {'pad': 0},
        dpi = my_dpi
    )

    axs.tick_params( labelsize=tick_size/scale_factor )
    
    axs.set_xscale( xscale )
    axs.set_yscale( yscale )

    axs.set_ylabel( y_label, fontsize=label_size/scale_factor )
    axs.set_xlabel( x_label, fontsize=label_size/scale_factor )
    
    if x_major_locator != None:
        axs.xaxis.set_major_locator(x_major_locator)

    if x_major_formatter != None:
        axs.xaxis.set_major_formatter(x_major_formatter) 
    
    #add data and data_label to legend
    for tp in plots:

        label=None
        linestyle="solid"

        if "label" in tp[1].keys():
            label=tp[1]["label"]
        
        if "linestyle" in tp[1].keys():
            linestyle=tp[1]["linestyle"]

        axs.plot(tp[0], label=label, linestyle=linestyle)
    
    axs.legend(fontsize=legend_fontsize/scale_factor)
    
    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=my_dpi )
    plt.close(fig=fig)

def evaluateECDF( data_to_use ):
    data = np.sort( data_to_use )

    # calculate the proportional values of samples
    norm_cdf = 100. * np.arange(len(data)) / (len(data) - 1)

    data = pd.DataFrame(data, columns=["data"])
    cdf = pd.DataFrame(norm_cdf, columns=["cdf"])

    ecdf_frame = pd.concat([data, cdf], axis=1)
    ecdf_frame.set_index('data', inplace=True) 

    return ecdf_frame

def rewriteDF( df ):
    '''This function takes a dataframe with white spaces as separator, first column as date (%Y-%m-%d) and
    second column as day (%h). It returns a dataframe with index the date and hour (%Y-%m-%dT%H:%M%S)'''

    import pandas as pd
    from datetime import timedelta

    date_time = []
    for i in range(len(df)):
        hour = df[i:i+1]["date"][0]
        #print(hour)
        date = pd.to_datetime(df[i:i+1].index[0])
        #print(date)

        if hour == 24:
            date_updated = date.replace(hour=0)
            date_updated = date_updated + timedelta(days=-1)
        else:
            date_updated = date.replace(hour=hour)
        #print(date_updated)
        date_time.append(date_updated)

    df.set_index(np.array(date_time), drop=True, inplace=True)
    df.drop("date", inplace=True, axis=1)

    return df


def density_eval( height, doy, model='S10', zone='alpine' ):
    
    if model == 'S10':
        if zone=='alpine':
            rho_0 = 223.7
            rho_max = 597.5
            k1 = 0.0012
            k2 = 0.0038
        else:
            print('not a defined zone')

        return round( (rho_max - rho_0) * (1-np.exp( -k1* height - k2* doy)) + rho_0, 2 )
    # 
    if model == 'J09':
        print('Not implemented yet')

def get_df_name(df):
    name =[x for x in globals() if globals()[x] is df][0]
    return name