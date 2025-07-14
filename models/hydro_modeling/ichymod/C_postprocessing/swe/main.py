import subprocess

## METEO

print('executing meteo_comparisons.py')
subprocess.call(['python', "meteo_comparisons.py"])
print('executing meteo_AA_biases_over_elevation.py')
subprocess.call(['python', "meteo_AA_biases_over_elevation.py"])
print('executing meteo_AA_temperature_comparisons.py')
subprocess.call(['python', "meteo_AA_temperature_comparisons.py"])
print('executing meteo_passirio_precipitation.py')
subprocess.call(['python', "meteo_passirio_precipitation.py"])
print('executing meteo_plan_precipitation_cells.py')
subprocess.call(['python', "meteo_plan_precipitation_cells.py"])
print('executing meteo_plan_precipitation.py')
subprocess.call(['python', "meteo_plan_precipitation.py"])
print('executing meteo_plan_temperature.py')
subprocess.call(['python', "meteo_plan_temperature.py"])

## HYDRO

print('executing model_passirio_merano_boxplot_streamflow_bias_kr.py')
subprocess.call(['python', "model_passirio_merano_boxplot_streamflow_bias_kr-kr11.py"])
print('executing model_passirio_merano_boxplot_streamflow_bias_kr.py')
subprocess.call(['python', "model_passirio_merano_boxplot_streamflow_bias_kr-rea.py"])
print('executing model_passirio_merano_boxplot_streamflow_bias_kr11.py')
subprocess.call(['python', "model_passirio_merano_boxplot_streamflow_bias_kr11-rea.py"])

print('executing model_passirio_merano_ECDF_streamflow_kr_rea_kr11_obs.py')
subprocess.call(['python', "model_passirio_merano_ECDF_streamflow_kr_rea_kr11_obs.py"])

print('executing model_passirio_merano_merano_hydrograph_kr11_obs.py')
subprocess.call(['python', "model_passirio_merano_merano_hydrograph_kr11_obs.py"])
print('executing model_passirio_merano_merano_hydrograph_kriging_obs.py')
subprocess.call(['python', "model_passirio_merano_merano_hydrograph_kriging_obs.py"])
print('executing model_passirio_merano_merano_hydrograph_rea_obs.py')
subprocess.call(['python', "model_passirio_merano_merano_hydrograph_rea_obs.py"])

print('executing model_passirio_merano_plan_hydrograph_kr11_obs.py')
subprocess.call(['python', "model_passirio_merano_plan_hydrograph_kr11_obs.py"])
print('executing model_passirio_merano_plan_hydrograph_kriging_obs.py')
subprocess.call(['python', "model_passirio_merano_plan_hydrograph_kriging_obs.py"])
print('executing model_passirio_merano_plan_hydrograph_rea_obs.py')
subprocess.call(['python', "model_passirio_merano_plan_hydrograph_rea_obs.py"])

print('executing model_passirio_plan_plan_hydrograph_kriging_obs.py')
subprocess.call(['python', "model_passirio_plan_plan_hydrograph_kriging_obs.py"])
print('executing model_passirio_plan_plan_hydrograph_kriging11_obs.py')
subprocess.call(['python', "model_passirio_plan_plan_hydrograph_kriging11_obs.py"])
print('executing model_passirio_plan_plan_hydrograph_rea_obs.py')
subprocess.call(['python', "model_passirio_plan_plan_hydrograph_rea_obs.py"])

print('executing model_passirio_swe.py')
subprocess.call(['python', "model_passirio_swe.py"])
print('executing model_plan_swe.py')
subprocess.call(['python', "model_plan_swe.py"])

print('executing model_passirio_sca.py')
subprocess.call(['python', "model_passirio_sca.py"])