#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# wdir = "C:/Users/daniele/Documents/GitHub/ftt01/phd/hydro_modeling/ichymod/C_postprocessing/scripts/"
wdir = "/home/daniele/documents/github/ftt01/phd/hydro_modeling/ichymod/C_postprocessing/scripts/"


# In[1]:


import sys, os
# sys.path.insert( 0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(''))),'lib') )
# to link the lib in py scripts as well
os.chdir( wdir )
sys.path.insert( 0, os.path.join(os.path.abspath(os.getcwd()),'lib') )

from lib import *
current = DataCollector()


# In[2]:


### simulation selection #############################################################################

kriging11_data_calibration = DataCollector()

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

kriging11_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################


# In[3]:


### simulation selection #############################################################################

kriging11_data_validation = DataCollector()

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

kriging11_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################


# In[4]:


kriging11_data = pd.concat( [kriging11_data_calibration.model_flow, kriging11_data_validation.model_flow] )
obs_data = pd.concat( [kriging11_data_calibration.obs_flow, kriging11_data_validation.obs_flow] )


# In[5]:


# define and add to plot the vertical line between calibration and validation #
last_date_cal = kriging11_data_calibration.model_flow.index[-1]
first_date_val = kriging11_data_validation.model_flow.index[0]

max_h = max( np.concatenate((kriging11_data_calibration.model_flow.values, kriging11_data_validation.model_flow.values,     kriging11_data_calibration.obs_flow.values, kriging11_data_validation.obs_flow.values)) )
vertical_line = np.array( [0, max_h] )
vertical_line_DF = pd.DataFrame(data=vertical_line, index=[last_date_cal, first_date_val])


# In[6]:


plots = []

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plt_conf["color"] = '#fdb863'
plots.append( (obs_data, plt_conf) )

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plt_conf["color"] = '#5e3c99'
plots.append( (kriging11_data, plt_conf) )

plt_conf = {}
plt_conf["linestyle"] = "--"
plots.append( (vertical_line_DF, plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')


# In[7]:


outfile_hd = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_merano/"     + "model_streamflow_passirio_merano_hourly_hydrograph_kr11_obs_hd." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

outfile = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_merano/"     + "model_streamflow_passirio_merano_hourly_hydrograph_kr11_obs." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )


# In[8]:


from datetime import datetime
start_date_str = "2015-10-01T01:00:00"
end_date_str = "2016-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

plots = []

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plt_conf["color"] = '#fdb863'
plots.append( (obs_data[start_date:end_date], plt_conf) )

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plt_conf["color"] = '#5e3c99'
plots.append( (kriging11_data[start_date:end_date], plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile_hd = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_merano/"     + "model_streamflow_passirio_merano_hourly_hydrograph_kr11_obs_20152016_hd." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

outfile = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_merano/"     + "model_streamflow_passirio_merano_hourly_hydrograph_kr11_obs_20152016." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )

########################

from datetime import datetime
start_date_str = "2016-10-01T01:00:00"
end_date_str = "2017-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

plots = []

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plt_conf["color"] = '#fdb863'
plots.append( (obs_data[start_date:end_date], plt_conf) )

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'Kriging 11x8'
plt_conf["color"] = '#5e3c99'
plots.append( (kriging11_data[start_date:end_date], plt_conf) )

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile_hd = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_merano/"     + "model_streamflow_passirio_merano_hourly_hydrograph_kr11_obs_20162017_hd." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600, height=80 )

outfile = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_merano/"     + "model_streamflow_passirio_merano_hourly_hydrograph_kr11_obs_20162017." + output_format
createPlot( plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50, height=80 )

