from lib import *

## model discharge - kriging 1x1 ##
### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

model_flow_kriging_11_calibration, model_precipitation_calibration, model_temperature, \
        obs_flow_calibration, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

model_flow_kriging_11_validation, model_precipitation_validation, model_temperature, \
        obs_flow_validation, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################

calibration_validation_data_kriging_11 = pd.concat( \
    [model_flow_kriging_11_calibration, model_flow_kriging_11_validation] )
calibration_validation_data_obs = pd.concat( \
    [obs_flow_calibration, obs_flow_validation] )

plots = []

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plots.append( (calibration_validation_data_kriging_11, plt_conf) )

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plots.append( (calibration_validation_data_obs, plt_conf) )

# define and add to plot the vertical line between calibration and validation #
last_date_cal = model_flow_kriging_11_calibration.index[-1]
first_date_val = model_flow_kriging_11_validation.index[0]

max_h = max( np.concatenate((model_flow_kriging_11_calibration.values, \
    model_flow_kriging_11_validation.values, obs_flow_calibration.values, obs_flow_validation.values, \
    calibration_validation_data_obs.values)) )
vertical_line = np.array( [0, max_h] )
vertical_line_DF = pd.DataFrame(data=vertical_line, index=[last_date_cal, first_date_val])

plt_conf = {}
plt_conf["linestyle"] = "--"
plots.append( (vertical_line_DF, plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile_hd = current.config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_merano\\" \
    + "model_passirio_merano_merano_hydrograph_kr11_obs_hd." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

outfile = current.config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_merano\\" \
    + "model_passirio_merano_merano_hydrograph_kr11_obs." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )

########################

from datetime import datetime
start_date_str = "2015-10-01T01:00:00"
end_date_str = "2016-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

plots = []

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plots.append( (calibration_validation_data_kriging_11[start_date:end_date], plt_conf) )

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plots.append( (calibration_validation_data_obs[start_date:end_date], plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile_hd = current.config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_merano\\" \
    + "model_passirio_merano_merano_hydrograph_kr11_obs_20152016_hd." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

outfile = current.config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_merano\\" \
    + "model_passirio_merano_merano_hydrograph_kr11_20152016_obs." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )

########################

from datetime import datetime
start_date_str = "2016-10-01T01:00:00"
end_date_str = "2017-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

plots = []

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plots.append( (calibration_validation_data_kriging_11[start_date:end_date], plt_conf) )

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plots.append( (calibration_validation_data_obs[start_date:end_date], plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile_hd = current.config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_merano\\" \
    + "model_passirio_merano_merano_hydrograph_kr11_obs_20162017_hd." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

outfile = current.config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_merano\\" \
    + "model_passirio_merano_merano_hydrograph_kr11_20162017_obs." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )