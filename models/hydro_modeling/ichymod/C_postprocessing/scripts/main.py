#!/usr/bin/env python
import subprocess

wdir = "/home/daniele/documents/github/ftt01/phd/models/hydro_modeling/ichymod/C_postprocessing/scripts/"

## METEO
print('>>>>> EXECUTING meteo_AA_precipitation_cells.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/precipitation/meteo_AA_precipitation_cells.py"])

print('>>>>> EXECUTING meteo_AA_precipitation_cells_elevation.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/precipitation/meteo_AA_precipitation_cells_elevation.py"])

print('>>>>> EXECUTING meteo_AA_temperature_cells.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/temperature/meteo_AA_temperature_cells.py"])  

print('>>>>> EXECUTING meteo_AA_temperature_cells_elevation.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/temperature/meteo_AA_temperature_cells_elevation.py"])  

print('>>>>> EXECUTING meteo_passirio_precipitation_cells.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/precipitation/meteo_passirio_precipitation_cells.py"])

print('>>>>> EXECUTING model_passirio_precipitation.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/precipitation/model_passirio_precipitation.py"])

print('>>>>> EXECUTING meteo_passirio_temperature_cells.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/temperature/meteo_passirio_temperature_cells.py"])

print('>>>>> EXECUTING model_passirio_temperature.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/temperature/model_passirio_temperature.py"])

print('>>>>> EXECUTING meteo_plan_precipitation_cells.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/precipitation/meteo_plan_precipitation_cells.py"])

print('>>>>> EXECUTING model_plan_precipitation.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/precipitation/model_plan_precipitation.py"])

print('>>>>> EXECUTING meteo_plan_temperature_cells.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/temperature/meteo_plan_temperature_cells.py"])

## HYDRO

print('>>>>> EXECUTING model_passirio_merano_boxplot_streamflow_bias_kr11-kr.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_boxplot_streamflow_bias_kr11-kr.py"])
print('>>>>> EXECUTING model_passirio_merano_boxplot_streamflow_bias_rea-kr.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_boxplot_streamflow_bias_rea-kr.py"])
print('>>>>> EXECUTING model_passirio_merano_boxplot_streamflow_bias_rea-kr11.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_boxplot_streamflow_bias_rea-kr11.py"])

print('>>>>> EXECUTING model_passirio_merano_ECDF_streamflow_kr_kr11_rea_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_ECDF_streamflow_kr_kr11_rea_obs.py"])
print('>>>>> EXECUTING model_passirio_merano_ECDF_streamflow_kr_kr11_rea_obs_insected.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_ECDF_streamflow_kr_kr11_rea_obs_insected.py"])

print('>>>>> EXECUTING model_passirio_plan_boxplot_streamflow_bias_rea-kr11.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_plan_boxplot_streamflow_bias_rea-kr11.py"])

print('>>>>> EXECUTING model_passirio_plan_ECDF_streamflow_kr_kr11_rea_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_plan_ECDF_streamflow_kr_kr11_rea_obs.py"])
print('>>>>> EXECUTING model_passirio_plan_ECDF_streamflow_kr_kr11_rea_obs_insected.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_plan_ECDF_streamflow_kr_kr11_rea_obs_insected.py"])

print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_kr_kr11_rea_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_merano_hydrograph_kr_kr11_rea_obs.py"])
print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_kr_kr11_rea_obs_insection.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_merano_hydrograph_kr_kr11_rea_obs_insection.py"])

print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_kr11_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_merano_hydrograph_kr11_obs.py"])
print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_kr_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_merano_hydrograph_kr_obs.py"])
print('>>>>> EXECUTING model_passirio_merano_merano_hydrograph_rea_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_merano_hydrograph_rea_obs.py"])

print('>>>>> EXECUTING model_passirio_merano_plan_hydrograph_kr11_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_plan_hydrograph_kr11_obs.py"])
print('>>>>> EXECUTING model_passirio_merano_plan_hydrograph_kr_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_plan_hydrograph_kr_obs.py"])
print('>>>>> EXECUTING model_passirio_merano_plan_hydrograph_rea_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_merano_plan_hydrograph_rea_obs.py"])

print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_kr_kr11_rea_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_plan_plan_hydrograph_kr_kr11_rea_obs.py"])
print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_kr_kr11_rea_obs_insection.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_plan_plan_hydrograph_kr_kr11_rea_obs_insection.py"])

print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_kr_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_plan_plan_hydrograph_kr_obs.py"])
print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_kr11_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_plan_plan_hydrograph_kr11_obs.py"])
print('>>>>> EXECUTING model_passirio_plan_plan_hydrograph_rea_obs.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/streamflow/model_passirio_plan_plan_hydrograph_rea_obs.py"])

print('>>>>> EXECUTING model_passirio_swe.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/snow/model_passirio_swe.py"])
print('>>>>> EXECUTING model_plan_swe.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/snow/model_plan_swe.py"])

print('>>>>> EXECUTING model_passirio_sca.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/snow/model_passirio_sca.py"])

print('>>>>> EXECUTING model_swe_local.py')
subprocess.call(['/usr/bin/python3', wdir + "bin/snow/model_swe_local.py"])