# -*- coding: utf-8 -*-
"""
Created on Wed May 20 08:40:29 2020
Modified on Mon Feb 22 2021

@author: Ndimarco, ftt01 (dallatorre.daniele@gmail.com)
"""

import numpy as np
import pandas as pd
import datetime as dt

path_krig_in  = 'D:\\hydrology\\scripts\\VS_kriging\\AltoAdige\\output\\1km_AA\\'
path_krig_out = 'D:\\hydrology\\hydro_modelling\\' + basin + '\\meteo\\kriging\\'

#### INPUTS ####

# KRIGING MODEL OUTPUTS TO USE
files_krig    = ['TMEAN', 'P']
kriging_precipitation_file = path_krig_in + 'P_AltoAdige.krig'
kriging_temperature_file = path_krig_in + 'TMEAN_AltoAdige.krig'
basin_cells_ID = path_krig_out + 'IDsubbs_IDgrid.csv'

# BASIN TO USE
#basin         = 'Monguelfo'
#basin         = 'Senales'
basin         = 'Passirio'

# CELLS METEO METADATA TO USE
grid_metadata = 'D:\\hydrology\\data\\GFS_models\\ECMWF\\ERA5Land-reanalysis\\grid_1x1km_Adige_river.csv'

#### OUTPUTS ####
precipitation_file_out = path_krig_out + 'observations\\'+'precipitation.txt'
temperature_file_out = path_krig_out + 'observations\\'+'temperature.txt'

# Threshold temperature for rain/snow classification
Tsnow = 0.5

# Kriging time window
t0 = dt.datetime(2012,10,1,0,0) 
t1 = dt.datetime(2018,9,30,23,0) 
dates = pd.date_range(t0, t1, freq='h')

# Reading kriging grid cell ID included in each subbasin (df index = ID subb.)
f = open( basin_cells_ID, 'r' )
IDsubbs = list()
IDgrid  = list()
for line in f.readlines():
    IDsubbs.append( int(line.split(',')[0]) )
    N = len(line.split(','))
    data = line.split(',')[1:N] 
    data[N-2] = data[N-2].replace('\n','')
    IDgrid.append( data )
f.close()
ID_all_basin = sum(IDgrid, [])

print('N cells: ',     len(ID_all_basin))
print('N time step: ', len(dates))

# Reading kriging grid metadata
df_grid = pd.read_csv( grid_metadata, index_col = 0 )
df_elev = df_grid['Elevation']
IDgrid_int = [int(k) for k in ID_all_basin]
elev       = df_elev[IDgrid_int]

df_T = pd.DataFrame(index=dates,columns=['Tinter','Tslope'])
df_P = pd.DataFrame(index=dates,columns=IDsubbs)

###
df_p = pd.read_csv(kriging_precipitation_file)
df_p['dates'] = dates
df_p.set_index('dates',inplace=True)
    
df_t = pd.read_csv(kriging_temperature_file)
df_t['dates'] = dates
df_t.set_index('dates',inplace=True)

krig_t = df_t[ID_all_basin]
krig_p = df_p[ID_all_basin]

for t in dates:
    currT = krig_t.loc[t].values
    df_LP = pd.DataFrame([elev.values,currT]).T 
    Tslope = df_LP.cov()[1][0] / elev.var()
    Tintercept = currT.mean() - Tslope*elev.mean()
    df_T.loc[t]['Tinter'] = round(Tintercept,3)
    df_T.loc[t]['Tslope'] = round(Tslope,6)


krig_p[krig_t<=Tsnow] = krig_p[krig_t<=Tsnow] *1

for i, ids in enumerate(IDsubbs):
    print(i, ' - IDsubb. = ', ids)
    krig = krig_p[IDgrid[i]]     
    df_P[ids] = round(krig.mean(axis=1),3)


# for file in files_krig:
#     print('Processing: ' + file + '_AltoAdige.krig')
    
#     df = pd.read_csv(path_krig_in+file+'_AltoAdige.krig')
#     df['dates'] = dates
#     df.set_index('dates',inplace=True)

#     if file=='TMEAN': 
#         krig = df[ID_all_basin]
        
        
#         # Set SCF matrix depending on T
#         SCF = krig
#         SCF[SCF<=Tsnow] = SCF[SCF<=Tsnow] * 1.4
#         # SCF[SCF>Tsnow]  = 1
        
        
#         for t in dates:
#             currT = krig.loc[t].values
#             df_LP = pd.DataFrame([elev.values,currT]).T 
#             Tslope = df_LP.cov()[1][0] / elev.var()
#             Tintercept = currT.mean() - Tslope*elev.mean()
#             df_T.loc[t]['Tinter'] = round(Tintercept,3)
#             df_T.loc[t]['Tslope'] = round(Tslope,3)
#     else:
                
#         for i, ids in enumerate(IDsubbs):
#             print(i, ' - IDsubb. = ', ids)
#             krig = SCF[IDgrid[i]]  # df[IDgrid[i]] * SCF[IDgrid[i]]           
#             df_P[ids] = round(krig.mean(axis=1),3)
######################################################
# Printing    
df_T.to_csv(temperature_file_out, header=False)

df_P.index.name='date'
df_P.to_csv(precipitation_file_out, header=True)
