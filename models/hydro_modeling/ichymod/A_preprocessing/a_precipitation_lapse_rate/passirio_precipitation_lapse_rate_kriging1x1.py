from lib import *

basin = 'Passirio'
output_path = config["output_path"] + "meteo\\" + basin + "\\precipitation\\over_elevation\\"
output_log = output_path + basin + '_precipitation_lapse_rate_kriging1x1.log'
mkNestedDir(output_path)

import logging
logging.basicConfig(filename=output_log, format='%(asctime)s - %(message)s', level=logging.INFO)

logging.info( "basin: " + basin )

### INPUTS 

#path_krig_in  = 'D:\\hydrology\\scripts\\VS_kriging\\AltoAdige\\output\\1km_AA\\'
path_krig_in  = 'D:\\hydrology\\works\\1_hydrometereological_data_comparison\\scripts\\kriging\\AltoAdige\\'
path_krig_out = 'D:\\hydrology\\hydro_modelling\\' + basin + '\\meteo\\kriging\\'

#### INPUTS ####

# KRIGING MODEL OUTPUTS TO USE
# files_krig    = ['TMEAN', 'P']
kriging_precipitation_file = path_krig_in + 'P_AltoAdige.krig'
# kriging_temperature_file = path_krig_in + 'TMEAN_AltoAdige.krig'
basin_cells_ID = path_krig_out + 'IDsubbs_IDgrid.csv'                                                       #### who created this??? - just Passirio!!!

# CELLS METEO METADATA TO USE
# define the id, centroid coordinates and elevation of each cell
grid_metadata = 'D:\\hydrology\\data\\GFS_models\\ECMWF\\ERA5Land-reanalysis\\grid_1x1km_Adige_river.csv'   #### who created this??? - entire Adige river

#### OUTPUTS ####
# precipitation_file_out = path_krig_out + 'observations\\' + 'precipitation.txt'
#temperature_file_out = path_krig_out + 'observations\\'+'temperature.txt'

# Threshold temperature for rain/snow classification
# Tsnow = 0.5

# Kriging time window
t0 = dt.datetime(2010,1,1,0,0) 
t1 = dt.datetime(2019,12,31,23,0)
dates = pd.date_range(t0, t1, freq='h')

#################################################################################
#################################################################################

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

logging.info( basin + " # cells: " + str(len(ID_all_basin)) )

# Reading kriging grid metadata - all Adige river cells
df_grid = pd.read_csv( grid_metadata, index_col=0 )
df_elev = df_grid['Elevation']
IDgrid_int = [int(k) for k in ID_all_basin]
df_elev = df_elev[IDgrid_int]

df_P = pd.DataFrame(index=dates,columns=IDsubbs)

### data entire Alto Adige
df_p = pd.read_csv( kriging_precipitation_file, parse_dates=True, index_col=0 )
df_p['dates'] = dates
df_p.set_index( 'dates',inplace=True )

# collects only specific basin IDs
df_p = df_p[ID_all_basin]

precipitation_yearly_mean = df_p.resample('Y').sum()

precipitation_yearly_mean_mean = precipitation_yearly_mean.mean()

precipitation_df = pd.DataFrame(columns=['id', 'elevation', 'precipitation'])
for id in precipitation_yearly_mean_mean.index:
    if df_elev[int(id)] != -999:
            # if prec > 400:
        precipitation_df = precipitation_df.append({'id':str(id), 'elevation':df_elev[int(id)], \
            'precipitation': precipitation_yearly_mean_mean[str(id)]}, ignore_index=True)
precipitation_df = precipitation_df.set_index('id')

# for id in df_elev.index:
#     if str(id) in krig_p_yearly_mean.columns:
#         for prec in krig_p_yearly_mean[str(id)].values:
#             if df_elev[id] != -999:
#                 # if prec > 400:
#                 precipitation_df = precipitation_df.append({'id':str(id), 'elevation': df_elev[id], \
#                     'precipitation': prec}, ignore_index=True)
# precipitation_df = precipitation_df.set_index('id')

diff_p = precipitation_df['precipitation']
elevation = precipitation_df['elevation']

fig, axs = instantiatePlot( "Elevation $[m]$", "Precipitation $[mm/year]$")

axs.scatter( elevation, diff_p, s=10 ) 

z1 = np.polyfit(elevation, diff_p, 1)
p1 = np.poly1d(z1)

cc_p  =  np.corrcoef(elevation, diff_p)
logging.info( "Kriging 1x1 correlation: " + str(cc_p[0][1]) )
axs.plot( elevation, p1(elevation), "r--" )

cc_p  =  np.corrcoef(elevation, diff_p)

output_file_hd = output_path + 'meteo_' + basin + '_precipitation_kr_over_elevation_hd.' + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig( output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600 ) 

## linear regression
# for t in dates:
#     currT = krig_t.loc[t].values
#     df_LP = pd.DataFrame([elev.values,currT]).T 
#     Tslope = df_LP.cov()[1][0] / elev.var()
#     Tintercept = currT.mean() - Tslope*elev.mean()
#     df_T.loc[t]['Tinter'] = round(Tintercept,3)
#     df_T.loc[t]['Tslope'] = round(Tslope,6)

# df_P.index.name='date'
# df_P.to_csv(precipitation_file_out, header=True)

## evaluation of parameter G
z_mean=precipitation_df['elevation'].mean()
logging.info( basin + " mean elevation: " + str(z_mean) )
p_mean=precipitation_df['precipitation'].mean()
logging.info( basin + " mean precipitation: " + str(p_mean) )

# gg = []
# for ind in precipitation_df.index:
#     z_i=precipitation_df['elevation'][ind]
#     p_i=precipitation_df['precipitation'][ind]
#     gg.append(evaluateParameterG(z_i=z_i, z_mean=z_mean, p_i=p_i, p_mean=p_mean))

# gg_arr = np.array(gg)

param_g = evaluateParameterGfromSlope( p_mean, p1[1] )

logging.info( basin + " linear regression slope: " + str(p1[1]) )
logging.info( basin + " evaluated G: " + str(param_g) )