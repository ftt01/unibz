from lib import *

## Boxplot bias kriging - reanalysis
### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
        obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated( configPath, \
            current_phase, current_basin, current_type, current_node )

### end simulation selection ##########################################################################
data_kr_daily_mean = model_flow.resample('MS').mean()

### simulation selection #############################################################################

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
        obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, sca_passirio, \
            swe1, swe2, swe3, swe4, swe5 = retrieveSimulated( configPath, \
            current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_rea_daily_mean = model_flow.resample('MS').mean()

data_daily_mean = data_kr_daily_mean - data_rea_daily_mean

#######################################################################################################
import matplotlib.ticker as ticker
x_major_locator=ticker.MultipleLocator(1)
x_labels = range(1,13)
x_major_formatter=ticker.FuncFormatter(lambda x, _: \
    dict(zip(range(len(x_labels)), x_labels)).get(x, ""))

output_path = config["output_path"] + "model\\passirio\\streamflow\\monthly\\" \
    + "model_passirio_merano_boxplot_streamflow_bias_kr-rea." + output_format 

createBoxPlot( data_daily_mean,  "Time $[month]$", "Streamflow bias $[m^3/month]$", \
    output_path, x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, \
        output_format=output_format, my_dpi=50 )

output_path_hd = config["output_path"] + "model\\passirio\\streamflow\\monthly\\" \
    + "model_passirio_merano_boxplot_streamflow_bias_kr-rea_hd." + output_format 

createBoxPlot( data_daily_mean,  "Time $[month]$", "Streamflow bias $[m^3/month]$", \
    output_path_hd, x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, \
        output_format=output_format, my_dpi=600)