from lib import *

### ECDF #############################################################################################

######################################################################################################
## model streamflow ECDF - kriging ################################################################
plots = []
### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

model_flow_cal, model_precipitation, \
    model_temperature, obs_flow_cal, obs_temperature, \
        model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, \
            current_phase, current_basin, current_type, current_node)

### end simulation selection #########################################################################
### simulation selection #############################################################################

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

model_flow_val, model_precipitation, \
    model_temperature, obs_flow_val, obs_temperature, \
        model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, \
            current_phase, current_basin, current_type, current_node)

### end simulation selection #########################################################################

model_flow = pd.concat( [model_flow_cal, model_flow_val] )

ecdf_model_flow_daily_mean = evaluateECDF( model_flow.resample('D').mean() )

plt_conf = {}
plt_conf["label"] = "Kriging 1x1"
plots.append( (ecdf_model_flow_daily_mean, plt_conf) )

## model streamflow ECDF - observed ##
obs_flow = pd.concat( [obs_flow_cal, obs_flow_val] )
ecdf_obs_flow_daily_mean = evaluateECDF( obs_flow.resample('D').mean() )

plt_conf = {}
plt_conf["label"] = "Observed"
plots.append( (ecdf_obs_flow_daily_mean, plt_conf) )

## model streamflow ECDF - reanalysis ##
### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

model_flow_cal, model_precipitation, \
    model_temperature, obs_flow, obs_temperature, \
        model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, \
            current_phase, current_basin, current_type, current_node)

### end simulation selection #########################################################################
### simulation selection #############################################################################

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

model_flow_val, model_precipitation, \
    model_temperature, obs_flow, obs_temperature, \
        model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, \
            current_phase, current_basin, current_type, current_node)

### end simulation selection #########################################################################

model_flow = pd.concat( [model_flow_cal, model_flow_val] )

ecdf_model_flow_daily_mean = evaluateECDF( model_flow.resample('D').mean() )

plt_conf = {}
plt_conf["label"] = "Reanalysis 11x8"
plots.append( (ecdf_model_flow_daily_mean, plt_conf) )

## model streamflow ECDF - kriging 11x8 ##
### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

model_flow_cal, model_precipitation, \
    model_temperature, obs_flow, obs_temperature, \
        model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, \
            current_phase, current_basin, current_type, current_node)

### end simulation selection #########################################################################
### simulation selection #############################################################################

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

model_flow_val, model_precipitation, \
    model_temperature, obs_flow, obs_temperature, \
        model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, \
            current_phase, current_basin, current_type, current_node)

### end simulation selection #########################################################################

model_flow = pd.concat( [model_flow_cal, model_flow_val] )

ecdf_model_flow_daily_mean = evaluateECDF( model_flow.resample('D').mean() )

plt_conf = {}
plt_conf["label"] = "Kriging 11x8"
plots.append( (ecdf_model_flow_daily_mean, plt_conf) )

######################################################################################################

kr_rea_output_file = config["output_path"] + "model\\passirio\\streamflow\\monthly\\" \
    + "model_passirio_merano_ECDF_streamflow_kr_rea_kr11_obs." + output_format
createPlot(plots,  "Streamflow $[m^3/day]$", "ECDF",
           kr_rea_output_file, output_format=output_format, my_dpi=50)

kr_rea_output_file_log = config["output_path"] + "model\\passirio\\streamflow\\monthly\\" \
    + "model_passirio_merano_ECDF_streamflow_kr_rea_kr11_obs_log." + output_format
createPlot(plots,  "Streamflow $[m^3/day]$", "ECDF",
           kr_rea_output_file_log, output_format=output_format, xscale='log', my_dpi=50)

kr_rea_output_file_hd = config["output_path"] + "model\\passirio\\streamflow\\monthly\\" \
    + "model_passirio_merano_ECDF_streamflow_kr_rea_kr11_obs_hd." + output_format
createPlot(plots,  "Streamflow $[m^3/day]$", "ECDF",
           kr_rea_output_file_hd, output_format=output_format, my_dpi=600)

kr_rea_output_file_log_hd = config["output_path"] + "model\\passirio\\streamflow\\monthly\\" \
    + "model_passirio_merano_ECDF_streamflow_kr_rea_kr11_obs_hd_log." + output_format
createPlot(plots,  "Streamflow $[m^3/day]$", "ECDF",
           kr_rea_output_file_log_hd, output_format=output_format, xscale='log', my_dpi=600)