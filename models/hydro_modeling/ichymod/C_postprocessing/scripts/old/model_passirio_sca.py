from pandas import read_csv
from lib import *

## OBSERVED ##
fileName_obs = "D:\\projects\\era5_bias\\calibration_validation\\hydro_modelling\\Passirio\\meteo\\MODIS_SCA.txt"

df_obs = read_csv(fileName_obs, header=0, index_col=0, parse_dates=True, delimiter=r"\s+")
df_obs_series = df_obs['SCA']

### simulation selection #############################################################################

current_phase = "best_merano_cal_val"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, model_sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
model_sca_passirio_mean_kr = model_sca_passirio.resample('D').mean()
model_sca_passirio_mean_kr = model_sca_passirio_mean_kr * 100

### simulation selection #############################################################################

current_phase = "best_merano_cal_val"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, model_sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
model_sca_passirio_mean_rea = model_sca_passirio.resample('D').mean()
model_sca_passirio_mean_rea = model_sca_passirio_mean_rea * 100

### simulation selection #############################################################################

current_phase = "best_merano_cal_val"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, model_sca_passirio, \
    swe1, swe2, swe3, swe4, swe5 = retrieveSimulated(configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
model_sca_passirio_mean_kr11 = model_sca_passirio.resample('D').mean()
model_sca_passirio_mean_kr11 = model_sca_passirio_mean_kr11 * 100

fig, axs = instantiatePlot("Time $[days]$", "SCA $[-]$", output_format='png')

axs.scatter(df_obs_series.index, df_obs_series.values, s=10, label='observed', color='orange')
            
axs.plot(model_sca_passirio_mean_kr, label='kriging', linestyle="solid", color='#8078bc')
axs.plot(model_sca_passirio_mean_kr11, label='kriging11x8', linestyle="solid", color='#fdb863')
axs.plot(model_sca_passirio_mean_rea, label='reanalysis', linestyle="solid", color='#e66101')

axs.legend(loc='lower right')

output_file = config["output_path"] + "model\\passirio\\sca\\daily\\" + "model_passirio_sca_daily." + output_format

mkNestedDir(getPathFromFilepath(output_file))
fig.savefig(output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50)

output_file_hd = config["output_path"] + "model\\passirio\\sca\\daily\\" + "model_passirio_sca_daily_hd." + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig(output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600)

########################################

from datetime import datetime
start_date_str = "2017-10-01T01:00:00"
end_date_str = "2018-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

fig, axs = instantiatePlot("Time $[days]$", "SCA $[-]$", output_format='png')

axs.scatter(df_obs_series[start_date:end_date].index, df_obs_series[start_date:end_date].values, s=10, label='observed', color='orange')
            
axs.plot(model_sca_passirio_mean_kr[start_date:end_date], label='kriging', linestyle="solid", color='#8078bc')
axs.plot(model_sca_passirio_mean_kr11[start_date:end_date], label='kriging11x8', linestyle="solid", color='#fdb863')
axs.plot(model_sca_passirio_mean_rea[start_date:end_date], label='reanalysis', linestyle="solid", color='#e66101')

axs.legend(loc='lower right')

output_file = config["output_path"] + "model\\passirio\\sca\\daily\\" + "model_passirio_sca_daily_20172018." + output_format

mkNestedDir(getPathFromFilepath(output_file))
fig.savefig(output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50)

output_file_hd = config["output_path"] + "model\\passirio\\sca\\daily\\" + "model_passirio_sca_daily__20172018_hd." + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig(output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600)

#########################

start_date_str = "2015-10-01T01:00:00"
end_date_str = "2016-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

fig, axs = instantiatePlot("Time $[days]$", "SCA $[-]$", output_format='png')

axs.scatter(df_obs_series[start_date:end_date].index, df_obs_series[start_date:end_date].values, s=10, label='observed', color='orange')
            
axs.plot(model_sca_passirio_mean_kr[start_date:end_date], label='kriging', linestyle="solid", color='#8078bc')
axs.plot(model_sca_passirio_mean_kr11[start_date:end_date], label='kriging11x8', linestyle="solid", color='#fdb863')
axs.plot(model_sca_passirio_mean_rea[start_date:end_date], label='reanalysis', linestyle="solid", color='#e66101')

axs.legend(loc='lower right')

output_file = config["output_path"] + "model\\passirio\\sca\\daily\\" + "model_passirio_sca_daily_20152016." + output_format

mkNestedDir(getPathFromFilepath(output_file))
fig.savefig(output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50)

output_file_hd = config["output_path"] + "model\\passirio\\sca\\daily\\" + "model_passirio_sca_daily__20152016_hd." + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig(output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600)
