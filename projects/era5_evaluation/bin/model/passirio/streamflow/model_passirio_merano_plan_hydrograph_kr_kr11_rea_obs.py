#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert(0, lib_dir)


# In[ ]:


from lib import *


# In[ ]:


wdir = "/home/daniele/documents/github/ftt01/phd/projects/era5_evaluation/"
current = DataCollector(configPath=wdir + "etc/conf/")


# In[ ]:


### simulation selection #############################################################################

kriging_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "plan"

kriging_data_calibration.retrieveData(
    current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

kriging_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "plan"

kriging_data_validation.retrieveData(
    current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
kriging_data = pd.concat(
    [kriging_data_calibration.model_flow, kriging_data_validation.model_flow])


# In[ ]:


### simulation selection #############################################################################

kriging_11_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "plan"

kriging_11_data_calibration.retrieveData(
    current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

kriging_11_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "plan"

kriging_11_data_validation.retrieveData(
    current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
kriging_11_data = pd.concat(
    [kriging_11_data_calibration.model_flow, kriging_11_data_validation.model_flow])


# In[ ]:


### simulation selection #############################################################################

rea_data_calibration = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "plan"

rea_data_calibration.retrieveData(
    current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

rea_data_validation = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "validation_best_merano"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "plan"

rea_data_validation.retrieveData(
    current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
rea_data = pd.concat([rea_data_calibration.model_flow,
                     rea_data_validation.model_flow])


# In[ ]:


obs_data = pd.concat([kriging_data_calibration.obs_flow,
                     kriging_data_validation.obs_flow])


# In[ ]:


## define and add to plot the vertical line between calibration and validation #
last_date_cal = kriging_data_calibration.model_flow.index[-1]
first_date_val = kriging_data_validation.model_flow.index[0]

max_h = max(np.concatenate((kriging_data_calibration.model_flow.values, kriging_data_validation.model_flow.values,
                            kriging_data_calibration.obs_flow.values, kriging_data_validation.obs_flow.values)))
vertical_line = np.array([0, max_h])
vertical_line_DF = pd.DataFrame(data=vertical_line, index=[
                                last_date_cal, first_date_val])


# In[ ]:


import matplotlib.dates as mdates
from datetime import datetime
start_date_str = "2013-10-01T01:00:00"
end_date_str = "2019-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

plots = []

plt_conf = {}
plt_conf["color"] = 'black'
plt_conf["linestyle"] = "--"
plt_conf["linewidth"] = 0.8
plots.append((vertical_line_DF, plt_conf))

### rea 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plt_conf["linewidth"] = 0.8
plots.append((rea_data[start_date:end_date], plt_conf))

### obs plot ###
plt_conf = {}
plt_conf["label"] = 'Observed'
plt_conf["color"] = 'black'
plt_conf["linewidth"] = 1
plots.append((obs_data[start_date:end_date], plt_conf))

### kriging 1x1 plot ###
plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plt_conf["linewidth"] = 0.8
plots.append((kriging_data[start_date:end_date], plt_conf))

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plt_conf["linewidth"] = 0.8
plots.append((kriging_11_data[start_date:end_date], plt_conf))

x_major_locator = mdates.YearLocator(month=10, day=1)
x_major_formatter = mdates.DateFormatter('%Y-%m')


# In[ ]:


outfile_hd = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_plan/" +     "model_streamflow_passirio_plan_hourly_hydrograph_kr_kr11_rea_obs_hd." + output_format
createPlot(plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, label="(a)", height=90, width=130,
           x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=600)

outfile = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_plan/" +     "model_streamflow_passirio_plan_hourly_hydrograph_kr_kr11_rea_obs." + output_format
createPlot(plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, label="(a)", height=90, width=130,
           x_major_locator=x_major_locator, x_major_formatter=x_major_formatter, my_dpi=50)


# In[ ]:


import matplotlib.dates as mdates
from datetime import datetime
start_date_str = "2015-10-01T01:00:00"
end_date_str = "2016-10-01T00:00:00"
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
plots.append((obs_data[start_date:end_date], plt_conf))

### rea 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plots.append((rea_data[start_date:end_date], plt_conf))

### kriging 1x1 plot ###
plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plots.append((kriging_data[start_date:end_date], plt_conf))

### kriging 11x8 plot ###
plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plots.append((kriging_11_data[start_date:end_date], plt_conf))

# x_major_locator = mdates.YearLocator(month=10, day=1)
x_major_formatter = mdates.DateFormatter('%Y-%m')


# In[ ]:


outfile_hd = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_plan/" +     f"model_streamflow_passirio_plan_hourly_hydrograph_kr_kr11_rea_obs_{start_year}{end_year}_hd." + output_format
createPlot(plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile_hd, x_rot=90,
           xticks=date_range,x_major_formatter=x_major_formatter, height=90, width=90, label="(b)", my_dpi=600 )

outfile = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_plan/" +     f"model_streamflow_passirio_plan_hourly_hydrograph_kr_kr11_rea_{start_year}{end_year}_obs." + output_format
createPlot(plots, "Time $[hour]$", "Streamflow $[m^3/hour]$", outfile, x_rot=90,
           xticks=date_range,x_major_formatter=x_major_formatter, height=90, width=90, label="(b)", my_dpi=50 )


# In[ ]:


# entire period exceedance curve evaluation

from datetime import datetime
start_date_str = "2013-10-01T01:00:00"
end_date_str = "2019-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

plots = []

### kriging 1x1 plot ###
kriging_data_fd = flowDuration(kriging_data[start_date:end_date])
kriging_data_fd.dropna(inplace=True)

plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plots.append((kriging_data_fd, plt_conf))

### obs plot ###
obs_data_fd = flowDuration(obs_data[start_date:end_date])
obs_data_fd.dropna(inplace=True)

plt_conf = {}
plt_conf["label"] = 'Observed'
plt_conf["color"] = 'black'
plots.append((obs_data_fd, plt_conf))

### rea 11x8 plot ###
rea_data_fd = flowDuration(rea_data[start_date:end_date])
rea_data_fd.dropna(inplace=True)

plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plots.append((rea_data_fd, plt_conf))

### kriging 11x8 plot ###
kriging_11_data_fd = flowDuration(kriging_11_data[start_date:end_date])
kriging_11_data_fd.dropna(inplace=True)

plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plots.append((kriging_11_data_fd, plt_conf))

outfile_hd = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_plan/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_kr_kr11_rea_obs_hd." + output_format
createPlot(plots, "Exceedance Probability",
           "Streamflow $[m^3/hour]$", outfile_hd, label="(b)", plot_legend=False, xticks=[0,25,50,75,100],
           yscale='log', height=90, width=60, my_dpi=600)

outfile = current.config["output_path"] + "model/streamflow/passirio/hourly/merano_plan/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_kr_kr11_rea_obs." + output_format
createPlot(plots, "Exceedance Probability",
           "Streamflow $[m^3/hour]$", outfile, label="(b)", plot_legend=False, xticks=[0,25,50,75,100],
           yscale='log', height=90, width=60, my_dpi=50)


# In[ ]:


# ## seasonal exceedance curve evaluation

# from datetime import datetime
# start_date_str = "2013-10-01T01:00:00"
# end_date_str = "2019-09-30T23:00:00"
# start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
# end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

# # seasonal separation data - observed data
# obs_data = obs_data[start_date:end_date]

# obs_data_jan=obs_data.loc[(obs_data.index.month==1)]
# obs_data_feb=obs_data.loc[(obs_data.index.month==2)]
# obs_data_mar=obs_data.loc[(obs_data.index.month==3)]
# obs_data_apr=obs_data.loc[(obs_data.index.month==4)]
# obs_data_may=obs_data.loc[(obs_data.index.month==5)]
# obs_data_jun=obs_data.loc[(obs_data.index.month==6)]
# obs_data_jul=obs_data.loc[(obs_data.index.month==7)]
# obs_data_aug=obs_data.loc[(obs_data.index.month==8)]
# obs_data_sep=obs_data.loc[(obs_data.index.month==9)]
# obs_data_oct=obs_data.loc[(obs_data.index.month==10)]
# obs_data_nov=obs_data.loc[(obs_data.index.month==11)]
# obs_data_dec=obs_data.loc[(obs_data.index.month==12)]

# obs_data_w = pd.concat([obs_data_dec, obs_data_jan, obs_data_feb])
# obs_data_sp = pd.concat([obs_data_mar, obs_data_apr, obs_data_may])
# obs_data_su = pd.concat([obs_data_jun, obs_data_jul, obs_data_aug])
# obs_data_a = pd.concat([obs_data_sep, obs_data_oct, obs_data_nov,])

# # seasonal separation data - kriging 1x1 data
# kriging_data = kriging_data[start_date:end_date]

# kriging_data_jan=kriging_data.loc[(kriging_data.index.month==1)]
# kriging_data_feb=kriging_data.loc[(kriging_data.index.month==2)]
# kriging_data_mar=kriging_data.loc[(kriging_data.index.month==3)]
# kriging_data_apr=kriging_data.loc[(kriging_data.index.month==4)]
# kriging_data_may=kriging_data.loc[(kriging_data.index.month==5)]
# kriging_data_jun=kriging_data.loc[(kriging_data.index.month==6)]
# kriging_data_jul=kriging_data.loc[(kriging_data.index.month==7)]
# kriging_data_aug=kriging_data.loc[(kriging_data.index.month==8)]
# kriging_data_sep=kriging_data.loc[(kriging_data.index.month==9)]
# kriging_data_oct=kriging_data.loc[(kriging_data.index.month==10)]
# kriging_data_nov=kriging_data.loc[(kriging_data.index.month==11)]
# kriging_data_dec=kriging_data.loc[(kriging_data.index.month==12)]

# kriging_data_w=pd.concat([kriging_data_dec,kriging_data_jan,kriging_data_feb])
# kriging_data_sp=pd.concat([kriging_data_mar,kriging_data_apr,kriging_data_may])
# kriging_data_su=pd.concat([kriging_data_jun,kriging_data_jul,kriging_data_aug])
# kriging_data_a=pd.concat([kriging_data_sep,kriging_data_oct,kriging_data_nov])

# # seasonal separation data - kriging 11x8 data
# kriging_11_data = kriging_11_data[start_date:end_date]

# kriging_11_data_jan=kriging_11_data.loc[(kriging_11_data.index.month==1)]
# kriging_11_data_feb=kriging_11_data.loc[(kriging_11_data.index.month==2)]
# kriging_11_data_mar=kriging_11_data.loc[(kriging_11_data.index.month==3)]
# kriging_11_data_apr=kriging_11_data.loc[(kriging_11_data.index.month==4)]
# kriging_11_data_may=kriging_11_data.loc[(kriging_11_data.index.month==5)]
# kriging_11_data_jun=kriging_11_data.loc[(kriging_11_data.index.month==6)]
# kriging_11_data_jul=kriging_11_data.loc[(kriging_11_data.index.month==7)]
# kriging_11_data_aug=kriging_11_data.loc[(kriging_11_data.index.month==8)]
# kriging_11_data_sep=kriging_11_data.loc[(kriging_11_data.index.month==9)]
# kriging_11_data_oct=kriging_11_data.loc[(kriging_11_data.index.month==10)]
# kriging_11_data_nov=kriging_11_data.loc[(kriging_11_data.index.month==11)]
# kriging_11_data_dec=kriging_11_data.loc[(kriging_11_data.index.month==12)]

# kriging_11_data_w=pd.concat([kriging_11_data_dec,kriging_11_data_jan,kriging_11_data_feb])
# kriging_11_data_sp=pd.concat([kriging_11_data_mar,kriging_11_data_apr,kriging_11_data_may])
# kriging_11_data_su=pd.concat([kriging_11_data_jun,kriging_11_data_jul,kriging_11_data_aug])
# kriging_11_data_a=pd.concat([kriging_11_data_sep,kriging_11_data_oct,kriging_11_data_nov])

# # seasonal separation data - reanalysis 11x8 data
# rea_data = rea_data[start_date:end_date]

# rea_data_jan=rea_data.loc[(rea_data.index.month==1)]
# rea_data_feb=rea_data.loc[(rea_data.index.month==2)]
# rea_data_mar=rea_data.loc[(rea_data.index.month==3)]
# rea_data_apr=rea_data.loc[(rea_data.index.month==4)]
# rea_data_may=rea_data.loc[(rea_data.index.month==5)]
# rea_data_jun=rea_data.loc[(rea_data.index.month==6)]
# rea_data_jul=rea_data.loc[(rea_data.index.month==7)]
# rea_data_aug=rea_data.loc[(rea_data.index.month==8)]
# rea_data_sep=rea_data.loc[(rea_data.index.month==9)]
# rea_data_oct=rea_data.loc[(rea_data.index.month==10)]
# rea_data_nov=rea_data.loc[(rea_data.index.month==11)]
# rea_data_dec=rea_data.loc[(rea_data.index.month==12)]

# rea_data_w = pd.concat([rea_data_dec,rea_data_jan,rea_data_feb])
# rea_data_sp = pd.concat([rea_data_mar,rea_data_apr,rea_data_may])
# rea_data_su = pd.concat([rea_data_jun,rea_data_jul,rea_data_aug])
# rea_data_a = pd.concat([rea_data_sep,rea_data_oct,rea_data_nov])


# In[ ]:


# ## seasonal exceedance curve evaluation

# from datetime import datetime
# start_date_str = "2013-10-01T01:00:00"
# end_date_str = "2019-09-30T23:00:00"
# start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
# end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

# # seasonal separation data - observed data
# obs_data = obs_data[start_date:end_date]

# obs_data_jan=obs_data.loc[(obs_data.index.month==1)]
# obs_data_feb=obs_data.loc[(obs_data.index.month==2)]
# obs_data_mar=obs_data.loc[(obs_data.index.month==3)]
# obs_data_apr=obs_data.loc[(obs_data.index.month==4)]
# obs_data_may=obs_data.loc[(obs_data.index.month==5)]
# obs_data_jun=obs_data.loc[(obs_data.index.month==6)]
# obs_data_jul=obs_data.loc[(obs_data.index.month==7)]
# obs_data_aug=obs_data.loc[(obs_data.index.month==8)]
# obs_data_sep=obs_data.loc[(obs_data.index.month==9)]
# obs_data_oct=obs_data.loc[(obs_data.index.month==10)]
# obs_data_nov=obs_data.loc[(obs_data.index.month==11)]
# obs_data_dec=obs_data.loc[(obs_data.index.month==12)]

# obs_data_w=pd.concat([obs_data_dec,obs_data_jan,obs_data_feb])
# obs_data_sp=pd.concat([obs_data_mar,obs_data_apr,obs_data_may])
# obs_data_su=pd.concat([obs_data_jun,obs_data_jul,obs_data_aug])
# obs_data_a=pd.concat([obs_data_sep,obs_data_oct,obs_data_nov])

# # seasonal separation data - kriging 1x1 data
# kriging_data = kriging_data[start_date:end_date]

# kriging_data_jan=kriging_data.loc[(kriging_data.index.month==1)]
# kriging_data_feb=kriging_data.loc[(kriging_data.index.month==2)]
# kriging_data_mar=kriging_data.loc[(kriging_data.index.month==3)]
# kriging_data_apr=kriging_data.loc[(kriging_data.index.month==4)]
# kriging_data_may=kriging_data.loc[(kriging_data.index.month==5)]
# kriging_data_jun=kriging_data.loc[(kriging_data.index.month==6)]
# kriging_data_jul=kriging_data.loc[(kriging_data.index.month==7)]
# kriging_data_aug=kriging_data.loc[(kriging_data.index.month==8)]
# kriging_data_sep=kriging_data.loc[(kriging_data.index.month==9)]
# kriging_data_oct=kriging_data.loc[(kriging_data.index.month==10)]
# kriging_data_nov=kriging_data.loc[(kriging_data.index.month==11)]
# kriging_data_dec=kriging_data.loc[(kriging_data.index.month==12)]

# kriging_data_w=pd.concat([kriging_data_dec,kriging_data_jan,kriging_data_feb])
# kriging_data_sp=pd.concat([kriging_data_mar,kriging_data_apr,kriging_data_may])
# kriging_data_su=pd.concat([kriging_data_jun,kriging_data_jul,kriging_data_aug])
# kriging_data_a=pd.concat([kriging_data_sep,kriging_data_oct,kriging_data_nov])

# # seasonal separation data - kriging 11x8 data
# kriging_11_data = kriging_11_data[start_date:end_date]

# kriging_11_data_jan=kriging_11_data.loc[(kriging_11_data.index.month==1)]
# kriging_11_data_feb=kriging_11_data.loc[(kriging_11_data.index.month==2)]
# kriging_11_data_mar=kriging_11_data.loc[(kriging_11_data.index.month==3)]
# kriging_11_data_apr=kriging_11_data.loc[(kriging_11_data.index.month==4)]
# kriging_11_data_may=kriging_11_data.loc[(kriging_11_data.index.month==5)]
# kriging_11_data_jun=kriging_11_data.loc[(kriging_11_data.index.month==6)]
# kriging_11_data_jul=kriging_11_data.loc[(kriging_11_data.index.month==7)]
# kriging_11_data_aug=kriging_11_data.loc[(kriging_11_data.index.month==8)]
# kriging_11_data_sep=kriging_11_data.loc[(kriging_11_data.index.month==9)]
# kriging_11_data_oct=kriging_11_data.loc[(kriging_11_data.index.month==10)]
# kriging_11_data_nov=kriging_11_data.loc[(kriging_11_data.index.month==11)]
# kriging_11_data_dec=kriging_11_data.loc[(kriging_11_data.index.month==12)]

# kriging_11_data_w=pd.concat([kriging_11_data_dec,kriging_11_data_jan,kriging_11_data_feb])
# kriging_11_data_sp=pd.concat([kriging_11_data_mar,kriging_11_data_apr,kriging_11_data_may])
# kriging_11_data_su=pd.concat([kriging_11_data_jun,kriging_11_data_jul,kriging_11_data_aug])
# kriging_11_data_a=pd.concat([kriging_11_data_sep,kriging_11_data_oct,kriging_11_data_nov])

# # seasonal separation data - reanalysis 11x8 data
# rea_data = rea_data[start_date:end_date]

# rea_data_jan=rea_data.loc[(rea_data.index.month==1)]
# rea_data_feb=rea_data.loc[(rea_data.index.month==2)]
# rea_data_mar=rea_data.loc[(rea_data.index.month==3)]
# rea_data_apr=rea_data.loc[(rea_data.index.month==4)]
# rea_data_may=rea_data.loc[(rea_data.index.month==5)]
# rea_data_jun=rea_data.loc[(rea_data.index.month==6)]
# rea_data_jul=rea_data.loc[(rea_data.index.month==7)]
# rea_data_aug=rea_data.loc[(rea_data.index.month==8)]
# rea_data_sep=rea_data.loc[(rea_data.index.month==9)]
# rea_data_oct=rea_data.loc[(rea_data.index.month==10)]
# rea_data_nov=rea_data.loc[(rea_data.index.month==11)]
# rea_data_dec=rea_data.loc[(rea_data.index.month==12)]

# rea_data_w=pd.concat([rea_data_dec,rea_data_jan,rea_data_feb])
# rea_data_sp=pd.concat([rea_data_mar,rea_data_apr,rea_data_may])
# rea_data_su=pd.concat([rea_data_jun,rea_data_jul,rea_data_aug])
# rea_data_a=pd.concat([rea_data_sep,rea_data_oct,rea_data_nov])


# In[ ]:


# seasonal exceedance curve evaluation

from datetime import datetime
start_date_str = "2013-10-01T01:00:00"
end_date_str = "2019-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

# seasonal separation data - observed data
obs_data = obs_data[start_date:end_date]

obs_data_jan = obs_data.loc[(obs_data.index.month == 1)]
obs_data_feb = obs_data.loc[(obs_data.index.month == 2)]
obs_data_mar = obs_data.loc[(obs_data.index.month == 3)]
obs_data_apr = obs_data.loc[(obs_data.index.month == 4)]
obs_data_may = obs_data.loc[(obs_data.index.month == 5)]
obs_data_jun = obs_data.loc[(obs_data.index.month == 6)]
obs_data_jul = obs_data.loc[(obs_data.index.month == 7)]
obs_data_aug = obs_data.loc[(obs_data.index.month == 8)]
obs_data_sep = obs_data.loc[(obs_data.index.month == 9)]
obs_data_oct = obs_data.loc[(obs_data.index.month == 10)]
obs_data_nov = obs_data.loc[(obs_data.index.month == 11)]
obs_data_dec = obs_data.loc[(obs_data.index.month == 12)]

obs_data_w = pd.concat([obs_data_dec, obs_data_jan, obs_data_feb])
obs_data_sp = pd.concat([obs_data_mar, obs_data_apr, obs_data_may])
obs_data_su = pd.concat([obs_data_jun, obs_data_jul, obs_data_aug])
obs_data_a = pd.concat([obs_data_sep, obs_data_oct, obs_data_nov])

# seasonal separation data - kriging 1x1 data
kriging_data = kriging_data[start_date:end_date]

kriging_data_jan = kriging_data.loc[(kriging_data.index.month == 1)]
kriging_data_feb = kriging_data.loc[(kriging_data.index.month == 2)]
kriging_data_mar = kriging_data.loc[(kriging_data.index.month == 3)]
kriging_data_apr = kriging_data.loc[(kriging_data.index.month == 4)]
kriging_data_may = kriging_data.loc[(kriging_data.index.month == 5)]
kriging_data_jun = kriging_data.loc[(kriging_data.index.month == 6)]
kriging_data_jul = kriging_data.loc[(kriging_data.index.month == 7)]
kriging_data_aug = kriging_data.loc[(kriging_data.index.month == 8)]
kriging_data_sep = kriging_data.loc[(kriging_data.index.month == 9)]
kriging_data_oct = kriging_data.loc[(kriging_data.index.month == 10)]
kriging_data_nov = kriging_data.loc[(kriging_data.index.month == 11)]
kriging_data_dec = kriging_data.loc[(kriging_data.index.month == 12)]

kriging_data_w = pd.concat(
    [kriging_data_dec, kriging_data_jan, kriging_data_feb])
kriging_data_sp = pd.concat(
    [kriging_data_mar, kriging_data_apr, kriging_data_may])
kriging_data_su = pd.concat(
    [kriging_data_jun, kriging_data_jul, kriging_data_aug])
kriging_data_a = pd.concat(
    [kriging_data_sep, kriging_data_oct, kriging_data_nov])

# seasonal separation data - kriging 11x8 data
kriging_11_data = kriging_11_data[start_date:end_date]

kriging_11_data_jan = kriging_11_data.loc[(kriging_11_data.index.month == 1)]
kriging_11_data_feb = kriging_11_data.loc[(kriging_11_data.index.month == 2)]
kriging_11_data_mar = kriging_11_data.loc[(kriging_11_data.index.month == 3)]
kriging_11_data_apr = kriging_11_data.loc[(kriging_11_data.index.month == 4)]
kriging_11_data_may = kriging_11_data.loc[(kriging_11_data.index.month == 5)]
kriging_11_data_jun = kriging_11_data.loc[(kriging_11_data.index.month == 6)]
kriging_11_data_jul = kriging_11_data.loc[(kriging_11_data.index.month == 7)]
kriging_11_data_aug = kriging_11_data.loc[(kriging_11_data.index.month == 8)]
kriging_11_data_sep = kriging_11_data.loc[(kriging_11_data.index.month == 9)]
kriging_11_data_oct = kriging_11_data.loc[(kriging_11_data.index.month == 10)]
kriging_11_data_nov = kriging_11_data.loc[(kriging_11_data.index.month == 11)]
kriging_11_data_dec = kriging_11_data.loc[(kriging_11_data.index.month == 12)]

kriging_11_data_w = pd.concat(
    [kriging_11_data_dec, kriging_11_data_jan, kriging_11_data_feb])
kriging_11_data_sp = pd.concat(
    [kriging_11_data_mar, kriging_11_data_apr, kriging_11_data_may])
kriging_11_data_su = pd.concat(
    [kriging_11_data_jun, kriging_11_data_jul, kriging_11_data_aug])
kriging_11_data_a = pd.concat(
    [kriging_11_data_sep, kriging_11_data_oct, kriging_11_data_nov])

# seasonal separation data - reanalysis 11x8 data
rea_data = rea_data[start_date:end_date]

rea_data_jan = rea_data.loc[(rea_data.index.month == 1)]
rea_data_feb = rea_data.loc[(rea_data.index.month == 2)]
rea_data_mar = rea_data.loc[(rea_data.index.month == 3)]
rea_data_apr = rea_data.loc[(rea_data.index.month == 4)]
rea_data_may = rea_data.loc[(rea_data.index.month == 5)]
rea_data_jun = rea_data.loc[(rea_data.index.month == 6)]
rea_data_jul = rea_data.loc[(rea_data.index.month == 7)]
rea_data_aug = rea_data.loc[(rea_data.index.month == 8)]
rea_data_sep = rea_data.loc[(rea_data.index.month == 9)]
rea_data_oct = rea_data.loc[(rea_data.index.month == 10)]
rea_data_nov = rea_data.loc[(rea_data.index.month == 11)]
rea_data_dec = rea_data.loc[(rea_data.index.month == 12)]

rea_data_w = pd.concat([rea_data_dec, rea_data_jan, rea_data_feb])
rea_data_sp = pd.concat([rea_data_mar, rea_data_apr, rea_data_may])
rea_data_su = pd.concat([rea_data_jun, rea_data_jul, rea_data_aug])
rea_data_a = pd.concat([rea_data_sep, rea_data_oct, rea_data_nov])


# In[ ]:


# autumn
plots = []

### obs plot ###
obs_data_fd = flowDuration(obs_data_a)
obs_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'Observed'
plt_conf["color"] = 'black'
plots.append((obs_data_fd, plt_conf))

### rea 11x8 plot ###
rea_data_fd = flowDuration(rea_data_a)
rea_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plots.append((rea_data_fd, plt_conf))

### kriging 1x1 plot ###
kriging_data_fd = flowDuration(kriging_data_a)
kriging_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plots.append((kriging_data_fd, plt_conf))

### kriging 11x8 plot ###
kriging_11_data_fd = flowDuration(kriging_11_data_a)
kriging_11_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plots.append((kriging_11_data_fd, plt_conf))

outfile_hd = current.config["output_path"] + "model/streamflow/passirio/seasonal/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_autumn_kr_kr11_rea_obs_hd." + output_format
createPlot(plots, "Exceedance Probability", "Streamflow $[m^3/h]$", outfile_hd, label="(b.1)", y_lim_min=0.2,
           y_lim_max=250, plot_legend=False, scale_factor=1, yscale='log', height=60, width=90, my_dpi=600)

outfile = current.config["output_path"] + "model/streamflow/passirio/seasonal/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_autumn_kr_kr11_rea_obs." + output_format
createPlot(plots, "Exceedance Probability", "Streamflow $[m^3/h]$", outfile, label="(b.1)", y_lim_min=0.2,
           y_lim_max=250, plot_legend=False, scale_factor=1, yscale='log', height=60, width=90, my_dpi=50)


# In[ ]:


# winter
plots = []

### obs plot ###
obs_data_fd = flowDuration(obs_data_w)
obs_data_fd.dropna(inplace=True)

plt_conf = {}
plt_conf["label"] = 'Observed'
plt_conf["color"] = 'black'
plots.append((obs_data_fd, plt_conf))

### rea 11x8 plot ###
rea_data_fd = flowDuration(rea_data_w)
rea_data_fd.dropna(inplace=True)

plt_conf = {}
plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plots.append((rea_data_fd, plt_conf))

### kriging 1x1 plot ###
kriging_data_fd = flowDuration(kriging_data_w)
kriging_data_fd.dropna(inplace=True)

plt_conf = {}
plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plots.append((kriging_data_fd, plt_conf))

### kriging 11x8 plot ###
kriging_11_data_fd = flowDuration(kriging_11_data_w)
kriging_11_data_fd.dropna(inplace=True)

plt_conf = {}
plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plots.append((kriging_11_data_fd, plt_conf))

outfile_hd = current.config["output_path"] + "model/streamflow/passirio/seasonal/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_winter_kr_kr11_rea_obs_hd." + output_format
createPlot(plots, "Exceedance Probability", "Streamflow $[m^3/h]$", outfile_hd, label="(b.2)", y_lim_min=0.03,
           y_lim_max=50, plot_legend=False, scale_factor=1, yscale='log', height=60, width=90, my_dpi=600)

outfile = current.config["output_path"] + "model/streamflow/passirio/seasonal/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_winter_kr_kr11_rea_obs." + output_format
createPlot(plots, "Exceedance Probability", "Streamflow $[m^3/h]$", outfile, label="(b.2)", y_lim_min=0.03,
           y_lim_max=50, plot_legend=False, scale_factor=1, yscale='log', height=60, width=90, my_dpi=50)


# In[ ]:


# spring
plots = []

### obs plot ###
obs_data_fd = flowDuration(obs_data_sp)
obs_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'Observed'
plt_conf["color"] = 'black'
plots.append((obs_data_fd, plt_conf))

### rea 11x8 plot ###
rea_data_fd = flowDuration(rea_data_sp)
rea_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plots.append((rea_data_fd, plt_conf))

### kriging 1x1 plot ###
kriging_data_fd = flowDuration(kriging_data_sp)
kriging_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plots.append((kriging_data_fd, plt_conf))

### kriging 11x8 plot ###
kriging_11_data_fd = flowDuration(kriging_11_data_sp)
kriging_11_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plots.append((kriging_11_data_fd, plt_conf))

outfile_hd = current.config["output_path"] + "model/streamflow/passirio/seasonal/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_spring_kr_kr11_rea_obs_hd." + output_format
createPlot(plots, "Exceedance Probability", "Streamflow $[m^3/h]$", outfile_hd, label="(b.3)",
           y_lim_min=0.02, y_lim_max=250, plot_legend=False, scale_factor=1, yscale='log',
           height=60, width=90, my_dpi=600)

outfile = current.config["output_path"] + "model/streamflow/passirio/seasonal/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_spring_kr_kr11_rea_obs." + output_format
createPlot(plots, "Exceedance Probability", "Streamflow $[m^3/h]$", outfile, label="(b.3)",
           y_lim_min=0.02, y_lim_max=250, plot_legend=False, scale_factor=1, yscale='log',
           height=60, width=90, my_dpi=50)


# In[ ]:

# summer
plots = []

### obs plot ###
### obs plot ###
### delete suspicious data
obs_data_cut = obs_data_su.copy()
# obs_data_cut = obs_data_cut[start_date:end_date]
obs_data_cut[obs_data_cut<=1.4] = 1.4
obs_data_fd = flowDuration(obs_data_cut.dropna())
obs_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'Observed'
plt_conf["color"] = 'black'
plots.append((obs_data_fd, plt_conf))

### rea 11x8 plot ###
rea_data_fd = flowDuration(rea_data_su)
rea_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'REA11x8'
plt_conf["color"] = '#CD001A'
plots.append((rea_data_fd, plt_conf))

### kriging 1x1 plot ###
kriging_data_fd = flowDuration(kriging_data_su)
kriging_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'KR1x1'
plt_conf["color"] = '#FE5000'
plots.append((kriging_data_fd, plt_conf))

### kriging 11x8 plot ###
kriging_11_data_fd = flowDuration(kriging_11_data_su)
kriging_11_data_fd.dropna(inplace=True)

plt_conf = {}
# plt_conf["label"] = 'KR11x8'
plt_conf["color"] = '#16ba07'
plots.append((kriging_11_data_fd, plt_conf))

outfile_hd = current.config["output_path"] +     "model/streamflow/passirio/seasonal/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_summer_kr_kr11_rea_obs_hd." + output_format
createPlot(plots, "Exceedance Probability", "Streamflow $[m^3/h]$", outfile_hd, #label="(b.4)",
           y_lim_min=0.7, y_lim_max=250, plot_legend=False, scale_factor=1, yscale='log',
           height=60, width=90, my_dpi=600)

outfile = current.config["output_path"] + "model/streamflow/passirio/seasonal/" +     "model_streamflow_passirio_plan_hourly_exceedance_curve_summer_kr_kr11_rea_obs." + output_format
createPlot(plots, "Exceedance Probability", "Streamflow $[m^3/h]$", outfile, #label="(b.4)",
           y_lim_min=0.7, y_lim_max=250, plot_legend=False, scale_factor=1, yscale='log',
           height=60, width=90, my_dpi=50)


# In[ ]:


# ENTIRE PERIOD NASH

from datetime import datetime
start_date_str = "2013-10-01T01:00:00"
end_date_str = "2019-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

kriging_nash = evaluateNash(
    obs_data[start_date:end_date], kriging_data[start_date:end_date], round_el=2)
print("KR1x1 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(kriging_nash))

kriging_11_nash = evaluateNash(
    obs_data[start_date:end_date], kriging_11_data[start_date:end_date], round_el=2)
print("KR11x8 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(kriging_11_nash))

rea_nash = evaluateNash(
    obs_data[start_date:end_date], rea_data[start_date:end_date], round_el=2)
print("REA11x8 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(rea_nash))


# In[ ]:


# CALIBRATION PERIOD NASH

from datetime import datetime
start_date_str = "2013-10-01T01:00:00"
end_date_str = "2017-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

kriging_nash = evaluateNash(
    obs_data[start_date:end_date], kriging_data[start_date:end_date], round_el=2)
print("KR1x1 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(kriging_nash))

kriging_11_nash = evaluateNash(
    obs_data[start_date:end_date], kriging_11_data[start_date:end_date], round_el=2)
print("KR11x8 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(kriging_11_nash))

rea_nash = evaluateNash(
    obs_data[start_date:end_date], rea_data[start_date:end_date], round_el=2)
print("REA11x8 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(rea_nash))


# In[ ]:


# VALIDATION PERIOD NASH

from datetime import datetime
start_date_str = "2017-10-01T01:00:00"
end_date_str = "2019-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

kriging_nash = evaluateNash(
    obs_data[start_date:end_date], kriging_data[start_date:end_date], round_el=2)
print("KR1x1 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(kriging_nash))

kriging_11_nash = evaluateNash(
    obs_data[start_date:end_date], kriging_11_data[start_date:end_date], round_el=2)
print("KR11x8 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(kriging_11_nash))

rea_nash = evaluateNash(
    obs_data[start_date:end_date], rea_data[start_date:end_date], round_el=2)
print("REA11x8 NASH from " + start_date_str +
      " to " + end_date_str + ": " + str(rea_nash))

