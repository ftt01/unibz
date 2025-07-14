#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## DESCRIPTION
# meteo_precipitation_passirio_cells_rea11_kr11
# meteo_precipitation_passirio_monthly_cellsBoxplot_kr11-rea11


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
basin_str = 'passirio'

start_date_str = "2010-01-01T00:00:00"
end_date_str = "2019-12-31T23:00:00"
start_date = dt.datetime.strptime( start_date_str, '%Y-%m-%dT%H:%M:%S' )
end_date = dt.datetime.strptime( end_date_str, '%Y-%m-%dT%H:%M:%S' )


# In[ ]:


## REANALYSIS DATASET ##
for el in current.sim_config:
    if el['basin'] == basin:
        meteo_stations_rea_path =  el["sim_path"] + el["meteo_path"] + "reanalysis/observations/precipitation/"
           
        precipitation_df_rea = pd.DataFrame()

        p_file_tot = glob.glob( meteo_stations_rea_path + '*.csv')
        
        for p_file in p_file_tot:
            data_tot = pd.read_csv(p_file, header=0, index_col=0,                 skiprows=4, parse_dates=True, names=[ os.path.basename(p_file)[:-4] ])
            data_tot = data_tot[start_date:end_date]
            data_tot[data_tot == -999] = None
            precipitation_df_rea = pd.concat([precipitation_df_rea, data_tot],axis=1)

# precipitation_rea_sum = precipitation_df_rea.resample('MS').sum()
precipitation_rea_spatial_mean = precipitation_df_rea.mean(axis=1)


# In[ ]:


## KRIGING 11X8 DATASET ##
for el in current.sim_config:
    if el['basin'] == basin:
        meteo_stations_kr11_path =  el["sim_path"] + el["meteo_path"] + "kriging/observations/11x8/precipitation/"
           
        precipitation_df_kr11 = pd.DataFrame()

        p_file_tot = glob.glob( meteo_stations_kr11_path + '*.csv')
        
        for p_file in p_file_tot:
            data_tot = pd.read_csv(p_file, header=0, index_col=0,                 skiprows=4, parse_dates=True, names=[ os.path.basename(p_file)[:-4] ])
            data_tot = data_tot[start_date:end_date]
            data_tot[data_tot == -999] = None
            precipitation_df_kr11 = pd.concat([precipitation_df_kr11, data_tot],axis=1)

precipitation_kr11_spatial_mean = precipitation_df_kr11.mean(axis=1)


# In[ ]:


# boxplot monthly bias
precipitation_bias = precipitation_rea_spatial_mean -     precipitation_kr11_spatial_mean
precipitation_bias_monthly_sum = precipitation_bias.resample('MS').sum()

output_path = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/monthly/"     + "meteo_precipitation_" + basin_str +     "_monthly_spatial_mean_cells_boxplot_rea-kr11." + output_format
createBoxPlot(precipitation_bias_monthly_sum,  "Time $[month]$", 'Prec. bias $[mm/month]$',
              output_path, label="(a)", period='MS', scale_factor=0.5, output_format=output_format, my_dpi=50)

output_path_hd = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/monthly/"     + "meteo_precipitation_" + basin_str +     "_monthly_spatial_mean_cells_boxplot_rea-kr11_HD." + output_format
createBoxPlot(precipitation_bias_monthly_sum,  "Time $[month]$", 'Prec. bias $[mm/month]$', output_path_hd,
              label="(a)", period='MS', scale_factor=0.5, output_format=output_format, my_dpi=600)


# In[ ]:


# spatial ECDF - hourly
precipitation_rea_spatial_ecdf = evaluateECDF( precipitation_rea_spatial_mean )
precipitation_kr11_spatial_ecdf = evaluateECDF( precipitation_kr11_spatial_mean )

plots = []

plt_conf = {}
plt_conf["label"] = "Reanalysis 11x8"
plt_conf["color"] = '#e66101'
plots.append( (precipitation_rea_spatial_ecdf, plt_conf) )

