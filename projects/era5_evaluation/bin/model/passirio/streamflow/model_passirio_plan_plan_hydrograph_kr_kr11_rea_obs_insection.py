#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert(0, lib_dir)


# In[ ]:


from lib import *


# In[2]:


wdir = "/home/daniele/documents/github/ftt01/phd/projects/era5_evaluation/"
current = DataCollector(configPath=wdir + "etc/conf/")


# In[3]:


### simulation selection #############################################################################

kriging_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging"
current_node = "plan"

kriging_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

kriging_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_plan"
current_basin = "passirio"
current_type = "kriging"
current_node = "plan"

kriging_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
kriging_data = pd.concat( [kriging_data_calibration.model_flow, kriging_data_validation.model_flow] )


# In[4]:


### simulation selection #############################################################################

kriging_11_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "plan"

kriging_11_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

kriging_11_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_plan"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "plan"

kriging_11_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
kriging_11_data = pd.concat( [kriging_11_data_calibration.model_flow, kriging_11_data_validation.model_flow] )


# In[5]:


### simulation selection #############################################################################

rea_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "plan"

rea_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

rea_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_plan"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "plan"

rea_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
rea_data = pd.concat( [rea_data_calibration.model_flow, rea_data_validation.model_flow] )


# In[6]:


obs_data = pd.concat( [kriging_data_calibration.obs_flow, kriging_data_validation.obs_flow] )


# In[7]:


import matplotlib.dates as mdates
from datetime import datetime
start_date_str = "2018-10-01T01:00:00"
end_date_str = "2019-10-01T00:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')
date_range = pd.date_range(start_date, end_date+dt.timedelta(days=31), freq="1MS").tolist()
start_year = str(start_date.year)
end_year = str(end_date.year)

plots = []

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plt_conf["color"] = 'black'
plt_conf["linewidth"] = 1
plots.append( (obs_data[start_date:end_date], plt_conf) )

### rea 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plt_conf["linewidth"] = 0.8
plots.append( (rea_data[start_date:end_date], plt_conf) )

### kriging 1x1 plot ###
plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plt_conf["linewidth"] = 0.8
plots.append( (kriging_data[start_date:end_date], plt_conf) )

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plt_conf["linewidth"] = 0.8
plots.append( (kriging_11_data[start_date:end_date], plt_conf) )

import matplotlib.dates as mdates
# x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')


# In[8]:


outfile_hd = current.config["output_path"] + "model/streamflow/passirio/hourly/plan_plan/" + f"model_streamflow_passirio_plan_hourly_hydrograph_kr_kr11_rea_obs_{start_year}{end_year}_hd_insection." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, x_rot=90,
           xticks=date_range,x_major_formatter=x_major_formatter, height=90, width=90, label="(b)", my_dpi=600 )

outfile = current.config["output_path"] + "model/streamflow/passirio/hourly/plan_plan/" + f"model_streamflow_passirio_plan_hourly_hydrograph_kr_kr11_rea_{start_year}{end_year}_obs_insection." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, x_rot=90,
           xticks=date_range,x_major_formatter=x_major_formatter, height=90, width=90, label="(b)", my_dpi=50 )

