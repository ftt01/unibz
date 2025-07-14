#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# wdir = "C:/Users/daniele/Documents/GitHub/ftt01/phd/hydro_modeling/ichymod/C_postprocessing/scripts/"
wdir = "/home/daniele/documents/github/ftt01/phd/hydro_modeling/ichymod/C_postprocessing/scripts/"


# In[ ]:


import sys, os
# sys.path.insert( 0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(''))),'lib') )
# to link the lib in py scripts as well
os.chdir( wdir )
sys.path.insert( 0, os.path.join(os.path.abspath(os.getcwd()),'lib') )

from lib import *
current = DataCollector()


# In[ ]:


### simulation selection #############################################################################

kriging_data_calibration = DataCollector()

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

kriging_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

kriging_data_validation = DataCollector()

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

kriging_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
kriging_data = pd.concat( [kriging_data_calibration.model_flow, kriging_data_validation.model_flow] )

obs_data = pd.concat( [kriging_data_calibration.obs_flow, kriging_data_validation.obs_flow] )


# In[ ]:


### simulation selection #############################################################################

kriging_11_data_calibration = DataCollector()

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

kriging_11_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

kriging_11_data_validation = DataCollector()

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

kriging_11_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
kriging_11_data = pd.concat( [kriging_11_data_calibration.model_flow, kriging_11_data_validation.model_flow] )


# In[ ]:


### simulation selection #############################################################################

reanalysis_data_calibration = DataCollector()

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

reanalysis_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

reanalysis_data_validation = DataCollector()

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

reanalysis_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
reanalysis_data = pd.concat( [reanalysis_data_calibration.model_flow, reanalysis_data_validation.model_flow] )


# In[ ]:


kriging_data_daily_mean =  kriging_data.resample('D').mean()
ecdf_kriging_flow_daily_mean = evaluateECDF( kriging_data_daily_mean )

obs_data_daily_mean =  obs_data.resample('D').mean()
ecdf_obs_flow_daily_mean = evaluateECDF( obs_data_daily_mean )

kriging_11_data_daily_mean =  kriging_11_data.resample('D').mean()
ecdf_kriging_11_flow_daily_mean = evaluateECDF( kriging_11_data_daily_mean )

reanalysis_data_daily_mean =  reanalysis_data.resample('D').mean()
ecdf_reanalysis_flow_daily_mean = evaluateECDF( reanalysis_data_daily_mean )

plots = []

### rea 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Reanalysis 11x8'
plt_conf["color"] = '#e66101'
plots.append( (ecdf_reanalysis_flow_daily_mean, plt_conf) )

### kriging 1x1 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 1x1'
plt_conf["color"] = '#8078bc'
plots.append( (ecdf_kriging_flow_daily_mean, plt_conf) )

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plt_conf["color"] = '#5e3c99'
plots.append( (ecdf_kriging_11_flow_daily_mean, plt_conf) )

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plt_conf["color"] = '#fdb863'
plots.append( (ecdf_obs_flow_daily_mean, plt_conf) )


# In[ ]:


kr_rea_output_file = current.config["output_path"] + "model/streamflow/passirio/daily/" + "model_streamflow_passirio_merano_daily_ECDF_kr_rea_kr11_obs." + output_format
createPlot(plots,  "Streamflow $[m^3/day]$", "ECDF",
           kr_rea_output_file, output_format=output_format, my_dpi=50)

kr_rea_output_file_log = current.config["output_path"] + "model/streamflow/passirio/daily/" + "model_streamflow_passirio_merano_daily_ECDF_kr_rea_kr11_obs_log." + output_format
createPlot(plots,  "Streamflow $[m^3/day]$", "ECDF",
           kr_rea_output_file_log, output_format=output_format, xscale='log', my_dpi=50)

kr_rea_output_file_hd = current.config["output_path"] +"model/streamflow/passirio/daily/" + "model_streamflow_passirio_merano_daily_ECDF_kr_rea_kr11_obs_HD." + output_format
createPlot(plots,  "Streamflow $[m^3/day]$", "ECDF",
           kr_rea_output_file_hd, output_format=output_format, my_dpi=600)

kr_rea_output_file_log_hd = current.config["output_path"] + "model/streamflow/passirio/daily/" + "model_streamflow_passirio_merano_daily_ECDF_kr_rea_kr11_obs_HD_log." + output_format
createPlot(plots,  "Streamflow $[m^3/day]$", "ECDF",
           kr_rea_output_file_log_hd, output_format=output_format, xscale='log', my_dpi=600)

