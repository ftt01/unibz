#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# DESCRIPTION
# model_temperature_AA_monthlyBias_kr-rea
# model_temperature_AA_monthlyBias_kr-kr11
# model_temperature_AA_monthlyBias_kr11-rea

# model_temperature_AA_boxplot_500-3000_kr-rea11
# model_temperature_AA_boxplot_500-3000_kr11-kr
# model_temperature_AA_boxplot_500-3000_kr11-rea11


# In[ ]:


# wdir = "C:/Users/daniele/Documents/GitHub/ftt01/phd/hydro_modeling/ichymod/C_postprocessing/scripts/"
wdir = "/home/daniele/documents/github/ftt01/phd/hydro_modeling/ichymod/C_postprocessing/scripts/"


# In[ ]:


import sys, os
# sys.path.insert( 0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(''))),'lib') )
# to link the lib in py scripts as well
os.chdir( wdir )
sys.path.insert( 0, os.path.join(os.path.abspath(os.getcwd()),'lib') )

from lib import *
current = DataCollector()


# In[ ]:


start_date_str = "2013-10-01T01:00:00"
end_date_str = "2020-09-30T23:00:00"
start_date = dt.datetime.strptime( start_date_str, '%Y-%m-%dT%H:%M:%S' )
end_date = dt.datetime.strptime( end_date_str, '%Y-%m-%dT%H:%M:%S' )

zz_top = [500, 1000, 1500, 2000, 2500, 3000] # elevation in meters
added_cols = []
for el in zz_top:
    added_cols.append( "t_at_" + str(el) )


# In[ ]:


def evaluateTemperatures( df, z_list=[1000] ):
    for elevation in zz_top:
        evaluated_temp = []
        column_str = 't_at_' + str(elevation)
        for i in range( len(df) ):
            evaluated_temp.append(float(df[i:i+1]['t_int']) + float(df[i:i+1]['t_slope']) * elevation)
        df[column_str] = evaluated_temp
    
    return df


# In[ ]:


## KRIGING DATASET ##
fileName_kr = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/meteo/kriging/observations/1x1/temperature.txt"
#fileName_kr = "/media/windows/projects/era5_bias/CALIBRAZIONE_PASSIRIO_REANALISYS/hydro_modelling/Passirio/meteo/kriging/observations/precipitation.txt"
df_kr = pd.read_csv(fileName_kr, header=None, index_col=0, parse_dates=True, names=['t_int', 't_slope'])

df_kr = evaluateTemperatures( df_kr, zz_top )

temperature_kr_monthly_mean = df_kr.resample('MS').mean()


# In[ ]:


## KRIGING 11X8 DATASET ##
fileName_kr11 = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/meteo/kriging/observations/11x8/temperature.txt"
#fileName_kr11 = "/media/windows/projects/era5_bias/CALIBRAZIONE_PASSIRIO_KRIGING_11x8/hydro_modelling/Passirio/meteo/kriging/observations/precipitation.txt"
df_kr11 = pd.read_csv(fileName_kr11, header=None, index_col=0, parse_dates=True, delimiter=r"\s+", names=['date', 't_int', 't_slope'])
df_kr11 = rewriteDF(df_kr11)
df_kr11 = df_kr11.sort_index()

df_kr11 = evaluateTemperatures( df_kr11, zz_top )

temperature_kr11_monthly_mean = df_kr11.resample('MS').mean()


# In[ ]:


## REANALYSIS DATASET ##
fileName_rea = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/meteo/reanalysis/observations/temperature.txt"
#fileName_rea =  "/media/windows/projects/era5_bias/CALIBRAZIONE_PASSIRIO_REANALISYS/hydro_modelling/Passirio/meteo/reanalysis/observations/precipitation.txt"
df_rea = pd.read_csv(fileName_rea, header=None, index_col=0, parse_dates=True, delimiter=r"\s+", names=['date', 't_int', 't_slope'])
df_rea = rewriteDF(df_rea)
df_rea = df_rea.sort_index()

df_rea = evaluateTemperatures( df_rea, zz_top )

temperature_rea_monthly_mean = df_rea.resample('MS').mean()


# In[ ]:



## OBSERVED ##
#fileName_obs = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/meteo/GS/observations/precipitation.txt"
#df_obs = pd.read_csv(fileName_obs, header=0, index_col=0, parse_dates=True, delimiter=r"\s+")
#df_obs = rewriteDF(df_obs)

## BASINS ##
#fileName_basins = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/INPUT/topological_elements/basins.txt"


# In[ ]:


###### BOXPLOTS ######

temperature_rea_kr_comparison = df_rea[start_date:end_date] - df_kr[start_date:end_date]
bias_rea_kr_plots = []

temperature_rea_kr11_comparison = df_rea[start_date:end_date] - df_kr11[start_date:end_date]
bias_rea_kr11_plots = []

temperature_kr11_kr_comparison = df_kr11[start_date:end_date] - df_kr[start_date:end_date]
bias_kr11_kr_plots = []

