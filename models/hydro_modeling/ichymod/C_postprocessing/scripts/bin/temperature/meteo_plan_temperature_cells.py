#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## DESCRIPTION
# meteo_temperature_plan_boxplotBias_cells_kr11-rea
# meteo_temperature_plan_boxplotBias_cells_kr11-rea_*


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
import glob


# In[ ]:


## SETUP
basin = 'passirio'
# for output name
basin_str = 'plan'

start_date_str = "2013-10-01T01:00:00"
end_date_str = "2020-09-30T23:00:00"
start_date = dt.datetime.strptime( start_date_str, '%Y-%m-%dT%H:%M:%S' )
end_date = dt.datetime.strptime( end_date_str, '%Y-%m-%dT%H:%M:%S' )


# In[ ]:


for el in current.sim_config:
    if el['basin'] == basin:
        ## REANALYSIS DATASET ##
        meteo_stations_rea_path = el["sim_path"] + el["meteo_path"] + "reanalysis/observations/temperature/"

        temperature_df_rea = pd.DataFrame()

        data_tot = pd.read_csv(meteo_stations_rea_path + '129.csv',index_col=0,parse_dates=True,skiprows=4,names=['values'])
        data_tot=data_tot[start_date:end_date]
        data_tot[data_tot == -999] = None
        temperature_df_rea=pd.concat([temperature_df_rea,data_tot],axis=1)

        data_tot = pd.read_csv(meteo_stations_rea_path + '153.csv',index_col=0,parse_dates=True,skiprows=4,names=['values'])
        data_tot=data_tot[start_date:end_date]
        data_tot[data_tot == -999] = None
        temperature_df_rea=pd.concat([temperature_df_rea,data_tot],axis=1)

        # spatial mean over all cells
        temperature_rea_spatial_mean = temperature_df_rea.mean(axis=1)

        ###################################
        ## KRIGING 11X8 DATASET ##
        meteo_stations_kr11_path = el["sim_path"] + el["meteo_path"] + "kriging/observations/11x8/temperature/"

        temperature_df_kr11 = pd.DataFrame()

        data_tot = pd.read_csv(meteo_stations_kr11_path + '129.csv',index_col=0,parse_dates=True,skiprows=4,names=['values'])
        data_tot=data_tot[start_date:end_date]
        data_tot[data_tot == -999] = None
        temperature_df_kr11=pd.concat([temperature_df_kr11,data_tot],axis=1)

        data_tot = pd.read_csv(meteo_stations_kr11_path + '153.csv',index_col=0,parse_dates=True,skiprows=4,names=['values'])
        data_tot=data_tot[start_date:end_date]
        data_tot[data_tot == -999] = None
        temperature_df_kr11=pd.concat([temperature_df_kr11,data_tot],axis=1)

        # spatial mean over all cells
        temperature_kr11_spatial_mean = temperature_df_kr11.mean(axis=1)


# In[ ]:


# boxplot monthly bias
temperature_bias = temperature_rea_spatial_mean - temperature_kr11_spatial_mean
temperature_bias_monthly_sum = temperature_bias.resample('MS').mean()

output_path = current.config["output_path"] + "meteo/temperature/" + basin_str + "/monthly/"     + "meteo_temperature_" + basin_str + "_monthly_spatial_mean_cells_boxplot_rea-kr11." + output_format 

createBoxPlot( temperature_bias_monthly_sum,  "Time $[month]$", "Temp. bias $[\degree C]$",     output_path, period='MS', output_format=output_format, my_dpi=50 )

output_path_hd = current.config["output_path"] +"meteo/temperature/" + basin_str + "/monthly/"     + "meteo_temperature_" + basin_str + "_monthly_spatial_mean_cells_boxplot_rea-kr11_HD." + output_format 

createBoxPlot( temperature_bias_monthly_sum,  "Time $[month]$", "Temp. bias $[\degree C]$",     output_path_hd, period='MS', output_format=output_format, my_dpi=600)


# In[ ]:


# boxplot hourly bias
temperature_bias = temperature_rea_spatial_mean - temperature_kr11_spatial_mean

output_path = current.config["output_path"] + "meteo/temperature/" + basin_str + "/hourly/"     + "meteo_temperature_" + basin_str + "_hourly_spatial_mean_cells_boxplot_rea-kr11." + output_format 

createBoxPlot( temperature_bias,  "Time $[hour]$", "Temp. bias $[\degree C]$",     output_path, period='MS', output_format=output_format, my_dpi=50 )

output_path_hd = current.config["output_path"] +"meteo/temperature/" + basin_str + "/hourly/"     + "meteo_temperature_" + basin_str + "_hourly_spatial_mean_cells_boxplot_rea-kr11_HD." + output_format 

createBoxPlot( temperature_bias,  "Time $[hour]$", "Temp. bias $[\degree C]$",     output_path_hd, period='MS', output_format=output_format, my_dpi=600)


# In[ ]:


# spatial ECDF - hourly
temperature_rea_spatial_ecdf = evaluateECDF( temperature_rea_spatial_mean )
temperature_kr11_spatial_ecdf = evaluateECDF( temperature_kr11_spatial_mean )

plots = []

plt_conf = {}
plt_conf["label"] = "Reanalysis 11x8"
plt_conf["color"] = '#e66101'
plots.append( (temperature_rea_spatial_ecdf, plt_conf) )

plt_conf = {}
plt_conf["label"] = "Kriging 11x8"
plt_conf["color"] = '#5e3c99'
plots.append( (temperature_kr11_spatial_ecdf, plt_conf) )

output_file = current.config["output_path"] + "meteo/temperature/passirio/hourly/meteo_"     + 'temperature_passirio_hourly_spatialECDF.' + output_format
createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file,     scale_factor=0.5, my_dpi=50)

output_file_hd = current.config["output_path"] + "meteo/temperature/passirio/hourly/meteo_"     + 'temperature_passirio_hourly_spatialECDF_HD.' + output_format
createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file_hd,     scale_factor=0.5, my_dpi=600)

output_file = current.config["output_path"] + "meteo/temperature/passirio/hourly/meteo_"     + 'temperature_passirio_hourly_spatialECDF_log.' + output_format
createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file,     xscale='log', scale_factor=0.5, my_dpi=50)

output_file_hd = current.config["output_path"] + "meteo/temperature/passirio/hourly/meteo_"     + 'temperature_passirio_hourly_spatialECDF_log_HD.' + output_format
createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file_hd,     xscale='log', scale_factor=0.5, my_dpi=600)


# In[ ]:


# spatial ECDF - monthly
temperature_rea_spatial_ecdf = evaluateECDF( temperature_rea_spatial_mean.resample('MS').mean() )
temperature_kr11_spatial_ecdf = evaluateECDF( temperature_kr11_spatial_mean.resample('MS').mean() )

plots = []

plt_conf = {}
plt_conf["label"] = "Reanalysis 11x8"
plt_conf["color"] = '#e66101'
plots.append( (temperature_rea_spatial_ecdf, plt_conf) )

plt_conf = {}
plt_conf["label"] = "Kriging 11x8"
plt_conf["color"] = '#5e3c99'
plots.append( (temperature_kr11_spatial_ecdf, plt_conf) )

output_file = current.config["output_path"] + "meteo/temperature/passirio/monthly/meteo_"     + 'temperature_passirio_monthly_spatialECDF.' + output_format
createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file,     scale_factor=0.5, my_dpi=50)

output_file_hd = current.config["output_path"] + "meteo/temperature/passirio/monthly/meteo_"     + 'temperature_passirio_monthly_spatialECDF_HD.' + output_format
createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file_hd,     scale_factor=0.5, my_dpi=600)

output_file = current.config["output_path"] + "meteo/temperature/passirio/monthly/meteo_"     + 'temperature_passirio_monthly_spatialECDF_log.' + output_format
createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file,     xscale='log', scale_factor=0.5, my_dpi=50)

