from lib import *

# Boxplot bias kriging - reanalysis
### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, \
    sca_passirio, swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(
        configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_kr11_daily_mean = model_flow.resample('MS').mean()

### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, \
    sca_passirio, swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(
        configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_kr_daily_mean = model_flow.resample('MS').mean()

data_daily_mean = data_kr_daily_mean - data_kr11_daily_mean

#######################################################################################################
output_path = config["output_path"] + "model\\passirio\\streamflow\\monthly\\" \
    + "model_passirio_merano_boxplot_streamflow_bias_kr-kr11." + output_format

createBoxPlot(data_daily_mean,  "Time $[month]$", "Streamflow bias $[m^3/month]$",
              output_path, period='MS', output_format=output_format, my_dpi=50)

output_path_hd = config["output_path"] + "model\\passirio\\streamflow\\monthly\\" \
    + "model_passirio_merano_boxplot_streamflow_bias_kr-kr11_hd." + output_format

createBoxPlot(data_daily_mean,  "Time $[month]$", "Streamflow bias $[m^3/month]$",
              output_path_hd, period='MS', output_format=output_format, my_dpi=600)
