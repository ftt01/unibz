#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## DESCRIPTION
# model_precipitation_passirio_hourly_kr_rea_kr11
# model_precipitation_passirio_monthly_kr_rea_kr11
# model_precipitation_passirio_boxplot_kr-rea
# model_precipitation_passirio_boxplot_kr-kr11
# model_precipitation_passirio_boxplot_kr11-rea


# In[ ]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )


# In[ ]:


from lib import *


# In[ ]:


## SETUP
current_basin = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,19,20,21,22,23]
# for output name
basin_str = 'passirio'

start_date_str = "2013-10-01T01:00:00"
end_date_str = "2019-12-31T23:00:00"
start_date = dt.datetime.strptime( start_date_str, '%Y-%m-%dT%H:%M:%S' )
end_date = dt.datetime.strptime( end_date_str, '%Y-%m-%dT%H:%M:%S' )


# In[ ]:


## BASINS ##
fileName_basins = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/INPUT/topological_elements/basins.txt"

df_basins = pd.read_csv(fileName_basins, header=None, delimiter=r"\s+", index_col=0)


# In[ ]:


## KRIGING DATASET ##
fileName_kr = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/meteo/kriging/observations/1x1/precipitation.txt"

df_kr = pd.read_csv(fileName_kr, header=0, index_col=0, parse_dates=True)

