# ##### simulated precipitation - from the output directory -

# from lib import *

# ## model discharge - kriging 1x1 ##
# ### simulation selection #############################################################################

# current_phase = "calibration_best_merano"
# current_basin = "passirio"
# current_type = "kriging"
# current_node = "merano"

# model_flow_kr_calibration, model_precipitation_calibration, \
#     model_temperature, obs_flow_calibration, obs_temperature, \
#         model_snow_we, model_snow_we_plan \
#             = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

# ### end simulation selection ##########################################################################
# ### simulation selection #############################################################################

# current_phase = "validation_best_merano"
# current_basin = "passirio"
# current_type = "kriging"
# current_node = "merano"

# model_flow_kr_validation, model_precipitation_validation, \
#     model_temperature, obs_flow_validation, obs_temperature, \
#         model_snow_we, model_snow_we_plan \
#             = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

# ### end simulation selection ##########################################################################

# calibration_validation_data_kriging = pd.concat( \
#     [model_flow_kr_calibration, model_flow_kr_validation] )
# calibration_validation_data_obs = pd.concat( \
#     [obs_flow_calibration, obs_flow_validation] )

# plots = []

# ### kriging plot ###
# plt_conf = {}
# plt_conf["label"] = 'Kriging 1x1 dataset'
# plots.append( (calibration_validation_data_kriging, plt_conf) )

# ### obs plot ###
# plt_conf = {}
# plt_conf["label"] = 'Observed dataset'
# plots.append( (calibration_validation_data_obs, plt_conf) )

# # define and add to plot the vertical line between calibration and validation #
# last_date_cal = model_flow_kr_calibration.index[-1]
# first_date_val = model_flow_kr_validation.index[0]
# vertical_line = np.array( [0, \
#     max( pd.concat( [calibration_validation_data_kriging, calibration_validation_data_obs] ) )] )
# vertical_line_DF = pd.DataFrame(data=vertical_line, index=[last_date_cal, first_date_val])

# plt_conf = {}
# plt_conf["linestyle"] = "--"
# plots.append( (vertical_line_DF, plt_conf) )

# import matplotlib.dates as mdates
# x_major_locator=mdates.YearLocator(month=10, day=1)
# x_major_formatter=mdates.DateFormatter('%Y-%m')

# outfile_hd = config["output_path"] + "hydrograph_kriging_obs_merano_merano_hd." + output_format
# createPlot( plots, "Time $[hour]$", "Stream flow $[m^3/hour]$", outfile_hd, \
#     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

# outfile = config["output_path"] + "hydrograph_kriging_obs_merano_merano." + output_format
# createPlot( plots, "Time $[hour]$", "Stream flow $[m^3/hour]$", outfile, \
#     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )

# ### precipitation plot ###

# calibration_validation_model_precipitation = pd.concat( \
#     [model_precipitation_calibration, model_precipitation_validation] )

# plots = []

# plt_conf = {}
# #plt_conf["label"] = 'Precipitation [$mm/hour$]'
# plots.append( (calibration_validation_model_precipitation, plt_conf) )

# # define and add to plot the vertical line between calibration and validation #
# last_date_cal = model_flow_kr_calibration.index[-1]
# first_date_val = model_flow_kr_validation.index[0]
# vertical_line = np.array( [0, \
#     max( calibration_validation_model_precipitation )] )
# vertical_line_DF = pd.DataFrame(data=vertical_line, index=[last_date_cal, first_date_val])

# plt_conf = {}
# plt_conf["linestyle"] = "--"
# plots.append( (vertical_line_DF, plt_conf) )

# import matplotlib.dates as mdates
# x_major_locator=mdates.YearLocator(month=10, day=1)
# x_major_formatter=mdates.DateFormatter('%Y-%m')

# outfile_hd = config["output_path"] + "precipitation_kriging_merano_merano_hd." + output_format
# createPlot( plots, "Time $[hour]$", 'Precipitation [$mm/hour$]', outfile_hd, \
#     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

# outfile = config["output_path"] + "precipitation_kriging_merano_merano." + output_format
# createPlot( plots, "Time $[hour]$", 'Precipitation [$mm/hour$]', outfile, \
#     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )