#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys

lib_dir = "/mnt/c/Users/daniele/Documents/GitHub/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )


# In[2]:


from lib import *


# In[3]:


wdir = "/media/windows/projects/meteo_forecast_water_demand/"

output_path = wdir + "meteo/era5/postprocessed/tmp/"

variables = ['2m_temperature', 'surface_net_solar_radiation',
             'total_precipitation', 'relative_humidity', 'surface_solar_radiation_downwards']

# variables = ['total_precipitation']

files = ['adaptor.mars.internal-1649846628.7378805-12259-5-c3bd14ea-6275-49b2-ad93-ce719c52b729.grib',
         'adaptor.mars.internal-1649846659.2984114-2675-7-cb7f4150-4ef2-4b09-839c-45d52e5a702a.grib',
         'adaptor.mars.internal-1649847657.5886977-4143-18-fb0a7dff-6e38-485c-8cb0-c7861a500c77.grib',
         'adaptor.mars.internal-1649863332.5546749-19721-6-59931d26-79e4-456f-a979-db42e29c55d7.grib']

tolerance = 0.001

# meta = [{'id': 1, 'coordinates': (46.15, 11.0)},
#         {'id': 2, 'coordinates': (46.15, 11.1)},
#         {'id': 3, 'coordinates': (46.15, 11.2)},
#         {'id': 4, 'coordinates': (46.05, 11.0)},
#         {'id': 5, 'coordinates': (46.05, 11.1)},
#         {'id': 6, 'coordinates': (46.05, 11.2)},
#         {'id': 7, 'coordinates': (45.95, 11.0)},
#         {'id': 8, 'coordinates': (45.95, 11.1)},
#         {'id': 9, 'coordinates': (45.95, 11.2)}]

meta = [{'id': 10, 'coordinates': (46.05, 11.1)}]


# In[4]:


def rel_humidity( t, td ):
    return round( 10**( 2 - (t - td)/31.25 ),2 )


# In[5]:


from eccodes import *
import xarray as xr


# In[6]:


# for file in files:

#     ds = xr.open_dataset(wdir + 'meteo/era5/original/' + file, engine='cfgrib')

#     dd = ds.to_dask_dataframe()

#     tmp = dd.compute()
#     # tmp.dropna(inplace=True)

#     for m in meta:
#         current_id = m['id']
#         local = tmp[tmp['latitude'] >= m['coordinates'][0] - tolerance]
#         local = local[local['latitude'] <= m['coordinates'][0] + tolerance]
#         local = local[local['longitude'] >= m['coordinates'][1] - tolerance]
#         local = local[local['longitude'] <= m['coordinates'][1] + tolerance]
#         # local.dropna(inplace=True)

#         for variable in variables:
#             if variable == '2m_temperature':
#                 var = 't2m'
#                 correction_factor = -273.15
#                 var_name = 'temperature'

#                 current_data = local[['valid_time', var]]
#                 current_data = current_data.rename(
#                     columns={'valid_time': 'datetime', var: 'values'})
#                 current_data = current_data.set_index('datetime')

#                 current_data['values'] = [ round(float(c)+correction_factor,2) for c in current_data['values'] ]

#             elif variable == 'total_precipitation':
#                 var = 'tp'
#                 var_name = 'precipitation'

#                 current_data = local[['valid_time', var]]
#                 current_data = current_data.rename(
#                     columns={'valid_time': 'datetime', var: 'values'})
#                 current_data = current_data.set_index('datetime')

#                 # transform from cumulate to instant precipitation
#                 cum = current_data['values'].replace(np.nan,0)
#                 cum = [ round(c*1000,2) for c in cum ]
 
#                 i = 0
#                 inst = []
#                 while i < len(cum):
#                     if i % 24 == 0:
#                         inst.append( float(cum[i]) )
#                     else:
#                         inst.append( abs(float(cum[i] - cum[i-1])) )
#                     i = i + 1
                
#                 current_data['values'] = [round(el,2) for el in inst]

#                 del [cum,inst]

#             elif variable == 'surface_net_solar_radiation':
#                 var = 'ssr'
#                 var_name = 'surface_net_solar_radiation'
#                 upper_threshold = 1500.0

#                 current_data = local[['valid_time', var]]
#                 current_data = current_data.rename(
#                     columns={'valid_time': 'datetime', var: 'values'})
#                 current_data = current_data.set_index('datetime')

#                 # transform from cumulate to instant radiation
#                 cum = current_data['values'].replace(np.nan,0)
#                 cum = [ c/1000 for c in cum ]
#                 i = 0
#                 inst = []
#                 while i < len(cum):
#                     if i % 24 == 0:
#                         t_data = float(cum[i])
#                     else:
#                         t_data = abs(float(cum[i] - cum[i-1]))
                    
#                     if t_data > upper_threshold:
#                         t_data = 0.0
#                     inst.append( t_data )

#                     i = i + 1

#                 current_data['values'] = [round(el,2) for el in inst]

#                 del [cum,inst]
            
#             elif variable == 'surface_solar_radiation_downwards':
#                 var = 'ssrd'
#                 var_name = 'surface_solar_radiation_downwards'
#                 upper_threshold = 1500.0

#                 current_data = local[['valid_time', var]]
#                 current_data = current_data.rename(
#                     columns={'valid_time': 'datetime', var: 'values'})
#                 current_data = current_data.set_index('datetime')

#                 # transform from cumulate to instant precipitation
#                 cum = current_data['values'].replace(np.nan,0)
#                 cum = [ c/1000 for c in cum ]
#                 i = 0
#                 inst = []
#                 while i < len(cum):
#                     if i % 24 == 0:
#                         t_data = float(cum[i])
#                     else:
#                         t_data = abs(float(cum[i] - cum[i-1]))
                    
#                     if t_data > upper_threshold:
#                         t_data = 0.0
#                     inst.append( t_data )

#                     i = i + 1

#                 current_data['values'] = [round(el,2) for el in inst]

#                 del [cum,inst]

#             elif variable == 'relative_humidity':
#                 var_td = 'd2m'
#                 var_t = 't2m'
#                 var_name = 'relative_humidity'

#                 current_data_td = local[['valid_time', var_td]]
#                 current_data_td = current_data_td.rename(
#                     columns={'valid_time': 'datetime', var_td: 'values'})
#                 current_data_td = current_data_td.set_index('datetime')

#                 current_data_t = local[['valid_time', var_t]]
#                 current_data_t = current_data_t.rename(
#                     columns={'valid_time': 'datetime', var_t: 'values'})
#                 current_data_t = current_data_t.set_index('datetime')

#                 current_data = pd.DataFrame(index=current_data_t.index)
#                 current_data['values'] = [ rel_humidity(float(current_data_t.loc[idx]),float(current_data_td.loc[idx])) for idx in current_data.index ]

#             else:
#                 continue

#             current_output_path = output_path + var_name + '/'
#             mkNestedDir(current_output_path)
#             current_data.to_csv(current_output_path + '{id}_{start_date}_{end_date}.csv'.format(id=current_id,
#             start_date=str(current_data.index[0]).replace('-', '').replace(':', '').replace(' ', ''),
#             end_date=str(current_data.index[-1]).replace('-', '').replace(':', '').replace(' ', '')))

#         del [current_data,local]
#     del [ds,dd,tmp]


# In[7]:


ds = xr.open_dataset(wdir + 'meteo/era5/download/original/' + '20132020.grib', engine='cfgrib')

dd = ds.to_dask_dataframe()

tmp = dd.compute()
# tmp.dropna(inplace=True)

for m in meta:
    current_id = m['id']
    local = tmp[tmp['latitude'] >= m['coordinates'][0] - tolerance]
    local = local[local['latitude'] <= m['coordinates'][0] + tolerance]
    local = local[local['longitude'] >= m['coordinates'][1] - tolerance]
    local = local[local['longitude'] <= m['coordinates'][1] + tolerance]
    # local.dropna(inplace=True)

    # break
    # local = local.compute()

    var = 'ssrd'
    var_name = 'surface_solar_radiation_downwards'
    upper_threshold = 1500.0

    current_data = local[['valid_time', var]]
    current_data = current_data.rename(
        columns={'valid_time': 'datetime', var: 'values'})
    current_data = current_data.set_index('datetime')

    # transform from cumulate to instant precipitation
    cum = current_data['values'].replace(np.nan,0)
    cum = [ c/1000 for c in cum ]
    i = 0
    inst = []
    while i < len(cum):
        if i % 24 == 0:
            t_data = float(cum[i])
        else:
            t_data = abs(float(cum[i] - cum[i-1]))
        
        if t_data > upper_threshold:
            t_data = 0.0
        inst.append( t_data )

        i = i + 1

    current_data['values'] = [round(el,2) for el in inst]

    del [cum,inst]

    current_output_path = output_path + var_name + '/'
    mkNestedDir(current_output_path)
    current_data.to_csv(current_output_path + '{id}_{start_date}_{end_date}.csv'.format(id=current_id,
    start_date=str(current_data.index[0]).replace('-', '').replace(':', '').replace(' ', ''),
    end_date=str(current_data.index[-1]).replace('-', '').replace(':', '').replace(' ', '')))

    del [current_data,local]
# del [ds,dd,tmp]


# In[ ]:


# current_data[-2000:-1800].plot()


# In[ ]:


# inst = inst[-2000:-1800]


# In[ ]:


# # cum = [ 0,0,0,0.1,0.1,0.1,0.2,0.5,0.5,2,2,2,2,2,2,2,2,2,2,2,2,2,2.5,2.5,0,0,0,0.1,0.1,0.1,0.2,0.5,0.5,2,2,2,2,2,2,2,2,2,2,2,2,2,2.5,2.5 ]
# i = 0
# inst = []
# while i < len(cum):
#     if i % 24 == 0:
#         inst.append( float(cum[i]) )
#     else:
#         inst.append( abs(float(cum[i] - cum[i-1])) )
#     i = i + 1

# # # current_data['values'] = [round(el,2) for el in inst]


# In[ ]:


# pd.DataFrame(cum).plot()


# In[ ]:


# inst = inst[-2000:-1800]
# pd.DataFrame(inst).plot()


# In[ ]:


for m in meta:
    current_id = m['id']
    print(current_id)

    data = pd.DataFrame()

    output_dirs = glob.glob( output_path + '*/' )
    for var_dirs in output_dirs:
        var = var_dirs.split('/')[-2]
        print(var)
        tmp = glob.glob( var_dirs + '/{id}_*'.format(id=current_id))
        var_data = None
        for f in tmp:
            # print('Reading: ' + f)
            c_data = pd.read_csv( f, parse_dates=True, index_col=0 )
            c_data.rename(columns={'values':var})

            try:
                var_data = append_data(var_data, c_data)
            except:
                # print('here')
                var_data = c_data
                var_data.rename(columns={'values':var})

            del [c_data]
        
        data[var] = var_data
        del [var_data]
    
    data.to_csv( output_path + '{id}.csv'.format(id=current_id), sep=';' )
    # del [data]


# In[ ]:


data[['surface_net_solar_radiation']].describe()


# In[ ]:


data[['surface_net_solar_radiation']].describe()


# In[ ]:


# data[['precipitation']][-600:-500].plot()


# In[ ]:





# In[ ]:


data_obs = pd.DataFrame()


# In[ ]:


current_data = pd.read_csv(wdir + '/meteo/historical/T0129.csv', header=None)

id_start = int(current_data[current_data[0]=='00:00:00 01/01/2013'].index[0])
id_end = int(current_data[current_data[0]=='23:00:00 31/12/2020'].index[0])
print( "ID start_date: " + str(id_start) )
print( "ID end_date: " + str(id_end) )

data_laste = pd.DataFrame( current_data.loc[id_start:id_end][1] )
data_laste.index = pd.to_datetime(current_data.loc[id_start:id_end][0],format='%H:%M:%S %d/%m/%Y')

data_laste = data_laste.resample('H').sum()

data_obs['surface_total_radiation_new'] = data_laste


# In[ ]:


current_data = pd.read_csv(wdir + '/meteo/historical/radiazione.csv', header=None)

id_start = int(current_data[current_data[0]== '00:00:00 01/01/2013'].index[0])
id_end = int(current_data[current_data[0]== '23:00:00 31/12/2020'].index[0])
print( "ID start_date: " + str(id_start) )
print( "ID end_date: " + str(id_end) )

data_laste = pd.DataFrame( current_data.loc[id_start:id_end][1] )
data_laste.index = pd.to_datetime(current_data.loc[id_start:id_end][0],format='%H:%M:%S %d/%m/%Y')

data_laste = data_laste.resample('H').sum()

data_obs['surface_total_radiation'] = data_laste


# In[ ]:


current_data = pd.read_csv(wdir + '/meteo/historical/precipitation.csv', header=None)

id_start = int(current_data[current_data[0]== '00:00:00 01/01/2013'].index[0])
id_end = int(current_data[current_data[0]== '23:00:00 31/12/2020'].index[0])
print( "ID start_date: " + str(id_start) )
print( "ID end_date: " + str(id_end) )

data_laste = pd.DataFrame( current_data.loc[id_start:id_end][1] )
data_laste.index = pd.to_datetime(current_data.loc[id_start:id_end][0],format='%H:%M:%S %d/%m/%Y')

data_laste = data_laste.resample('H').sum()

data_obs['precipitation'] = data_laste


# In[ ]:


current_data = pd.read_csv(wdir + '/meteo/historical/relative_humidity.csv', header=None)

id_start = int(current_data[current_data[0]== '00:00:00 01/01/2013'].index[0])
id_end = int(current_data[current_data[0]== '23:00:00 31/12/2020'].index[0])
print( "ID start_date: " + str(id_start) )
print( "ID end_date: " + str(id_end) )

data_laste = pd.DataFrame( current_data.loc[id_start:id_end][1] )
data_laste.index = pd.to_datetime(current_data.loc[id_start:id_end][0],format='%H:%M:%S %d/%m/%Y')

data_laste = data_laste.resample('H').mean()

data_obs['relative_humidity'] = data_laste


# In[ ]:


current_data = pd.read_csv(wdir + '/meteo/historical/temperature.csv', header=None)

id_start = int(current_data[current_data[0]== '00:00:00 01/01/2013'].index[0])
id_end = int(current_data[current_data[0]== '23:00:00 31/12/2020'].index[0])
print( "ID start_date: " + str(id_start) )
print( "ID end_date: " + str(id_end) )

data_laste = pd.DataFrame( current_data.loc[id_start:id_end][1] )
data_laste.index = pd.to_datetime(current_data.loc[id_start:id_end][0],format='%H:%M:%S %d/%m/%Y')

data_laste = data_laste.resample('H').mean()

data_obs['temperature'] = data_laste


# In[ ]:


data_obs[['surface_total_radiation_new']].describe()
# era5_laste = era5_laste.resample('H').mean()
# era5_laste.plot()


# In[ ]:


data_obs[['surface_total_radiation_new']].plot()


# In[ ]:


era5_laste = data[['precipitation']][dt.date(2013,6,9):dt.date(2013,6,11)]
# era5_laste = era5_laste.resample('H').mean()
era5_laste.plot()


# In[ ]:


data_obs[['surface_net_solar_radiation']][dt.date(2013,1,1):dt.date(2016,12,31)].describe()


# In[ ]:


# laste_radiazione.loc[47705:327982].plot()


# In[ ]:


# coeff = pd.DataFrame( era5_laste['surface_net_solar_radiation'] / 1000 / data_laste[1] )


# In[ ]:


