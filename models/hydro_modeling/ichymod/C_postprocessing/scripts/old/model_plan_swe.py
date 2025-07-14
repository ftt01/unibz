from lib import *

# Boxplot bias kriging_11 - kriging
### simulation selection #############################################################################

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging"
current_node = "plan"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath,
                                                     current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_kr_plan_swe_mean = model_snow_we_plan.resample('MS').mean()

### simulation selection #############################################################################

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "plan"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath,
                                                     current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_kr11_plan_swe_mean = model_snow_we_plan.resample('MS').mean()

data_kr11_kr_plan_swe_mean_bias = data_kr_plan_swe_mean - data_kr11_plan_swe_mean

plt_conf = {}

outfile = config["output_path"] + "model\\plan\\swe\\monthly\\" \
    + "model_plan_boxplot_swe_kr-kr11." + output_format
createBoxPlot(data_kr11_kr_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile, output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile_hd = config["output_path"] + "model\\plan\\swe\\monthly\\" \
    + "model_plan_boxplot_swe_kr-kr11_hd." + output_format
createBoxPlot(data_kr11_kr_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile_hd, output_format=output_format, scale_factor=0.5, my_dpi=600)

# Boxplot bias kriging - reanalysis
### simulation selection #############################################################################

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, \
        current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_rea_plan_swe_mean = model_snow_we_plan.resample('MS').mean()

data_rea_kr_plan_swe_mean_bias = data_kr_plan_swe_mean - data_rea_plan_swe_mean

plt_conf = {}

outfile = config["output_path"] + "model\\plan\\swe\\monthly\\" \
    + "model_plan_boxplot_swe_kr-rea." + output_format
createBoxPlot(data_rea_kr_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile, output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile_hd = config["output_path"] + "model\\plan\\swe\\monthly\\" \
    + "model_plan_boxplot_swe_kr-rea_hd." + output_format
createBoxPlot(data_rea_kr_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile_hd,  output_format=output_format, scale_factor=0.5, my_dpi=600)


## SWE over time #####################################################################################
### simulation selection #############################################################################

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath,
                                                     current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
plots = []
plots.append((model_snow_we_plan, {"label": "Kriging 1x1"}))

### simulation selection #############################################################################

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "plan"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we_kr11, model_snow_we_plan, sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath,
                                                     current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
plots.append((model_snow_we_kr11, {"label": "Kriging 11x8"}))

### simulation selection #############################################################################

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath,
                                                     current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
plots.append((model_snow_we_plan, {"label": "Reanalysis 11x8"}))

outfile = config["output_path"] + "model\\plan\\swe\\hourly\\" \
    + "model_plan_swe_kr_rea." + output_format
createPlot(plots, "Time $[hour]$", 'SWE $[mm/hour]$', outfile,
           output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile = config["output_path"] + "model\\plan\\swe\\hourly\\" \
    + "model_plan_swe_kr_rea_hd." + output_format
createPlot(plots, "Time $[hour]$", 'SWE $[mm/hour]$', outfile,
           output_format=output_format, scale_factor=0.5, my_dpi=600)
