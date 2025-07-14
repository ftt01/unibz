#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## DESCRIPTION
# Script to plot temperature cells bias against elevation.


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
import glob


# In[ ]:


## SETUP
basin = 'AA'
# for output name
basin_str = 'alto_adige'

start_date_str = "2010-01-01T00:00:00"
end_date_str = "2019-12-31T23:00:00"
start_date = dt.datetime.strptime( start_date_str, '%Y-%m-%dT%H:%M:%S' )
end_date = dt.datetime.strptime( end_date_str, '%Y-%m-%dT%H:%M:%S' )


# In[ ]:


## REANALYSIS DATASET ##
temperature_rea_path = "/media/windows/data/GFS_models/ECMWF/ERA5Land-reanalysis/derivatives/t2m/"

list_of_cells = []
temperature_df_rea = pd.DataFrame()

t_file_tot = glob.glob( temperature_rea_path + '*.csv' )

for t_file in t_file_tot:
    data_tot = pd.read_csv(t_file,index_col=0,parse_dates=True,skiprows=4,names=[ os.path.basename(t_file)[:-4] ])
    data_tot=data_tot[start_date:end_date]
    data_tot[data_tot == -999] = None
    temperature_df_rea=pd.concat([temperature_df_rea, data_tot],axis=1)
    list_of_cells.append(os.path.basename(t_file)[:-4])

# spatial mean over all cells
# temperature_rea_spatial_mean = temperature_df_rea.mean(axis=1)

# # temporal mean over all cells
# temperature_df_rea_temporal_mean = temperature_df_rea.mean(axis=0)
# # temporal ECDF
# temperature_df_rea_temporal_ecdf = evaluateECDF( temperature_df_rea_temporal_mean )


# In[ ]:


## KRIGING 11X8 DATASET ##
temperature_kr11_path = "/media/windows/projects/era5_bias/OLD/comparison/scripts/kriging/AltoAdige/TMEAN/"
         
temperature_df_kr11 = pd.DataFrame()

t_file_tot = glob.glob( temperature_kr11_path + '*.csv')

for t_file in t_file_tot:
    if os.path.basename(t_file)[:-4] in list_of_cells:
        data_tot = pd.read_csv(t_file,index_col=0,parse_dates=True,skiprows=4,names=[ os.path.basename(t_file)[:-4] ])
        data_tot = data_tot[start_date:end_date]
        data_tot[data_tot == -999] = None
        temperature_df_kr11 = pd.concat([temperature_df_kr11, data_tot],axis=1)

# spatial mean over all cells
# temperature_kr11_spatial_mean = temperature_df_kr11.mean(axis=1)

# # temporal mean over all cells
# temperature_df_kr11_temporal_mean = temperature_df_kr11.mean(axis=0)
# # temporal ECDF
# temperature_df_kr11_temporal_ecdf = evaluateECDF( temperature_df_kr11_temporal_mean )


# In[ ]:


temperature_bias = temperature_df_rea - temperature_df_kr11


# In[ ]:


bias_df = pd.DataFrame( temperature_bias.resample('Y').mean().mean(), columns=['bias'] )


# In[ ]:


el = "/media/windows/OLD/data/data/GFS_models/ECMWF/ERA5Land-reanalysis/ECMWF_grid_Adige_river.csv"
tmp = pd.read_csv( el )
tmp.set_index( "ID", inplace=True )


# In[ ]:


elev = []
bias = []

for i in bias_df.index:
    # print(i)
    elev.append( tmp.loc[int(i)]['Elev'] )
    bias.append( bias_df.loc[str(i)].values[0] )


# In[ ]:


data = pd.DataFrame(elev, columns=['elevation'])
data['bias'] = bias


# In[ ]:


data[data['elevation']==-999] = None
data.dropna(inplace=True)


# In[ ]:


fig, axs = instantiatePlot( "Temperature bias $[mm]$", "Elevation $[m]$" )

axs.scatter( data['bias'], data['elevation'], s=10 )

output_file = current.config["output_path"] + "meteo/temperature/" + basin_str + "/yearly/meteo_" + 'temperature_AA_yearly_elevation_bias.' + output_format
mkNestedDir(getPathFromFilepath(output_file))
fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/temperature/" + basin_str + "/yearly/meteo_" + 'temperature_AA_yearly_elevation_bias_HD.' + output_format
mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig( output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600 ) 


# 
