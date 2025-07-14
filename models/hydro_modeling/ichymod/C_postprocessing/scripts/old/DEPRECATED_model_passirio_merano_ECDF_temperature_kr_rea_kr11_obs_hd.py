# from lib import *

# ### ECDF #############################################################################################

# ######################################################################################################
# ## model temperature ECDF - kriging ################################################################
# plots = []
# ### simulation selection #############################################################################

# current_phase = "calibration_best_merano"
# current_basin = "passirio"
# current_type = "kriging"
# current_node = "merano"

# model_flow, model_precipitation, \
#     model_temperature, obs_flow, obs_temperature = retrieveSimulated(configPath, \
#         current_phase, current_basin, current_type, current_node)

# ### end simulation selection #########################################################################

# ecdf_model_temperature_kr_daily_mean = evaluateECDF( model_temperature.resample('D').mean() )

# plt_conf = {}
# plt_conf["label"] = "Kriging 1x1"
# plots.append( (ecdf_model_temperature_kr_daily_mean, plt_conf) )

# ## model temperature ECDF - reanalysis ##
# ### simulation selection #############################################################################

# current_phase = "calibration_best_merano"
# current_basin = "passirio"
# current_type = "reanalysis"
# current_node = "merano"

# model_flow, model_precipitation, \
#     model_temperature, obs_flow, obs_temperature = retrieveSimulated(configPath, \
#         current_phase, current_basin, current_type, current_node)

# ### end simulation selection #########################################################################

# ecdf_model_temperature_rea_daily_mean = evaluateECDF( model_temperature.resample('D').mean() )

# plt_conf = {}
# plt_conf["label"] = "Reanalysis 11x8"
# plots.append( (ecdf_model_temperature_rea_daily_mean, plt_conf) )

# kr_rea_output_file = config["output_path"] + \
#     "ECDF_model_temperature_kr_rea_comparison." + output_format
# createPlot(plots,  "Temperature $[\degree C]$", "ECDF",
#            kr_rea_output_file, output_format=output_format, my_dpi=50)

# kr_rea_output_file_log = config["output_path"] + \
#     "ECDF_model_temperature_kr_rea_comparison_log." + output_format
# createPlot(plots,  "Temperature $[\degree C]$", "ECDF",
#            kr_rea_output_file_log, output_format=output_format, xscale='log', my_dpi=50)

# kr_rea_output_file_hd = config["output_path"] + \
#     "ECDF_model_temperature_kr_rea_comparison_hd." + output_format
# createPlot(plots,  "Temperature $[\degree C]$", "ECDF",
#            kr_rea_output_file_hd, output_format=output_format, my_dpi=600)

# kr_rea_output_file_log_hd = config["output_path"] + \
#     "ECDF_model_temperature_kr_rea_comparison_log_hd." + output_format
# createPlot(plots,  "Temperature $[\degree C]$", "ECDF",
#            kr_rea_output_file_log_hd, output_format=output_format, xscale='log', my_dpi=600)