plt_conf = {}
plt_conf["label"] = "Kriging 11x8"
plt_conf["color"] = '#5e3c99'
plots.append( (precipitation_kr11_spatial_ecdf, plt_conf) )

output_file = current.config["output_path"] + "meteo/precipitation/passirio/hourly/meteo_"     + 'precipitation_passirio_hourly_spatialECDF.' + output_format
createPlot( plots, "Precipitation $[mm/hour]$", "ECDF", output_file,     scale_factor=0.5, my_dpi=50)

output_file_hd = current.config["output_path"] + "meteo/precipitation/passirio/hourly/meteo_"     + 'precipitation_passirio_hourly_spatialECDF_HD.' + output_format
createPlot( plots, "Precipitation $[mm/hour]$", "ECDF", output_file_hd,     scale_factor=0.5, my_dpi=600)

output_file = current.config["output_path"] + "meteo/precipitation/passirio/hourly/meteo_"     + 'precipitation_passirio_hourly_spatialECDF_log.' + output_format
createPlot( plots, "Precipitation $[mm/hour]$", "ECDF", output_file,     xscale='log', scale_factor=0.5, my_dpi=50)

output_file_hd = current.config["output_path"] + "meteo/precipitation/passirio/hourly/meteo_"     + 'precipitation_passirio_hourly_spatialECDF_log_HD.' + output_format
createPlot( plots, "Precipitation $[mm/hour]$", "ECDF", output_file_hd,     xscale='log', scale_factor=0.5, my_dpi=600)


# In[ ]:


# spatial ECDF - monthly
precipitation_rea_spatial_ecdf = evaluateECDF( precipitation_rea_spatial_mean.resample('MS').sum() )
precipitation_kr11_spatial_ecdf = evaluateECDF( precipitation_kr11_spatial_mean.resample('MS').sum() )

plots = []

plt_conf = {}
plt_conf["label"] = "Reanalysis 11x8"
plt_conf["color"] = '#e66101'
plots.append( (precipitation_rea_spatial_ecdf, plt_conf) )

plt_conf = {}
plt_conf["label"] = "Kriging 11x8"
plt_conf["color"] = '#5e3c99'
plots.append( (precipitation_kr11_spatial_ecdf, plt_conf) )

output_file = current.config["output_path"] + "meteo/precipitation/passirio/monthly/meteo_"     + 'precipitation_passirio_monthly_spatialECDF.' + output_format
createPlot( plots, "Precipitation $[mm/month]$", "ECDF", output_file,     scale_factor=0.5, my_dpi=50)

output_file_hd = current.config["output_path"] + "meteo/precipitation/passirio/monthly/meteo_"     + 'precipitation_passirio_monthly_spatialECDF_HD.' + output_format
createPlot( plots, "Precipitation $[mm/month]$", "ECDF", output_file_hd,     scale_factor=0.5, my_dpi=600)

output_file = current.config["output_path"] + "meteo/precipitation/passirio/monthly/meteo_"     + 'precipitation_passirio_monthly_spatialECDF_log.' + output_format
createPlot( plots, "Precipitation $[mm/month]$", "ECDF", output_file,     xscale='log', scale_factor=0.5, my_dpi=50)

output_file_hd = current.config["output_path"] + "meteo/precipitation/passirio/monthly/meteo_"     + 'precipitation_passirio_monthly_spatialECDF_log_HD.' + output_format
createPlot( plots, "Precipitation $[mm/month]$", "ECDF", output_file_hd,     xscale='log', scale_factor=0.5, my_dpi=600)


# In[ ]:


precipitation_bias = precipitation_rea_spatial_mean - precipitation_kr11_spatial_mean

