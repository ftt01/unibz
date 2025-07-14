#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )


# In[2]:


from lib import *


# In[3]:


wdir = "/media/windows/projects/meteo_forecast_water_demand/"

output_path = wdir + "meteo/era5/download/original/"

spatial_resolution = 0.1

bbox = [ 45.67, 10.39, 47.09, 12.48 ]


# In[ ]:


mkNestedDir( output_path )
os.chdir( output_path )

## ERA5-Land
lat_min = round( 0.05 + bbox[0] - bbox[0] % spatial_resolution, 2 )
lat_max = round( 0.05 + bbox[2] - bbox[2] % spatial_resolution + spatial_resolution, 2 )
lon_min = round( bbox[1] - bbox[1] % spatial_resolution, 2 )
lon_max = round( bbox[3] - bbox[3] % spatial_resolution + spatial_resolution, 2 )


# In[ ]:


import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-land',
    {
        'variable': [
            'surface_solar_radiation_downwards'
        ],
        'year': [
            '2013', '2014','2015','2016','2017','2018','2019','2020'
        ],
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
        'area': [
            lat_min, lon_min, lat_max,
            lon_max,
        ],
        'format': 'grib',
    },
    '20132020.grib')


# In[ ]:


# variables = ['2m_dewpoint_temperature', '2m_temperature', 'surface_net_solar_radiation','surface_pressure', 'total_precipitation']
# years = ['2013','2014','2015','2016','2017','2018','2019']
# months = ['1','2','3','4','5','6','7','8','9','10','11','12']
# days = ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28','29','30','31']
# hours = ['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']


# In[ ]:


# import cdsapi

# c = cdsapi.Client()

# c.retrieve(
#     'reanalysis-era5-land',
#     {
#         'variable': [
#             '2m_temperature'
#         ],
#         'year': [
#             '2019'
#         ],
#         'month': [
#             '01'
#         ],
#         'day': [
#             '01'
#         ],
#         'time': [
#             '00:00'
#         ],
#         'area': [
#             46.15, 11, 45.95,
#             11.2,
#         ],
#         'format': 'grib',
#     },
#     '2019_01_01_0000_2m_temperature.grib')

