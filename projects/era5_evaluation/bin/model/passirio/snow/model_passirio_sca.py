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


## OBSERVED ##
fileName_obs = "/media/windows/projects/era5_bias/00_data/vectorial_data/MODIS_SCA.txt"

df_obs = pd.read_csv(fileName_obs, header=0, index_col=0, parse_dates=True, delimiter=r"\s+")
df_obs_series = df_obs['SCA']


# In[ ]:


### simulation selection #############################################################################

kriging_data = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "best_merano_cal_val"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

kriging_data.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
model_sca_passirio_mean_kr = kriging_data.model_sca_passirio.resample('D').mean() * 100


# In[ ]:


### simulation selection #############################################################################

kriging_11_data = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "best_merano_cal_val"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

kriging_11_data.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
model_sca_passirio_mean_kr11 = kriging_11_data.model_sca_passirio.resample('D').mean() * 100


# In[ ]:


### simulation selection #############################################################################

reanalysis_data = DataCollector(configPath=wdir + "etc/conf/")

current_phase = "best_merano_cal_val"
current_basin = "passirio"
current_type = "reanalysis"
current_node = "merano"

reanalysis_data.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
model_sca_passirio_mean_rea = reanalysis_data.model_sca_passirio.resample('D').mean() * 100


# In[ ]:


fig, axs = instantiatePlot("Time $[days]$", "SCA $[-]$", output_format='tiff')

axs.scatter(df_obs_series.index, df_obs_series.values, s=10, label='observed', color='#fdb863')

axs.plot(model_sca_passirio_mean_rea, label='REA11x8', linestyle="solid", color='#e66101')
axs.plot(model_sca_passirio_mean_kr, label='KR1x1', linestyle="solid", color='#8078bc')
axs.plot(model_sca_passirio_mean_kr11, label='KR11x8', linestyle="solid", color='#5e3c99')

axs.legend(loc='lower right')

output_file = current.config["output_path"] + "model/sca/passirio/daily/" + "model_sca_passirio_daily." + output_format

mkNestedDir(getPathFromFilepath(output_file))
fig.savefig(output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50)

output_file_hd = current.config["output_path"] + "model/sca/passirio/daily/" + "model_sca_passirio_daily_hd." + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig(output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600)


# In[ ]:


from datetime import datetime
start_date_str = "2015-10-01T01:00:00"
end_date_str = "2016-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

fig, axs = instantiatePlot("Time $[days]$", "SCA $[-]$", output_format='tiff')

axs.scatter(df_obs_series[start_date:end_date].index, df_obs_series[start_date:end_date].values, s=10, label='observed', color='#fdb863')

axs.plot(model_sca_passirio_mean_rea[start_date:end_date], label='REA11x8', linestyle="solid", color='#e66101')
axs.plot(model_sca_passirio_mean_kr[start_date:end_date], label='KR1x1', linestyle="solid", color='#8078bc')
axs.plot(model_sca_passirio_mean_kr11[start_date:end_date], label='KR11x8', linestyle="solid", color='#5e3c99')

axs.legend(loc='lower right')

output_file = current.config["output_path"] + "model/sca/passirio/daily/" + "model_sca_passirio_daily_20152016." + output_format

mkNestedDir(getPathFromFilepath(output_file))
fig.savefig(output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50)

output_file_hd = current.config["output_path"] + "model/sca/passirio/daily/" + "model_sca_passirio_daily_20152016_hd." + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig(output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600)


# In[ ]:


from datetime import datetime
start_date_str = "2016-10-01T01:00:00"
end_date_str = "2017-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

fig, axs = instantiatePlot("Time $[days]$", "SCA $[-]$", output_format='tiff')

axs.scatter(df_obs_series[start_date:end_date].index, df_obs_series[start_date:end_date].values, s=10, label='observed', color='#fdb863')

axs.plot(model_sca_passirio_mean_rea[start_date:end_date], label='REA11x8', linestyle="solid", color='#e66101')
axs.plot(model_sca_passirio_mean_kr[start_date:end_date], label='KR1x1', linestyle="solid", color='#8078bc')
axs.plot(model_sca_passirio_mean_kr11[start_date:end_date], label='KR11x8', linestyle="solid", color='#5e3c99')

axs.legend(loc='lower right')

output_file = current.config["output_path"] + "model/sca/passirio/daily/" + "model_sca_passirio_daily_20162017." + output_format

mkNestedDir(getPathFromFilepath(output_file))
fig.savefig(output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50)

output_file_hd = current.config["output_path"] + "model/sca/passirio/daily/" + "model_sca_passirio_daily_20162017_hd." + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig(output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600)


# In[ ]:


from datetime import datetime
start_date_str = "2017-10-01T01:00:00"
end_date_str = "2018-09-30T23:00:00"
start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%S')
end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')

fig, axs = instantiatePlot("Time $[days]$", "SCA $[-]$", output_format='tiff')

axs.scatter(df_obs_series[start_date:end_date].index, df_obs_series[start_date:end_date].values, s=10, label='observed', color='#fdb863')

axs.plot(model_sca_passirio_mean_rea[start_date:end_date], label='REA11x8', linestyle="solid", color='#e66101')
axs.plot(model_sca_passirio_mean_kr[start_date:end_date], label='KR1x1', linestyle="solid", color='#8078bc')
axs.plot(model_sca_passirio_mean_kr11[start_date:end_date], label='KR11x8', linestyle="solid", color='#5e3c99')

axs.legend(loc='lower right')

output_file = current.config["output_path"] + "model/sca/passirio/daily/" + "model_sca_passirio_daily_20172018." + output_format

mkNestedDir(getPathFromFilepath(output_file))
fig.savefig(output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50)

output_file_hd = current.config["output_path"] + "model/sca/passirio/daily/" + "model_sca_passirio_daily_20172018_hd." + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig(output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600)


# In[ ]:




