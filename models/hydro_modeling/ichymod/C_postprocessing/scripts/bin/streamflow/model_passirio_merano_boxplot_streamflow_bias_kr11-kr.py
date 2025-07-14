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

kriging_data = DataCollector()

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging"
current_node = "merano"

kriging_data.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################


# In[ ]:


### simulation selection #############################################################################

kriging11_data = DataCollector()

current_phase = "calibration_best_merano"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

kriging11_data.retrieveData(current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################


# In[ ]:


data_kr_temporal_mean = kriging_data.model_flow.resample('MS').mean()
data_kr11_temporal_mean = kriging11_data.model_flow.resample('MS').mean()
data_monthly_mean = data_kr11_temporal_mean - data_kr_temporal_mean


# In[ ]:


output_path = current.config["output_path"] + "model/streamflow/passirio/monthly/"     + "model_streamflow_passirio_merano_boxplotBias_kr11-kr." + output_format

createBoxPlot(data_monthly_mean,  "Time $[month]$", "Streamflow bias $[m^3/month]$",
              output_path, period='MS', output_format=output_format, my_dpi=50)

output_path_hd = current.config["output_path"] + "model/streamflow/passirio/monthly/"     + "model_streamflow_passirio_merano_boxplotBias_kr11-kr_HD." + output_format

createBoxPlot(data_monthly_mean,  "Time $[month]$", "Streamflow bias $[m^3/month]$",
              output_path_hd, period='MS', output_format=output_format, my_dpi=600)


# In[ ]:




