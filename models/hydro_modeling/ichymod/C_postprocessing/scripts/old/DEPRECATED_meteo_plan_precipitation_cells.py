from lib import *

basin = "Plan"

## KRIGING DATASET ##
# fileName_kr = "D:\\projects\\era5_bias\\02_calibration_validation\\hydro_modelling\\Passirio\\meteo\\kriging\\observations\\1x1\\temperature.txt"

## REANALYSIS DATASET ##
fileName_rea_129 = "D:\\projects\\era5_bias\\02_calibration_validation\\hydro_modelling\\Passirio\\meteo\\reanalysis\\observations\\precipitation\\129.csv"
fileName_rea_153 = "D:\\projects\\era5_bias\\02_calibration_validation\\hydro_modelling\\Passirio\\meteo\\reanalysis\\observations\\precipitation\\153.csv"

## KRIGING 11X8 DATASET ##
fileName_kr11_129 = "D:\\projects\\era5_bias\\02_calibration_validation\\hydro_modelling\\Passirio\\meteo\\kriging\\observations\\11x8\\precipitation\\129.csv"
fileName_kr11_153 = "D:\\projects\\era5_bias\\02_calibration_validation\\hydro_modelling\\Passirio\\meteo\\kriging\\observations\\11x8\\precipitation\\153.csv"

from pandas import read_csv
df_rea_129 = read_csv(fileName_rea_129, header=0, index_col=0, \
    skiprows=4, parse_dates=True, names=['values'])

df_rea_153 = read_csv(fileName_rea_153, header=0, index_col=0, \
    skiprows=4, parse_dates=True, names=['values'])

df_kr11_129 = read_csv(fileName_kr11_129, header=0, index_col=0, \
    skiprows=4, parse_dates=True, names=['values'])

df_kr11_153 = read_csv(fileName_kr11_153, header=0, index_col=0, \
    skiprows=4, parse_dates=True, names=['values'])

precipitation_rea_129_sum = df_rea_129.resample('MS').sum()
precipitation_rea_153_sum = df_rea_153.resample('MS').sum()

precipitation_kr11_129_sum = df_kr11_129.resample('MS').sum()
precipitation_kr11_153_sum = df_kr11_153.resample('MS').sum()

precipitation_rea_mean = (precipitation_rea_129_sum + precipitation_rea_153_sum) / 2
precipitation_kr11_mean = (precipitation_kr11_129_sum + precipitation_kr11_153_sum) / 2

plots = []

plt_conf = {}
plt_conf["label"] = 'Reanalysis 11x8'
plots.append( (precipitation_rea_mean, plt_conf) )

plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plots.append( (precipitation_kr11_mean, plt_conf) )

outfile = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\" \
    + "meteo_" + basin + "_precipitation_cells_rea11_kr11." + output_format
createPlot( plots, "Time $[month]$", 'Precipitation $[mm/month]$', outfile, my_dpi=50 )

outfile_hd = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\" \
    + "meteo_" + basin + "_precipitation_cells_rea11_kr11_hd." + output_format
createPlot( plots, "Time $[month]$", 'Precipitation $[mm/month]$', outfile_hd, my_dpi=600 )

#######################################################################################################

precipitation_bias_kr11_rea11 = precipitation_kr11_mean['values'] - precipitation_rea_mean['values']

output_path = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\" \
    + "meteo_" + basin + "_precipitation_cells_boxplot_kr11-rea11." + output_format 

createBoxPlot( precipitation_bias_kr11_rea11,  "Time $[month]$", 'Prec. bias $[mm/month]$', \
    output_path, period='MS', output_format=output_format, my_dpi=50 )

output_path_hd = config["output_path"] + "meteo\\" + basin + "\\precipitation\\monthly\\" \
    + "meteo_" + basin + "_precipitation_cells_boxplot_kr11-rea11_hd." + output_format 

createBoxPlot( precipitation_bias_kr11_rea11,  "Time $[month]$", 'Prec. bias $[mm/month]$', \
    output_path_hd, period='MS', output_format=output_format, my_dpi=600)