precipitation_kr = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_kr = pd.concat([precipitation_kr, 
            df_kr[start_date:end_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_kr_passirio_sum = precipitation_kr.sum(axis=1)


# In[ ]:


## KRIGING 11X8 DATASET ##
fileName_kr11 = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/meteo/kriging/observations/11x8/precipitation.txt"

df_kr11 = pd.read_csv(fileName_kr11, header=0, index_col=0, parse_dates=True, delimiter=r"\s+")
df_kr11 = rewriteDF(df_kr11)
df_kr11 = df_kr11.sort_index()

precipitation_kr11 = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_kr11 = pd.concat([precipitation_kr11, 
            df_kr11[start_date:end_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_kr11_passirio_sum = precipitation_kr11.sum(axis=1)


# In[ ]:


## REANALYSIS DATASET ##
fileName_rea = "/media/windows/projects/era5_bias/02_calibration_validation/hydro_modelling/Passirio/meteo/reanalysis/observations/precipitation.txt"

df_rea = pd.read_csv(fileName_rea, header=0, index_col=0, parse_dates=True, delimiter=r"\s+")
df_rea = rewriteDF(df_rea)
df_rea = df_rea.sort_index()

precipitation_rea = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_rea = pd.concat([precipitation_rea, 
            df_rea[start_date:end_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_rea_passirio_sum = precipitation_rea.sum(axis=1)


# In[ ]:


################################ PRECIPITATION MONTHLY #####################################
precipitation_kr_passirio_monthly_mean = precipitation_kr_passirio_sum.resample('MS').sum()
precipitation_kr11_passirio_monthly_mean = precipitation_kr11_passirio_sum.resample('MS').sum()
precipitation_rea_passirio_monthly_mean = precipitation_rea_passirio_sum.resample('MS').sum()

plots = []

plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_rea_passirio_monthly_mean, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_kr_passirio_monthly_mean, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_kr11_passirio_monthly_mean, plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile = current.config["output_path"] + "model/precipitation/" + basin_str + "/monthly/"     + "model_precipitation_" + basin_str + "_monthly_kr_rea_kr11." + output_format
createPlot( plots, "Time $[month]$", 'Prec. [$mm/month$]', outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )

outfile_hd = current.config["output_path"] + "model/precipitation/" + basin_str + "/monthly/"     + "model_precipitation_" + basin_str + "_monthly_kr_rea_kr11_HD." + output_format
createPlot( plots, "Time $[month]$", 'Prec. [$mm/month$]', outfile_hd,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )


# In[ ]:


################################ PRECIPITATION HOURLY #####################################
############################# CALIBRATION + VALIDATION ####################################
plots = []

plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_rea_passirio_sum, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_kr_passirio_sum, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_kr11_passirio_sum, plt_conf) )


import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile = current.config["output_path"] + "model/precipitation/" + basin_str + "/hourly/"     + "model_precipitation_" + basin_str + "_hourly_kr_rea_kr11." + output_format
createPlot( plots, "Time $[hour]$", 'Precipitation $[mm/hour]$', outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )
    
outfile_hd = current.config["output_path"] + "model/precipitation/" + basin_str + "/hourly/"     + "model_precipitation_" + basin_str + "_hourly_kr_rea_kr11_HD." + output_format
createPlot( plots, "Time $[hour]$", 'Precipitation $[mm/hour]$', outfile_hd,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )


# In[ ]:


################################### ONLY VALIDATION #######################################
start_VAL_date_str = "2017-10-01T01:00:00"
end_VAL_date_str = "2020-09-30T23:00:00"
start_VAL_date = dt.datetime.strptime( start_VAL_date_str, '%Y-%m-%dT%H:%M:%S' )
end_VAL_date = dt.datetime.strptime( end_VAL_date_str, '%Y-%m-%dT%H:%M:%S' )

precipitation_VAL_kr = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_VAL_kr = pd.concat([precipitation_VAL_kr, 
            df_kr[start_VAL_date:end_VAL_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_VAL_kr_passirio_sum = precipitation_VAL_kr.sum(axis=1)


# In[ ]:


precipitation_VAL_kr11 = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_VAL_kr11 = pd.concat([precipitation_VAL_kr11, 
            df_kr11[start_VAL_date:end_VAL_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_VAL_kr11_passirio_sum = precipitation_VAL_kr11.sum(axis=1)


# In[ ]:


precipitation_VAL_rea = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_VAL_rea = pd.concat([precipitation_VAL_rea, 
            df_rea[start_VAL_date:end_VAL_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_VAL_rea_passirio_sum = precipitation_VAL_rea.sum(axis=1)


# In[ ]:


plots = []

plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_VAL_rea_passirio_sum, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_VAL_kr_passirio_sum, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plt_conf["linewidth"] = 0.8
plots.append( (precipitation_VAL_kr11_passirio_sum, plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile = current.config["output_path"] + "model/precipitation/" + basin_str + "/hourly/"     + "model_precipitation_" + basin_str + "_hourly_kr_rea_kr11_validation." + output_format
createPlot( plots, "Time $[hour]$", 'Precipitation $[mm/hour]$', outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )
    
outfile_hd = current.config["output_path"] + "model/precipitation/" + basin_str + "/hourly/"     + "model_precipitation_" + basin_str + "_hourly_kr_rea_kr11_validation_HD." + output_format
createPlot( plots, "Time $[hour]$", 'Precipitation $[mm/hour]$', outfile_hd,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )


# In[ ]:


################################ BOXPLOT BIAS ###############################################
############################ reanalysis - kriging ###########################################
diff_rea_kr_passirio = precipitation_rea_passirio_monthly_mean - precipitation_kr_passirio_monthly_mean

output_path = current.config["output_path"] + "model/precipitation/" + basin_str + "/monthly/"     + "model_precipitation_" + basin_str + "_boxplot_rea-kr." + output_format
createBoxPlot( diff_rea_kr_passirio,  "Time $[month]$", "Prec. bias $[mm/month]$",     output_path, output_format=output_format, my_dpi=50 )

output_path_hd = current.config["output_path"] + "model/precipitation/" + basin_str + "/monthly/"     + "model_precipitation_" + basin_str + "_boxplot_rea-kr_HD." + output_format 
createBoxPlot( diff_rea_kr_passirio,  "Time $[month]$", "Prec. bias $[mm/month]$",     output_path_hd, output_format=output_format, my_dpi=600 )

############################ kriging_11 - kriging ###########################################
diff_kr11_kr_merano = precipitation_kr11_passirio_monthly_mean - precipitation_kr_passirio_monthly_mean

output_path = current.config["output_path"] + "model/precipitation/" + basin_str + "/monthly/"     + "model_precipitation_" + basin_str + "_boxplot_kr11-kr." + output_format 
createBoxPlot( diff_kr11_kr_merano,  "Time $[month]$", "Prec. bias $[mm/month]$", output_path, output_format=output_format, my_dpi=50 )

output_path_hd = current.config["output_path"] + "model/precipitation/" + basin_str + "/monthly/"     + "model_precipitation_" + basin_str + "_boxplot_kr11-kr_HD." + output_format 
createBoxPlot( diff_kr11_kr_merano,  "Time $[month]$", "Prec. bias $[mm/month]$", output_path_hd, output_format=output_format, my_dpi=600 )

############################ kriging_11 - reanalysis ###########################################
diff_kr11_rea_merano = precipitation_rea_passirio_monthly_mean - precipitation_kr11_passirio_monthly_mean

output_path = current.config["output_path"] + "model/precipitation/" + basin_str + "/monthly/"     + "model_precipitation_" + basin_str + "_boxplot_rea-kr11." + output_format 

createBoxPlot( diff_kr11_rea_merano,  "Time $[month]$", "Prec. bias $[mm/month]$",     output_path, output_format=output_format, my_dpi=50 )

output_path_hd = current.config["output_path"] + "model/precipitation/" + basin_str + "/monthly/"     + "model_precipitation_" + basin_str + "_boxplot_rea-kr11_HD." + output_format 

createBoxPlot( diff_kr11_rea_merano,  "Time $[month]$", "Prec. bias $[mm/month]$",     output_path_hd, output_format=output_format, my_dpi=600 )


# In[ ]:




