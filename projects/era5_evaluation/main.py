import subprocess

repo_dir = "/home/daniele/documents/github/ftt01/phd/projects/era5_evaluation/"

### METEO ####
## AA ##
print('>>>>> EXECUTING meteo_AA_weather_stations.py')
subprocess.call(['python3', "{repo_path}bin/meteo/alto_adige/meteo_AA_weather_stations.py".format(repo_path=repo_dir)])
# precipitation #
print('>>>>> EXECUTING meteo_AA_precipitation_cells.py')
subprocess.call(['python3', "{repo_path}bin/meteo/alto_adige/precipitation/meteo_AA_precipitation_cells.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING meteo_AA_precipitation_lapserate.py')
subprocess.call(['python3', "{repo_path}bin/meteo/alto_adige/precipitation/meteo_AA_precipitation_lapserate.py".format(repo_path=repo_dir)])
# temperature #
print('>>>>> EXECUTING meteo_AA_temperature_cells.py')
subprocess.call(['python3', "{repo_path}bin/meteo/alto_adige/temperature/meteo_AA_temperature_cells.py".format(repo_path=repo_dir)])

## PASSIRIO ##
# precipitation #
print('>>>>> EXECUTING meteo_passirio_precipitation_cells.py')
subprocess.call(['python3', "{repo_path}bin/meteo/passirio/precipitation/meteo_passirio_precipitation_cells.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING meteo_passirio_precipitation_lapserate.py')
subprocess.call(['python3', "{repo_path}bin/meteo/passirio/precipitation/meteo_passirio_precipitation_lapserate.py".format(repo_path=repo_dir)])
# temperature #
print('>>>>> EXECUTING meteo_passirio_temperature_cells.py')
subprocess.call(['python3', "{repo_path}bin/meteo/passirio/temperature/meteo_passirio_temperature_cells.py".format(repo_path=repo_dir)])

## PLAN ##
# precipitation #
# print('>>>>> EXECUTING meteo_plan_precipitation_cells.py')
# subprocess.call(['python3', "{repo_path}bin/precipitation/meteo_plan_precipitation_cells.py".format(repo_path=repo_dir)])
# temperature
# print('>>>>> EXECUTING meteo_plan_temperature_cells.py')
# subprocess.call(['python3', "{repo_path}bin/temperature/meteo_plan_temperature_cells.py".format(repo_path=repo_dir)])

### MODEL ###
## PASSIRIO ##
# precipitation #
print('>>>>> EXECUTING model_passirio_precipitation.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/precipitation/model_passirio_precipitation.py".format(repo_path=repo_dir)])
# temperature #
print('>>>>> EXECUTING model_passirio_temperature.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/temperature/model_passirio_temperature.py".format(repo_path=repo_dir)])
# streamflow #
print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_kr_kr11_rea_obs.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/streamflow/model_passirio_merano_merano_hydrograph_kr_kr11_rea_obs.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING model_passirio_merano_merano_qqplot_kr_kr11_rea_obs.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/streamflow/model_passirio_merano_merano_qqplot_kr_kr11_rea_obs.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_kr_kr11_rea_obs_insection.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/streamflow/model_passirio_merano_merano_hydrograph_kr_kr11_rea_obs_insection.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING model_passirio_merano_plan_hydrograph_kr_kr11_rea_obs.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/streamflow/model_passirio_merano_plan_hydrograph_kr_kr11_rea_obs.py".format(repo_path=repo_dir)])
# snow #
print('>>>>> EXECUTING model_passirio_swe.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/snow/model_passirio_swe.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING model_passirio_sca.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/snow/model_passirio_sca.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING model_swe_local.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/snow/model_swe_local.py".format(repo_path=repo_dir)])

## PLAN
# print('>>>>> EXECUTING model_plan_precipitation.py')
# subprocess.call(['python3', "{repo_path}bin/precipitation/model_plan_precipitation.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_kr_kr11_rea_obs.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/streamflow/model_passirio_plan_plan_hydrograph_kr_kr11_rea_obs.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_kr_kr11_rea_obs.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/streamflow/model_passirio_plan_plan_hydrograph_kr_kr11_rea_obs.py".format(repo_path=repo_dir)])
print('>>>>> EXECUTING model_passirio_plan_plan_qqplot_kr_kr11_rea_obs.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/streamflow/model_passirio_plan_plan_qqplot_kr_kr11_rea_obs.py".format(repo_path=repo_dir)])
# snow #
print('>>>>> EXECUTING model_plan_swe.py')
subprocess.call(['python3', "{repo_path}bin/model/passirio/snow/model_plan_swe.py".format(repo_path=repo_dir)])

#############################

# print('>>>>> EXECUTING model_passirio_merano_boxplot_streamflow_bias_kr11-kr.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_boxplot_streamflow_bias_kr11-kr.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_merano_boxplot_streamflow_bias_rea-kr.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_boxplot_streamflow_bias_rea-kr.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_merano_boxplot_streamflow_bias_rea-kr11.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_boxplot_streamflow_bias_rea-kr11.py".format(repo_path=repo_dir)])

# print('>>>>> EXECUTING model_passirio_merano_ECDF_streamflow_kr_kr11_rea_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_ECDF_streamflow_kr_kr11_rea_obs.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_merano_ECDF_streamflow_kr_kr11_rea_obs_insected.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_ECDF_streamflow_kr_kr11_rea_obs_insected.py".format(repo_path=repo_dir)])

# print('>>>>> EXECUTING model_passirio_plan_boxplot_streamflow_bias_rea-kr11.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_plan_boxplot_streamflow_bias_rea-kr11.py".format(repo_path=repo_dir)])

# print('>>>>> EXECUTING model_passirio_plan_ECDF_streamflow_kr_kr11_rea_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_plan_ECDF_streamflow_kr_kr11_rea_obs.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_plan_ECDF_streamflow_kr_kr11_rea_obs_insected.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_pprint(output_dir)

# print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_kr11_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_merano_hydrograph_kr11_obs.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_kr_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_merano_hydrograph_kr_obs.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_rea_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_merano_hydrograph_rea_obs.py".format(repo_path=repo_dir)])

# print('>>>>> EXECUTING model_passirio_merano_plan_hydrograph_kr11_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_plan_hydrograph_kr11_obs.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_merano_plan_hydrograph_kr_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_plan_hydrograph_kr_obs.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_merano_plan_hydrograph_rea_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_merano_plan_hydrograph_rea_obs.py".format(repo_path=repo_dir)])

# print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_kr_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_plan_plan_hydrograph_kr_obs.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_kr11_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_plan_plan_hydrograph_kr11_obs.py".format(repo_path=repo_dir)])
# print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_rea_obs.py')
# subprocess.call(['python3', "{repo_path}bin/streamflow/model_passirio_plan_plan_hydrograph_rea_obs.py".format(repo_path=repo_dir)])
