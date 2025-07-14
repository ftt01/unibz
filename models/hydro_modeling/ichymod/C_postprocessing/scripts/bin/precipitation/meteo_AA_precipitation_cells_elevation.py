#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## DESCRIPTION
# Script to plot precipitation cells bias against elevation.


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
precipitation_rea_path = "/media/windows/data/GFS_models/ECMWF/ERA5Land-reanalysis/derivatives/ptot/hourly_ts/"

# to consider only AA cells 
list_of_cells = []

precipitation_df_rea = pd.DataFrame()
precipitation_box_rea = pd.DataFrame()

p_file_tot = glob.glob( precipitation_rea_path + '*.csv' )

for p_file in p_file_tot:
    data_tot = pd.read_csv( p_file, header=0, index_col=0,         skiprows=4, parse_dates=True, names=[ os.path.basename(p_file)[:-4] ])
    data_tot = data_tot[start_date:end_date]
    data_tot[data_tot == -999] = None
    precipitation_df_rea = pd.concat([precipitation_df_rea, data_tot],axis=1)
    list_of_cells.append(os.path.basename(p_file)[:-4])

# # spatial mean over all cells
# precipitation_rea_spatial_mean = precipitation_df_rea.sum(axis=1)

# # temporal mean over all cells
# precipitation_rea_temporal_mean = precipitation_df_rea.mean(axis=0)
# # temporal ECDF
# precipitation_rea_temporal_ecdf = evaluateECDF( precipitation_rea_temporal_mean )


# In[ ]:


## KRIGING 11X8 DATASET ##
precipitation_kr11_path = "/media/windows/projects/era5_bias/OLD/comparison/scripts/kriging/AltoAdige/P/"
    
precipitation_df_kr11 = pd.DataFrame()
precipitation_box_kr11 = pd.DataFrame()

p_file_tot = glob.glob( precipitation_kr11_path + '*.csv' )

for p_file in p_file_tot:
    if os.path.basename(p_file)[:-4] in list_of_cells:
        data_tot = pd.read_csv( p_file, header=0, index_col=0,             skiprows=4, parse_dates=True, names=[ os.path.basename(p_file)[:-4] ])
        data_tot = data_tot[start_date:end_date]
        data_tot[data_tot == -999] = None
        precipitation_df_kr11 = pd.concat([precipitation_df_kr11, data_tot],axis=1)

# # spatial mean over all cells
# precipitation_kr11_spatial_mean = precipitation_df_kr11.sum(axis=1)

# # temporal mean over all cells
# precipitation_kr11_temporal_mean = precipitation_df_kr11.mean(axis=0)
# # temporal ECDF
# precipitation_kr11_temporal_ecdf = evaluateECDF( precipitation_kr11_temporal_mean )


# In[ ]:


precipitation_bias = precipitation_df_rea - precipitation_df_kr11


# In[ ]:


bias_df = pd.DataFrame( precipitation_bias.resample('Y').sum().mean(), columns=['bias'] )


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


# data.set_index('elevation', inplace=True)


# In[ ]:


# plots = []

# ### rea 11x8 plot ###
# plt_conf = {}
# # plt_conf["label"] = 'Reanalysis 11x8'
# # plt_conf["color"] = '#e66101'
# plots.append( (data, plt_conf) )

# output_file = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/yearly/meteo_" + 'precipitation_AA_yearly_elevation_bias.' + output_format
# createPlot( plots, "Elevation $[m]$", "Precipitation bias $[mm]$", output_file, scale_factor=0.5, my_dpi=50 )
# # 
# output_file_hd = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/yearly/meteo_" + 'precipitation_AA_yearly_elevation_bias_HD.' + output_format
# createPlot( plots, "Elevation $[m]$", "Precipitation bias $[mm]$", output_file_hd, scale_factor=0.5, my_dpi=600 )


# In[ ]:


fig, axs = instantiatePlot( "Precipitation bias $[mm]$", "Elevation $[m]$" )

axs.scatter( data['bias'], data['elevation'], s=10 )

output_file = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/yearly/meteo_" + 'precipitation_AA_yearly_elevation_bias.' + output_format
mkNestedDir(getPathFromFilepath(output_file))
fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50 )

output_file_hd = current.config["output_path"] + "meteo/precipitation/" + basin_str + "/yearly/meteo_" + 'precipitation_AA_yearly_elevation_bias_HD.' + output_format
mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig( output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600 ) 


# 