# coeff[ (coeff[0] > 0) & (coeff[0] < 100) ][0:100].plot()


# In[ ]:


laste_data.drop(columns=2, inplace=True)


# In[ ]:


laste_data.rename(columns={1:'values'}, inplace=True)


# In[ ]:


laste_data.index.name = 'datetime'


# In[ ]:


laste_data.iloc[8000:15000][[0]].plot()


# In[ ]:


laste_data.describe()


# In[ ]:


# fid = open('/media/windows/projects/meteo_forecast_water_demand/meteo/era5/original/adaptor.mars.internal-1649846628.7378805-12259-5-c3bd14ea-6275-49b2-ad93-ce719c52b729.grib',"r")
# gid = codes_any_new_from_file(fid)


# In[ ]:


# codes_grib_get_data(gid)


# In[ ]:


# iterid = codes_keys_iterator_new(gid, 'time')


# In[ ]:


# while codes_keys_iterator_next(iterid):
#     keyname = codes_keys_iterator_get_name(iterid)
#     keyval = codes_get_string(gid, keyname)
#     print("%s = %s" % (keyname, keyval))


# In[ ]:


# fid = open('/media/windows/projects/meteo_forecast_water_demand/meteo/era5/1.grib',"r")
# gid = codes_any_new_from_file(fid)

# iterid = codes_keys_iterator_new(gid, 'time')

# while codes_keys_iterator_next(iterid):
#     keyname = codes_keys_iterator_get_name(iterid)
#     keyval = codes_get_string(gid, keyname)
#     print("%s = %s" % (keyname, keyval))


# In[ ]:


# iterid


# In[ ]:


# import cdsapi

# c = cdsapi.Client()

# c.retrieve(
#     'reanalysis-era5-land',
#     {
#         'variable': [
#             '2m_dewpoint_temperature', '2m_temperature', 'surface_net_solar_radiation',
#             'surface_pressure', 'total_precipitation',
#         ],
#         'year': [
#             '2019', '2020',
#         ],
#         'month': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#         ],
#         'day': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#             '13', '14', '15',
#             '16', '17', '18',
#             '19', '20', '21',
#             '22', '23', '24',
#             '25', '26', '27',
#             '28', '29', '30',
#             '31',
#         ],
#         'time': [
#             '00:00', '01:00', '02:00',
#             '03:00', '04:00', '05:00',
#             '06:00', '07:00', '08:00',
#             '09:00', '10:00', '11:00',
#             '12:00', '13:00', '14:00',
#             '15:00', '16:00', '17:00',
#             '18:00', '19:00', '20:00',
#             '21:00', '22:00', '23:00',
#         ],
#         'area': [
#             46.15, 11, 45.95,
#             11.2,
#         ],
#         'format': 'grib',
#     },
#     'download.grib')


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


# In[ ]:


# import cdsapi

# for variable in variables:
#     for year in years:
#         for month in months:
#             for day in days:
#                 for hour in hours:
                    
#                     try:
#                         c = cdsapi.Client()

#                         c.retrieve(
#                             'reanalysis-era5-land',
#                             {
#                                 'variable': [
#                                     '{var}'.format(var=variable)
#                                 ],
#                                 'year': [
#                                     '{y}'.format(y=year)
#                                 ],
#                                 'month': [
#                                     '{m}'.format(m=month)
#                                 ],
#                                 'day': [
#                                     '{d}'.format(d=day)
#                                 ],
#                                 'time': [
#                                     '{t}:00'.format(t=hour)
#                                 ],
#                                 'area': [
#                                     46.15, 11, 45.95,
#                                     11.2,
#                                 ],
#                                 'format': 'grib',
#                             },
#                             '{y}_{m}_{d}_{t}00_{var}.grib'.format(var=variable,y=year,m=month,d=day,t=hour))
#                     except:
#                         continue


# In[ ]:


os.chdir( wdir + "meteo/era5/original/" )


# In[ ]:


# variables = ['2m_temperature', 'surface_net_solar_radiation', 'total_precipitation']
# years = ['2010']
# months = ['1']
# days = ['01']
# hours = ['00']


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
            47.09, 10.39, 45.67,
            12.48,
        ],
        'format': 'grib',
    },
    '20132020.grib')


# In[ ]:


# import cdsapi

# c = cdsapi.Client()

# c.retrieve(
#     'reanalysis-era5-land',
#     {
#         'variable': [
#             '2m_dewpoint_temperature', '2m_temperature', 'surface_net_solar_radiation',
#             'total_precipitation',
#         ],
#         'year': [
#             '2010', '2011',
#         ],
#         'month': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#         ],
#         'day': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#             '13', '14', '15',
#             '16', '17', '18',
#             '19', '20', '21',
#             '22', '23', '24',
#             '25', '26', '27',
#             '28', '29', '30',
#             '31',
#         ],
#         'time': [
#             '00:00', '01:00', '02:00',
#             '03:00', '04:00', '05:00',
#             '06:00', '07:00', '08:00',
#             '09:00', '10:00', '11:00',
#             '12:00', '13:00', '14:00',
#             '15:00', '16:00', '17:00',
#             '18:00', '19:00', '20:00',
#             '21:00', '22:00', '23:00',
#         ],
#         'area': [
#             47.09, 10.39, 45.67,
#             12.48,
#         ],
#         'format': 'grib',
#     },
#     '20102011.grib')


# In[ ]:


# c = cdsapi.Client()

# c.retrieve(
#     'reanalysis-era5-land',
#     {
#         'variable': [
#             '2m_dewpoint_temperature', '2m_temperature', 'surface_net_solar_radiation',
#             'total_precipitation',
#         ],
#         'year': [
#             '2012', '2013',
#         ],
#         'month': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#         ],
#         'day': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#             '13', '14', '15',
#             '16', '17', '18',
#             '19', '20', '21',
#             '22', '23', '24',
#             '25', '26', '27',
#             '28', '29', '30',
#             '31',
#         ],
#         'time': [
#             '00:00', '01:00', '02:00',
#             '03:00', '04:00', '05:00',
#             '06:00', '07:00', '08:00',
#             '09:00', '10:00', '11:00',
#             '12:00', '13:00', '14:00',
#             '15:00', '16:00', '17:00',
#             '18:00', '19:00', '20:00',
#             '21:00', '22:00', '23:00',
#         ],
#         'area': [
#             47.09, 10.39, 45.67,
#             12.48,
#         ],
#         'format': 'grib',
#     },
#     '20122013.grib')


# In[ ]:


# c = cdsapi.Client()

# c.retrieve(
#     'reanalysis-era5-land',
#     {
#         'variable': [
#             '2m_dewpoint_temperature', '2m_temperature', 'surface_net_solar_radiation',
#             'total_precipitation',
#         ],
#         'year': [
#             '2014', '2015',
#         ],
#         'month': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#         ],
#         'day': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#             '13', '14', '15',
#             '16', '17', '18',
#             '19', '20', '21',
#             '22', '23', '24',
#             '25', '26', '27',
#             '28', '29', '30',
#             '31',
#         ],
#         'time': [
#             '00:00', '01:00', '02:00',
#             '03:00', '04:00', '05:00',
#             '06:00', '07:00', '08:00',
#             '09:00', '10:00', '11:00',
#             '12:00', '13:00', '14:00',
#             '15:00', '16:00', '17:00',
#             '18:00', '19:00', '20:00',
#             '21:00', '22:00', '23:00',
#         ],
#         'area': [
#             47.09, 10.39, 45.67,
#             12.48,
#         ],
#         'format': 'grib',
#     },
#     '20142015.grib')


# In[ ]:


# c = cdsapi.Client()

