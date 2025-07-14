from lib import *

## model discharge - kriging 1x1 ##
### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

model_flow_kr_calibration, model_precipitation_calibration, model_temperature, \
        obs_flow_calibration, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "plan"

model_flow_kr_validation, model_precipitation_validation, model_temperature, \
        obs_flow_validation, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################

calibration_validation_data_kriging = pd.concat( \
    [model_flow_kr_calibration, model_flow_kr_validation] )
calibration_validation_data_obs = pd.concat( \
    [obs_flow_calibration, obs_flow_validation] )

plots = []

### kriging plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 1x1'
plots.append( (calibration_validation_data_kriging, plt_conf) )

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plots.append( (calibration_validation_data_obs, plt_conf) )

# define and add to plot the vertical line between calibration and validation #
last_date_cal = model_flow_kr_calibration.index[-1]
first_date_val = model_flow_kr_validation.index[0]

max_h = max( np.concatenate((model_flow_kr_calibration.values, \
    model_flow_kr_validation.values, obs_flow_calibration.values, obs_flow_validation.values, \
    calibration_validation_data_obs.values)) )
vertical_line = np.array( [0, max_h] )
vertical_line_DF = pd.DataFrame(data=vertical_line, index=[last_date_cal, first_date_val])

plt_conf = {}
plt_conf["linestyle"] = "--"
plots.append( (vertical_line_DF, plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

# outfile = config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_plan\\" \
#     + "model_passirio_merano_plan_hydrograph_kriging_obs." + output_format
# createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, height=80, \
#     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50 )

# outfile_hd = config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_plan\\" \
#     + "model_passirio_merano_plan_hydrograph_kriging_obs_hd." + output_format
# createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, height=80, \
#     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600 )

# ### ONLY CALIBRATION ###

# plots = []

# ### kriging plot ###
# plt_conf = {}
# plt_conf["label"] = 'Kriging 1x1'
# plots.append( (model_flow_kr_calibration, plt_conf) )

# ### obs plot ###
# plt_conf = {}
# plt_conf["label"] = 'Observed'
# plots.append( (obs_flow_calibration, plt_conf) )

# outfile = config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_plan\\" \
#     + "model_passirio_merano_plan_hydrograph_kriging_obs_calibration." + output_format
# createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, width=120, height=80, \
#     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50 )

# outfile_hd = config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_plan\\" \
#     + "model_passirio_merano_plan_hydrograph_kriging_obs_calibration_hd." + output_format
# createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, width=120, height=80, \
#     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600 )


### ONLY VALIDATION ###

plots = []

### kriging plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 1x1'
plots.append( (model_flow_kr_validation, plt_conf) )

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plots.append( (obs_flow_validation, plt_conf) )

outfile = config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_plan\\" \
    + "model_passirio_merano_plan_hydrograph_kriging_obs_validation." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, width=150, height=80, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50 )

outfile_hd = config["output_path"] + "model\\passirio\\streamflow\\hourly\\merano_plan\\" \
    + "model_passirio_merano_plan_hydrograph_kriging_obs_validation_hd." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, width=150, height=80, \
    x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600 )