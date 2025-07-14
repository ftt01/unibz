from lib import *

from datetime import datetime
start_date_str = "2013-10-01T01:00:00"
end_date_str = "2020-09-30T23:00:00"
start_date = datetime.strptime( start_date_str, '%Y-%m-%dT%H:%M:%S' )
end_date = datetime.strptime( end_date_str, '%Y-%m-%dT%H:%M:%S' )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

## KRIGING DATASET ##
fileName_kr = "D:\\projects\\era5_bias\\calibration_validation\\hydro_modelling\\Passirio\\meteo\\kriging\\observations\\1x1\\precipitation.txt"
#fileName_kr = "D:\\projects\\era5_bias\\CALIBRAZIONE_PASSIRIO_REANALISYS\\hydro_modelling\\Passirio\\meteo\\kriging\\observations\\precipitation.txt"

## REANALYSIS DATASET ##
fileName_rea = "D:\\projects\\era5_bias\\calibration_validation\\hydro_modelling\\Passirio\\meteo\\reanalysis\\observations\\precipitation.txt"
#fileName_rea =  "D:\\projects\\era5_bias\\CALIBRAZIONE_PASSIRIO_REANALISYS\\hydro_modelling\\Passirio\\meteo\\reanalysis\\observations\\precipitation.txt"

## KRIGING 11X8 DATASET ##
fileName_kr11 = "D:\\projects\\era5_bias\\calibration_validation\\hydro_modelling\\Passirio\\meteo\\kriging\\observations\\11x8\\precipitation.txt"
#fileName_kr11 = "D:\\projects\\era5_bias\\CALIBRAZIONE_PASSIRIO_KRIGING_11x8\\hydro_modelling\\Passirio\\meteo\\kriging\\observations\\precipitation.txt"

## OBSERVED ##
#fileName_obs = "D:\\projects\\era5_bias\\calibration_validation\\hydro_modelling\\Passirio\\meteo\\GS\\observations\\precipitation.txt"

## BASINS ##
fileName_basins = "D:\\projects\\era5_bias\\calibration_validation\\hydro_modelling\\Passirio\\INPUT\\topological_elements\\basins.txt"

from pandas import read_csv
df_kr = read_csv(fileName_kr, header=0, index_col=0, parse_dates=True)
df_rea = read_csv(fileName_rea, header=0, index_col=0, parse_dates=True, delimiter=r"\s+")
df_rea = rewriteDF(df_rea)
df_rea = df_rea.sort_index()
df_kr11 = read_csv(fileName_kr11, header=0, index_col=0, parse_dates=True, delimiter=r"\s+")
df_kr11 = rewriteDF(df_kr11)
df_kr11 = df_kr11.sort_index()

df_basins = read_csv(fileName_basins, header=None, delimiter=r"\s+", index_col=0)

### PRECIPITATION PASSIRIO ###
basin = "Passirio"
current_basin = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,19,20,21,22,23]