# c.retrieve(
#     'reanalysis-era5-land',
#     {
#         'variable': [
#             '2m_dewpoint_temperature', '2m_temperature', 'surface_net_solar_radiation',
#             'total_precipitation',
#         ],
#         'year': [
#             '2016', '2017',
#         ],
#         'month': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#         ],
#         'day': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#             '13', '14', '15',
#             '16', '17', '18',
#             '19', '20', '21',
#             '22', '23', '24',
#             '25', '26', '27',
#             '28', '29', '30',
#             '31',
#         ],
#         'time': [
#             '00:00', '01:00', '02:00',
#             '03:00', '04:00', '05:00',
#             '06:00', '07:00', '08:00',
#             '09:00', '10:00', '11:00',
#             '12:00', '13:00', '14:00',
#             '15:00', '16:00', '17:00',
#             '18:00', '19:00', '20:00',
#             '21:00', '22:00', '23:00',
#         ],
#         'area': [
#             47.09, 10.39, 45.67,
#             12.48,
#         ],
#         'format': 'grib',
#     },
#     '20162017.grib')


# In[ ]:


# c = cdsapi.Client()

# c.retrieve(
#     'reanalysis-era5-land',
#     {
#         'variable': [
#             '2m_dewpoint_temperature', '2m_temperature', 'surface_net_solar_radiation',
#             'total_precipitation',
#         ],
#         'year': [
#             '2018', '2019',
#         ],
#         'month': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#         ],
#         'day': [
#             '01', '02', '03',
#             '04', '05', '06',
#             '07', '08', '09',
#             '10', '11', '12',
#             '13', '14', '15',
#             '16', '17', '18',
#             '19', '20', '21',
#             '22', '23', '24',
#             '25', '26', '27',
#             '28', '29', '30',
#             '31',
#         ],
#         'time': [
#             '00:00', '01:00', '02:00',
#             '03:00', '04:00', '05:00',
#             '06:00', '07:00', '08:00',
#             '09:00', '10:00', '11:00',
#             '12:00', '13:00', '14:00',
#             '15:00', '16:00', '17:00',
#             '18:00', '19:00', '20:00',
#             '21:00', '22:00', '23:00',
#         ],
#         'area': [
#             47.09, 10.39, 45.67,
#             12.48,
#         ],
#         'format': 'grib',
#     },
#     '20182019.grib')


# In[ ]:


# import cdsapi

# for variable in variables:
#     for year in years:
#         for month in months:
#             for day in days:
#                 for hour in hours:

#                     try:
#                         c = cdsapi.Client()

#                         c.retrieve(
#                             'reanalysis-era5-land',
#                             {
#                                 'variable': [
#                                     '{var}'.format(var=variable)
#                                 ],
#                                 'year': [
#                                     '{y}'.format(y=year)
#                                 ],
#                                 'month': [
#                                     '{m}'.format(m=month)
#                                 ],
#                                 'day': [
#                                     '{d}'.format(d=day)
#                                 ],
#                                 'time': [
#                                     '00:00', '01:00', '02:00',
#                                     '03:00', '04:00', '05:00',
#                                     '06:00', '07:00', '08:00',
#                                     '09:00', '10:00', '11:00',
#                                     '12:00', '13:00', '14:00',
#                                     '15:00', '16:00', '17:00',
#                                     '18:00', '19:00', '20:00',
#                                     '21:00', '22:00', '23:00',
#                                 ],
#                                 'area': [
#                                     45.67, 10.39, 47.09, 12.48,
#                                 ],
#                                 'format': 'grib',
#                             },
#                             '{y}_{m}_{d}_{var}.grib'.format(var=variable, y=year, m=month, d=day))
#                     except:
#                         continue


# In[ ]:


# fid = open('/media/windows/projects/meteo_forecast_water_demand/meteo/era5/raw/2013_1_01_2m_dewpoint_temperature.grib',"r")
# gid = codes_any_new_from_file(fid)

# iterid = codes_keys_iterator_new(gid, 'ls')

# while codes_keys_iterator_next(iterid):
#     keyname = codes_keys_iterator_get_name(iterid)
#     keyval = codes_get_string(gid, keyname)
#     print("%s = %s" % (keyname, keyval))