index = 0
for col in added_cols:

    temperature_at_rea_kr = temperature_rea_kr_comparison[col]
    temperature_at_rea_kr_mean = temperature_at_rea_kr.resample('MS').mean()

    bias_rea_kr_plots.append( (temperature_at_rea_kr_mean, {"label":str(zz_top[index])}) )

    temperature_at_rea_kr11 = temperature_rea_kr11_comparison[col]
    temperature_at_rea_kr11_mean = temperature_at_rea_kr11.resample('MS').mean()

    bias_rea_kr11_plots.append( (temperature_at_rea_kr11_mean, {"label":str(zz_top[index])}) )

    temperature_at_kr11_kr = temperature_kr11_kr_comparison[col]
    temperature_at_kr11_kr_mean = temperature_at_kr11_kr.resample('MS').mean()

    bias_kr11_kr_plots.append( (temperature_at_kr11_kr_mean, {"label":str(zz_top[index])}) )

    index = index + 1

createPlot( bias_rea_kr_plots, "Time $[month]$", 'Temp. bias [$\degree C$]',     current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"         + "model_temperature_AA_monthlyBias_kr-rea." + output_format, my_dpi=50 )

createPlot( bias_rea_kr_plots, "Time $[month]$", 'Temp. bias [$\degree C$]',     current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"         + "model_temperature_AA_monthlyBias_kr-rea_HD." + output_format, my_dpi=600 )

createPlot( bias_kr11_kr_plots, "Time $[month]$", 'Temp. bias [$\degree C$]',     current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"         + "model_temperature_AA_monthlyBias_kr-kr11." + output_format, my_dpi=50 )

createPlot( bias_kr11_kr_plots, "Time $[month]$", 'Temp. bias [$\degree C$]',     current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"         + "model_temperature_AA_monthlyBias_kr-kr11_hd." + output_format, my_dpi=600 )

createPlot( bias_rea_kr11_plots, "Time $[month]$", 'Temp. bias [$\degree C$]',     current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"         + "model_temperature_AA_monthlyBias_kr11-rea." + output_format, my_dpi=50 )

createPlot( bias_rea_kr11_plots, "Time $[month]$", 'Temp. bias [$\degree C$]',     current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"         + "model_temperature_AA_monthlyBias_kr11-rea_hd." + output_format, my_dpi=600 )


# In[ ]:


################ BOXPLOT BIAS kriging - reanalysis ##################
rea_kr_bias = temperature_rea_kr_comparison[added_cols[len(added_cols)-1]].resample('MS').mean() -     temperature_rea_kr_comparison[added_cols[0]].resample('MS').mean()

output_path = current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"     "model_temperature_passirio_boxplot_" + added_cols[len(added_cols)-1] + "-" + added_cols[0] + "_rea-kr." + output_format 

createBoxPlot( rea_kr_bias,  "Time $[month]$", "Temp. bias $[\degree C]$",     output_path, period='MS', output_format=output_format, my_dpi=50 )

output_path_hd = current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"     "model_temperature_passirio_boxplot_" + added_cols[len(added_cols)-1] + "-" + added_cols[0] + "_rea-kr_HD." + output_format 

createBoxPlot( rea_kr_bias,  "Time $[month]$", "Temp. bias $[\degree C]$",     output_path_hd, period='MS', output_format=output_format, my_dpi=600)


# In[ ]:


################ BOXPLOT BIAS kriging - kriging11 ##################
kr11_kr_bias = temperature_kr11_kr_comparison[added_cols[len(added_cols)-1]].resample('MS').mean() -     temperature_kr11_kr_comparison[added_cols[0]].resample('MS').mean()

output_path = current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"     "model_temperature_passirio_boxplot_" + added_cols[len(added_cols)-1] + "-" + added_cols[0] + "_kr11-kr." + output_format 

createBoxPlot( kr11_kr_bias,  "Time $[month]$", "Temp. bias $[\degree C]$",     output_path, period='MS', output_format=output_format, my_dpi=50 )

output_path_hd = current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"     "model_temperature_passirio_boxplot_" + added_cols[len(added_cols)-1] + "-" + added_cols[0] + "_kr11-kr_HD." + output_format 

createBoxPlot( kr11_kr_bias,  "Time $[month]$", "Temp. bias $[\degree C]$",     output_path_hd, period='MS', output_format=output_format, my_dpi=600)


# In[ ]:


################ BOXPLOT BIAS kriging11 - reanalysis ##################
rea_kr11_bias = temperature_rea_kr11_comparison[added_cols[len(added_cols)-1]].resample('MS').mean() -     temperature_rea_kr11_comparison[added_cols[0]].resample('MS').mean()

output_path = current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"     "model_temperature_passirio_boxplot_" + added_cols[len(added_cols)-1] + "-" + added_cols[0] + "_rea-kr11." + output_format 

createBoxPlot( rea_kr11_bias,  "Time $[month]$", "Temp. bias $[\degree C]$",     output_path, period='MS', output_format=output_format, my_dpi=50 )

output_path_hd = current.config["output_path"] + "model/temperature/passirio/monthly/over_elevation/"     "model_temperature_passirio_boxplot_" + added_cols[len(added_cols)-1] + "-" + added_cols[0] + "_rea-kr11_HD." + output_format 

createBoxPlot( rea_kr11_bias,  "Time $[month]$", "Temp. bias $[\degree C]$",     output_path_hd, period='MS', output_format=output_format, my_dpi=600)


# In[ ]:




