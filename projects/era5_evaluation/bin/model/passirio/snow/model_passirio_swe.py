#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert(0, lib_dir)


# In[2]:


from lib import *


# In[ ]:


wdir = "/home/daniele/documents/github/ftt01/phd/projects/era5_evaluation/"
current = DataCollector(configPath=wdir + "etc/conf/")


# In[3]:


### simulation selection #############################################################################

kriging_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

kriging_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_kr_merano_swe_mean_calibration = kriging_data_calibration.model_snow_we.resample('MS').mean()


# In[4]:


### simulation selection #############################################################################

kriging_11_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

kriging_11_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_kr11_merano_swe_mean_calibration = kriging_11_data_calibration.model_snow_we.resample('MS').mean()


# In[5]:


### simulation selection #############################################################################

reanalysis_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

reanalysis_data_calibration.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_rea_merano_swe_mean_calibration = reanalysis_data_calibration.model_snow_we.resample('MS').mean()


# In[6]:


data_kr11_kr_merano_swe_mean_bias = data_kr11_merano_swe_mean_calibration - data_kr_merano_swe_mean_calibration

plt_conf = {}

outfile = current.config["output_path"] + "model/swe/passirio/monthly/"     + "model_swe_passirio_monthly_boxplot_kr11-kr." + output_format
createBoxPlot(data_kr11_kr_merano_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile, output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile_hd = current.config["output_path"] + "model/swe/passirio/monthly/"     + "model_swe_passirio_monthly_boxplot_kr11-kr_HD." + output_format
createBoxPlot(data_kr11_kr_merano_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile_hd, output_format=output_format, scale_factor=0.5, my_dpi=600)


# In[7]:


data_rea_kr_merano_swe_mean_bias = data_rea_merano_swe_mean_calibration - data_kr_merano_swe_mean_calibration

plt_conf = {}

outfile = current.config["output_path"] + "model/swe/passirio/monthly/"     + "model_swe_passirio_monthly_boxplot_rea-kr." + output_format
createBoxPlot(data_rea_kr_merano_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile, output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile_hd = current.config["output_path"] + "model/swe/passirio/monthly/"     + "model_swe_passirio_monthly_boxplot_rea-kr_HD." + output_format
createBoxPlot(data_rea_kr_merano_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile_hd, output_format=output_format, scale_factor=0.5, my_dpi=600)


# In[8]:


data_rea_kr11_merano_swe_mean_bias = data_rea_merano_swe_mean_calibration - data_kr11_merano_swe_mean_calibration

plt_conf = {}

outfile = current.config["output_path"] + "model/swe/passirio/monthly/"     + "model_swe_passirio_monthly_boxplot_rea-kr11." + output_format
createBoxPlot(data_rea_kr11_merano_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile, output_format=output_format, scale_factor=0.5, my_dpi=50)

outfile_hd = current.config["output_path"] + "model/swe/passirio/monthly/"     + "model_swe_passirio_monthly_boxplot_rea-kr11_HD." + output_format
createBoxPlot(data_rea_kr11_merano_swe_mean_bias, "Time $[month]$",
              'SWE bias $[mm/month]$', outfile_hd, output_format=output_format, scale_factor=0.5, my_dpi=600)


# In[9]:


plots = []

### rea 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plt_conf["linewidth"] = 0.8
plots.append((reanalysis_data_calibration.model_snow_we, plt_conf))

### kriging 1x1 plot ###
plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plt_conf["linewidth"] = 0.8
plots.append((kriging_data_calibration.model_snow_we, plt_conf))

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plt_conf["linewidth"] = 0.8
plots.append((kriging_11_data_calibration.model_snow_we, plt_conf))

import matplotlib.dates as mdates
x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y')

outfile = current.config["output_path"] + "model/swe/passirio/hourly/"     + "model_swe_passirio_hourly_kr_kr11_rea." + output_format
createPlot(plots, "Time $[hour]$", 'SWE $[mm/hour]$', outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter,         output_format=output_format, my_dpi=50)

outfile = current.config["output_path"] + "model/swe/passirio/hourly/"     + "model_swe_passirio_hourly_kr_kr11_rea_hd." + output_format
createPlot(plots, "Time $[hour]$", 'SWE $[mm/hour]$', outfile,     x_major_locator=x_major_locator, x_major_formatter=x_major_formatter,         output_format=output_format, my_dpi=600)


# In[ ]:

### simulation selection #############################################################################

kriging_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

kriging_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_kr_merano_swe_mean_validation = kriging_data_validation.model_snow_we.resample('MS').mean()


# In[4]:


### simulation selection #############################################################################

kriging_11_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

kriging_11_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_kr11_merano_swe_mean_validation = kriging_11_data_validation.model_snow_we.resample('MS').mean()


# In[5]:


### simulation selection #############################################################################

reanalysis_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

reanalysis_data_validation.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
data_rea_merano_swe_mean_validation = reanalysis_data_validation.model_snow_we.resample('MS').mean()



from datetime import datetime
start_date_str = "2017-10-01T01:00:00"
end_date_str = "2019-10-01T00:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')
date_range = pd.date_range(start_date, end_date+dt.timedelta(days=31), freq="3MS").tolist()
start_year = str(start_date.year)
end_year = str(end_date.year)


# In[9]:


plots = []

### rea 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plt_conf["linewidth"] = 0.8
plots.append((reanalysis_data_validation.model_snow_we[start_date:end_date], plt_conf))

### kriging 1x1 plot ###
plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plt_conf["linewidth"] = 0.8
plots.append((kriging_data_validation.model_snow_we[start_date:end_date], plt_conf))

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plt_conf["linewidth"] = 0.8
plots.append((kriging_11_data_validation.model_snow_we[start_date:end_date], plt_conf))

import matplotlib.dates as mdates
# x_major_locator=mdates.YearLocator(month=10, day=1)
x_major_formatter=mdates.DateFormatter('%Y-%m')

outfile = current.config["output_path"] + "model/swe/passirio/hourly/"     + f"model_swe_passirio_hourly_kr_kr11_rea_{start_year}{end_year}." + output_format
createPlot(
    plots, "Time $[hour]$", 'SWE $[mm/hour]$', outfile, yticks=[0,50,100,150,200,250,300,350,400,450], y_lim_min=0, y_lim_max=450, x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, output_format=output_format, label="(a)", height=90, width=90, my_dpi=50)

outfile = current.config["output_path"] + "model/swe/passirio/hourly/"     + f"model_swe_passirio_hourly_kr_kr11_rea_{start_year}{end_year}_hd." + output_format
createPlot(
    plots, "Time $[hour]$", 'SWE $[mm/hour]$', outfile, yticks=[0,50,100,150,200,250,300,350,400,450], y_lim_min=0, y_lim_max=450, x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, output_format=output_format, label="(a)", height=90, width=90, my_dpi=600)
