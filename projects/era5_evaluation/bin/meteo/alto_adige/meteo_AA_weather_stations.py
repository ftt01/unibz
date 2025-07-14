#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## DESCRIPTION
# 


# In[ ]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )


# In[ ]:


from lib import *


# In[ ]:


wdir = "/home/daniele/documents/github/ftt01/phd/projects/era5_evaluation/"
current = DataCollector(configPath=wdir + "etc/conf/")


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


## GROUND STATIONS DATASET ##
# data
precipitation_gs_path = "/media/windows/projects/era5_bias/00_data/meteo/aa/P_AltoAdige.in"

data_tot = pd.read_csv( precipitation_gs_path, header=0, index_col=0, parse_dates=True )
data_tot.replace(-999,np.NaN, inplace=True)
data_tot.index.name = "datetime"

# metadata
precipitation_gs_metadata = "/media/windows/projects/era5_bias/00_data/meteo/aa/AA_stations_metadata.csv"
metadata_tot = pd.read_csv( precipitation_gs_metadata, header=0 )


# In[ ]:


metadata_tot


# In[ ]:


precipitation_gs = metadata_tot[metadata_tot['flagP']==1][['ID','Elevation']].set_index('ID').rename(columns={'Elevation':'precipitation'})
temperature_gs = metadata_tot[metadata_tot['flagT']==1][['ID','Elevation']].set_index('ID').rename(columns={'Elevation':'temperature'})


# In[ ]:


xx = pd.concat( [precipitation_gs, temperature_gs], axis=1 )

plt.hist([xx['precipitation'], xx['temperature']], 25, label=['precipitation', 'temperature'])
plt.legend(loc='upper right')
# plt.show()


# In[ ]:


output_path = current.config["output_path"] + "meteo/alto_adige/"
mkNestedDir(output_path)

##
output_file = output_path + "gs_histograph_vsElevation.tiff"

c_fig, c_axs = instantiatePlot( 'Elevation [m]', 'N. of stations' )
c_axs.hist([xx['precipitation'], xx['temperature']], bins=np.arange(0,3501,250), color=['y','g'], label=['precipitation','temperature'])
c_axs.set_ylim(0,20)
c_axs.legend()
plt.xticks(np.arange(0,3500,250))
plt.yticks(np.arange(0,31,2))
plt.tight_layout()
c_fig.savefig(
    output_file, 
    format='tiff',
    facecolor='w',
    dpi=300)

plt.close(fig=c_fig)

##

output_file_hd = output_path + "gs_histograph_vsElevation_HD.tiff"

c_fig, c_axs = instantiatePlot( 'Elevation [m]', 'N. of stations' )
c_axs.hist([xx['precipitation'], xx['temperature']], bins=np.arange(0,3501,250), color=['y','g'], label=['precipitation','temperature'])
c_axs.set_ylim(0,20)
c_axs.legend()
plt.xticks(np.arange(0,3500,250))
plt.yticks(np.arange(0,31,2))
plt.tight_layout()
c_fig.savefig(
    output_file_hd, 
    format='tiff',
    facecolor='w',
    dpi=600)

plt.close(fig=c_fig)