output_file_hd = current.config["output_path"] + "meteo/temperature/passirio/monthly/meteo_"     + 'temperature_passirio_monthly_spatialECDF_log_HD.' + output_format
createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file_hd,     xscale='log', scale_factor=0.5, my_dpi=600)


# In[ ]:


temperature_bias = temperature_rea_spatial_mean - temperature_kr11_spatial_mean

#-------------------boxplot seasonal--------------------     
temperature_bias_jan=temperature_bias.loc[(temperature_bias.index.month==1)]
temperature_bias_feb=temperature_bias.loc[(temperature_bias.index.month==2)]
temperature_bias_mar=temperature_bias.loc[(temperature_bias.index.month==3)]
temperature_bias_apr=temperature_bias.loc[(temperature_bias.index.month==4)]
temperature_bias_may=temperature_bias.loc[(temperature_bias.index.month==5)]
temperature_bias_jun=temperature_bias.loc[(temperature_bias.index.month==6)]
temperature_bias_jul=temperature_bias.loc[(temperature_bias.index.month==7)]
temperature_bias_aug=temperature_bias.loc[(temperature_bias.index.month==8)]
temperature_bias_sep=temperature_bias.loc[(temperature_bias.index.month==9)]
temperature_bias_oct=temperature_bias.loc[(temperature_bias.index.month==10)]
temperature_bias_nov=temperature_bias.loc[(temperature_bias.index.month==11)]
temperature_bias_dec=temperature_bias.loc[(temperature_bias.index.month==12)]

temperature_bias_w=pd.concat([temperature_bias_jan,temperature_bias_feb,temperature_bias_mar])
temperature_bias_sp=pd.concat([temperature_bias_apr,temperature_bias_may,temperature_bias_jun])
temperature_bias_su=pd.concat([temperature_bias_jul,temperature_bias_aug,temperature_bias_sep])
temperature_bias_a=pd.concat([temperature_bias_oct,temperature_bias_nov,temperature_bias_dec])

output_file = current.config["output_path"] + "meteo/temperature/" + basin_str + "/hourly/seasonal/"     + 'meteo_temperature_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_winter.' + output_format
createBoxPlot( temperature_bias_w, "Time $[hour]$", "Temp. bias $[\degree C]$",     output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/temperature/" + basin_str + "/hourly/seasonal/"     + 'meteo_temperature_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_winter_HD.' + output_format
createBoxPlot( temperature_bias_w, "Time $[hour]$", "Temp. bias $[\degree C]$",     output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

output_file = current.config["output_path"] + "meteo/temperature/" + basin_str + "/hourly/seasonal/"     + 'meteo_temperature_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_spring.' + output_format
createBoxPlot( temperature_bias_sp, "Time $[hour]$", "Temp. bias $[\degree C]$",     output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/temperature/" + basin_str + "/hourly/seasonal/"     + 'meteo_temperature_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_spring_HD.' + output_format
createBoxPlot( temperature_bias_sp, "Time $[hour]$", "Temp. bias $[\degree C]$",     output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

output_file = current.config["output_path"] + "meteo/temperature/" + basin_str + "/hourly/seasonal/"     + 'meteo_temperature_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_summer.' + output_format
createBoxPlot( temperature_bias_su, "Time $[hour]$", "Temp. bias $[\degree C]$",     output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/temperature/" + basin_str + "/hourly/seasonal/"     + 'meteo_temperature_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_summer_HD.' + output_format
createBoxPlot( temperature_bias_su, "Time $[hour]$", "Temp. bias $[\degree C]$",     output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

output_file = current.config["output_path"] +"meteo/temperature/" + basin_str + "/hourly/seasonal/"     + 'meteo_temperature_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_autumn.' + output_format
createBoxPlot( temperature_bias_a, "Time $[hour]$", "Temp. bias $[\degree C]$",     output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/temperature/" + basin_str + "/hourly/seasonal/"     + 'meteo_temperature_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_autumn_HD.' + output_format
createBoxPlot( temperature_bias_a, "Time $[hour]$", "Temp. bias $[\degree C]$",     output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