#-------------------boxplot seasonal--------------------     
precipitation_bias_jan=precipitation_bias.loc[(precipitation_bias.index.month==1)]
precipitation_bias_feb=precipitation_bias.loc[(precipitation_bias.index.month==2)]
precipitation_bias_mar=precipitation_bias.loc[(precipitation_bias.index.month==3)]
precipitation_bias_apr=precipitation_bias.loc[(precipitation_bias.index.month==4)]
precipitation_bias_may=precipitation_bias.loc[(precipitation_bias.index.month==5)]
precipitation_bias_jun=precipitation_bias.loc[(precipitation_bias.index.month==6)]
precipitation_bias_jul=precipitation_bias.loc[(precipitation_bias.index.month==7)]
precipitation_bias_aug=precipitation_bias.loc[(precipitation_bias.index.month==8)]
precipitation_bias_sep=precipitation_bias.loc[(precipitation_bias.index.month==9)]
precipitation_bias_oct=precipitation_bias.loc[(precipitation_bias.index.month==10)]
precipitation_bias_nov=precipitation_bias.loc[(precipitation_bias.index.month==11)]
precipitation_bias_dec=precipitation_bias.loc[(precipitation_bias.index.month==12)]

precipitation_bias_w=pd.concat([precipitation_bias_jan,precipitation_bias_feb,precipitation_bias_mar])
precipitation_bias_sp=pd.concat([precipitation_bias_apr,precipitation_bias_may,precipitation_bias_jun])
precipitation_bias_su=pd.concat([precipitation_bias_jul,precipitation_bias_aug,precipitation_bias_sep])
precipitation_bias_a=pd.concat([precipitation_bias_oct,precipitation_bias_nov,precipitation_bias_dec])

output_file = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/hourly/seasonal/"     + 'meteo_precipitation_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_winter.' + output_format
createBoxPlot( precipitation_bias_w, "Time $[hour]$", "Prec. $[mm/hour]$",     output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/hourly/seasonal/"     + 'meteo_precipitation_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_winter_HD.' + output_format
createBoxPlot( precipitation_bias_w, "Time $[hour]$", "Prec. $[mm/hour]$",     output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

output_file = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/hourly/seasonal/"     + 'meteo_precipitation_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_spring.' + output_format
createBoxPlot( precipitation_bias_sp, "Time $[hour]$", "Prec. $[mm/hour]$",     output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/hourly/seasonal/"     + 'meteo_precipitation_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_spring_HD.' + output_format
createBoxPlot( precipitation_bias_sp, "Time $[hour]$", "Prec. $[mm/hour]$",     output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

output_file = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/hourly/seasonal/"     + 'meteo_precipitation_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_summer.' + output_format
createBoxPlot( precipitation_bias_su, "Time $[hour]$", "Prec. $[mm/hour]$",     output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/hourly/seasonal/"     + 'meteo_precipitation_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_summer_HD.' + output_format
createBoxPlot( precipitation_bias_su, "Time $[hour]$", "Prec. $[mm/hour]$",     output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

output_file = current.config["output_path"] +"meteo/precipitation/" + basin_str + "/hourly/seasonal/"     + 'meteo_precipitation_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_autumn.' + output_format
createBoxPlot( precipitation_bias_a, "Time $[hour]$", "Prec. $[mm/hour]$",     output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/hourly/seasonal/"     + 'meteo_precipitation_' + basin_str + '_hourly_boxplot_spatial_mean_cells_rea-kr11_autumn_HD.' + output_format
createBoxPlot( precipitation_bias_a, "Time $[hour]$", "Prec. $[mm/hour]$",     output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )


# In[ ]:


# plots = []

# plt_conf = {}
# plt_conf["label"] = 'Kriging 11x8'
# plt_conf["color"] = 'orange'
# plots.append( (precipitation_kr11_mean, plt_conf) )

# plt_conf = {}
# plt_conf["label"] = 'Reanalysis 11x8'
# plt_conf["color"] = '#e66101'
# plots.append( (precipitation_rea_mean, plt_conf) )

# outfile = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/monthly/" \
#     + "meteo_precipitation_" + basin_str + "_cells_rea11_kr11." + output_format
# createPlot( plots, "Time $[month]$", 'Precipitation $[mm/month]$', outfile, my_dpi=50 )

# outfile_hd = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/monthly/" \
#     + "meteo_precipitation_" + basin_str + "_cells_rea11_kr11_hd." + output_format
# createPlot( plots, "Time $[month]$", 'Precipitation $[mm/month]$', outfile_hd, my_dpi=600 )

# #######################################################################################################