precipitation_kr = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_kr = pd.concat([precipitation_kr, 
            df_kr[start_date:end_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_rea = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_rea = pd.concat([precipitation_rea, 
            df_rea[start_date:end_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_kr11 = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_kr11 = pd.concat([precipitation_kr11, 
            df_kr11[start_date:end_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_kr_passirio_sum = precipitation_kr.sum(axis=1)
precipitation_kr11_passirio_sum = precipitation_kr11.sum(axis=1)
precipitation_rea_passirio_sum = precipitation_rea.sum(axis=1)

precipitation_kr_passirio_monthly_mean = precipitation_kr_passirio_sum.resample('MS').sum()
precipitation_rea_passirio_monthly_mean = precipitation_rea_passirio_sum.resample('MS').sum()
precipitation_kr11_passirio_monthly_mean = precipitation_kr11_passirio_sum.resample('MS').sum()

plots = []

plt_conf = {}
plt_conf["label"] = 'Kriging'
plots.append( (precipitation_kr_passirio_monthly_mean, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'Reanalysis'
plots.append( (precipitation_rea_passirio_monthly_mean, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plots.append( (precipitation_kr11_passirio_monthly_mean, plt_conf) )

outfile = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\volumes\\" \
    + "meteo_" + basin + "_precipitation_kr_rea_kr11." + output_format
createPlot( plots, "Time $[month]$", 'Prec. [$mm/month$]', outfile, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )

outfile_hd = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\volumes\\" \
    + "meteo_" + basin + "_precipitation_kr_rea_kr11_hd." + output_format
createPlot( plots, "Time $[month]$", 'Prec. [$mm/month$]', outfile_hd, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

################################ PRECIPITATION HOURLY #####################################
############################# CALIBRATION + VALIDATION ####################################
plots = []

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

plt_conf = {}
plots.append( (precipitation_kr_passirio_sum, plt_conf) )

outfile = config["output_path"] + "meteo\\" + basin + "\\precipitation\\hourly\\volumes\\" \
    + "meteo_passirio_precipitation_hourly." + output_format
createPlot( plots, "Time $[hour]$", 'Precipitation $[mm/hour]$', outfile, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )
    
outfile_hd = config["output_path"] + "meteo\\" + basin + "\\precipitation\\hourly\\volumes\\" \
    + "meteo_passirio_precipitation_hourly_hd." + output_format
createPlot( plots, "Time $[hour]$", 'Precipitation $[mm/hour]$', outfile_hd, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

################################### ONLY VALIDATION #######################################
start_VAL_date_str = "2017-10-01T01:00:00"
end_VAL_date_str = "2020-09-30T23:00:00"
start_VAL_date = datetime.strptime( start_VAL_date_str, '%Y-%m-%dT%H:%M:%S' )
end_VAL_date = datetime.strptime( end_VAL_date_str, '%Y-%m-%dT%H:%M:%S' )

precipitation_VAL_kr = pd.DataFrame()
for basin_id in range(1,len(df_basins)+1):
    if basin_id in current_basin:
        precipitation_VAL_kr = pd.concat([precipitation_VAL_kr, 
            df_kr[start_VAL_date:end_VAL_date][str(basin_id)] * int(df_basins[basin_id-1:basin_id][2]) \
                / df_basins.loc[current_basin][2].sum(0)], axis=1)

precipitation_VAL_kr_passirio_sum = precipitation_VAL_kr.sum(axis=1)

plots = []

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

plt_conf = {}
plots.append( (precipitation_VAL_kr_passirio_sum, plt_conf) )

outfile = config["output_path"] + "meteo\\" + basin + "\\precipitation\\hourly\\volumes\\" \
    + "meteo_" + basin + "_precipitation_VAL_hourly." + output_format
createPlot( plots, "Time $[hour]$", 'Precipitation $[mm/hour]$', outfile, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )
    
outfile_hd = config["output_path"] + "meteo\\" + basin + "\\precipitation\\hourly\\volumes\\" \
    + "meteo_" + basin + "_precipitation_VAL_hourly_hd." + output_format
createPlot( plots, "Time $[hour]$", 'Precipitation $[mm/hour]$', outfile_hd, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

################################ BOXPLOT BIAS ###############################################
############################ reanalysis - kriging ###########################################
diff_rea_kr_passirio = precipitation_kr_passirio_monthly_mean - precipitation_rea_passirio_monthly_mean

output_path = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\volumes\\" \
    + "meteo_passirio_precipitation_boxplot_kr-rea." + output_format 

createBoxPlot( diff_rea_kr_passirio,  "Time $[month]$", "Prec. bias $[mm/month]$", \
    output_path, output_format=output_format, my_dpi=50 )

output_path_hd = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\volumes\\" \
    + "meteo_passirio_precipitation_boxplot_kr-rea_hd." + output_format 

createBoxPlot( diff_rea_kr_passirio,  "Time $[month]$", "Prec. bias $[mm/month]$", \
    output_path_hd, output_format=output_format, my_dpi=600 )

############################ kriging_11 - kriging ###########################################
diff_kr11_kr_merano = precipitation_kr_passirio_monthly_mean - precipitation_kr11_passirio_monthly_mean

output_path = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\volumes\\" \
    + "meteo_passirio_precipitation_boxplot_kr-kr11." + output_format 
createBoxPlot( diff_kr11_kr_merano,  "Time $[month]$", "Prec. bias $[mm/month]$", output_path, output_format=output_format, my_dpi=50 )

output_path_hd = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\volumes\\" \
    + "meteo_passirio_precipitation_boxplot_kr-kr11_hd." + output_format 
createBoxPlot( diff_kr11_kr_merano,  "Time $[month]$", "Prec. bias $[mm/month]$", output_path_hd, output_format=output_format, my_dpi=600 )

############################ kriging_11 - reanalysis ###########################################
diff_kr11_rea_merano = precipitation_kr11_passirio_monthly_mean - precipitation_rea_passirio_monthly_mean

output_path = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\volumes\\" \
    + "meteo_passirio_precipitation_boxplot_kr11-rea." + output_format 

createBoxPlot( diff_kr11_rea_merano,  "Time $[month]$", "Prec. bias $[mm/month]$", \
    output_path, output_format=output_format, my_dpi=50 )

output_path_hd = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\volumes\\" \
    + "meteo_passirio_precipitation_boxplot_kr11-rea_hd." + output_format 

createBoxPlot( diff_kr11_rea_merano,  "Time $[month]$", "Prec. bias $[mm/month]$", \
    output_path_hd, output_format=output_format, my_dpi=600 )