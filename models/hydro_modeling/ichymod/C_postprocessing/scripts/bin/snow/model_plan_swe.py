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

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging"
current_node = "plan"

kriging_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################


# In[ ]:


### simulation selection #############################################################################

kriging_11_data_calibration = DataCollector()

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "plan"

kriging_11_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################


# In[ ]:


### simulation selection #############################################################################

reanalysis_data_calibration = DataCollector()

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "plan"

reanalysis_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################


# In[ ]:


data_kr_plan_swe_mean_calibration = kriging_data_calibration.model_snow_we_plan.resample('MS').mean()
data_kr11_plan_swe_mean_calibration = kriging_11_data_calibration.model_snow_we_plan.resample('MS').mean()
data_rea_plan_swe_mean_calibration = reanalysis_data_calibration.model_snow_we_plan.resample('MS').mean()

data_kr11_kr_plan_swe_mean_bias = data_kr11_plan_swe_mean_calibration - data_kr_plan_swe_mean_calibration

plt_conf = {}

outfile = current.config["output_path"] + "model/swe/plan/monthly/"     + "model_swe_plan_monthly_boxplot_kr11-kr." + output_format
createBoxPlot(data_kr11_kr_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile, output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile_hd = current.config["output_path"] + "model/swe/plan/monthly/"     + "model_swe_plan_monthly_boxplot_kr11-kr_HD." + output_format
createBoxPlot(data_kr11_kr_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile_hd, output_format=output_format, scale_factor=0.5, my_dpi=600)


# In[ ]:


data_rea_kr_plan_swe_mean_bias = data_rea_plan_swe_mean_calibration - data_kr_plan_swe_mean_calibration

plt_conf = {}

outfile = current.config["output_path"] + "model/swe/plan/monthly/"     + "model_swe_plan_monthly_boxplot_rea-kr." + output_format
createBoxPlot(data_rea_kr_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile, output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile_hd = current.config["output_path"] + "model/swe/plan/monthly/"     + "model_swe_plan_monthly_boxplot_rea-kr_HD." + output_format
createBoxPlot(data_rea_kr_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile_hd, output_format=output_format, scale_factor=0.5, my_dpi=600)


# In[ ]:


data_rea_kr11_plan_swe_mean_bias = data_rea_plan_swe_mean_calibration - data_kr11_plan_swe_mean_calibration

plt_conf = {}

outfile = current.config["output_path"] + "model/swe/plan/monthly/"     + "model_swe_plan_monthly_boxplot_rea-kr11." + output_format
createBoxPlot(data_rea_kr11_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile, output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile_hd = current.config["output_path"] + "model/swe/plan/monthly/"     + "model_swe_plan_monthly_boxplot_rea-kr11_HD." + output_format
createBoxPlot(data_rea_kr11_plan_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile_hd, output_format=output_format, scale_factor=0.5, my_dpi=600)


# In[ ]:


plots = []

### rea 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Reanalysis 11x8'
plt_conf["color"] = '#e66101'
plots.append((reanalysis_data_calibration.model_snow_we, plt_conf))

### kriging 1x1 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 1x1'
plt_conf["color"] = '#8078bc'
plots.append((kriging_data_calibration.model_snow_we, plt_conf))

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plt_conf["color"] = '#5e3c99'
plots.append((kriging_11_data_calibration.model_snow_we, plt_conf))

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y')

outfile = current.config["output_path"] + "model/swe/plan/hourly/"     + "model_swe_plan_hourly_boxplot_kr_rea_kr11." + output_format
createPlot(plots, "Time $[hour]$", 'SWE $[mm/hour]$', outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter,         output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile = current.config["output_path"] + "model/swe/plan/hourly/"     + "model_swe_plan_hourly_boxplot_kr_rea_kr11_HD." + output_format
createPlot(plots, "Time $[hour]$", 'SWE $[mm/hour]$', outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter,         output_format=output_format, scale_factor=0.5, my_dpi=600)

