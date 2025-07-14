from lib import *

basin = 'AltoAdige'
output_path = config["output_path"] + "meteo\\" + basin + "\\precipitation\\over_elevation\\"
output_log = output_path + 'AA_precipitation_lapse_rate_reanalysis11x8.log'
mkNestedDir(output_path)

import logging
logging.basicConfig(filename=output_log, format='%(asctime)s - %(message)s', level=logging.INFO)

logging.info( "basin: " + basin )

### INPUTS 

# path_in  = 'D:\\hydrology\\works\\calibration_validation\\hydro_modelling\\Passirio\\meteo\\reanalysis\\observations\\precipitation\\'
path_in  = 'D:\\hydrology\\data\\GFS_models\\ECMWF\\ERA5Land-reanalysis\\ptot\\hourly_ts\\'
ids_in = pd.read_csv('D:\\hydrology\\results\\meteo\\kriging\\id_AA_cells.csv', delimiter=',')

# time window
t0 = dt.datetime(2010,1,1,0,0) 
t1 = dt.datetime(2019,12,31,23,0)
dates = pd.date_range(t0, t1, freq='h')

import glob
cells_data = glob.glob( path_in + '*.csv')

i = 0
precipitation = pd.DataFrame() # dataframe kriging with all data in the directory
df_elev = pd.DataFrame(columns=['id', 'elevation'])
for file in cells_data:
    col = file.removeprefix(path_in).strip('.csv')
    if int(col) in list(ids_in['id']):
        data_tot = pd.read_csv( file, index_col=0, parse_dates=True, skiprows=4, names=[col] )
        data_tot_metadata = pd.read_csv( file, index_col=0, parse_dates=True, names=[col] ) 
        data_tot = data_tot[t0:t1]
        data_tot_metadata = data_tot_metadata[0:4]
        df_elev = df_elev.append({'id': col, 'elevation': data_tot_metadata[col][3]}, ignore_index=True)
        #data_tot[data_tot == -999] = None
        #data_tot = data_tot.resample('d').mean()
        precipitation = pd.concat([precipitation,data_tot],axis=1)
        # metadata_k=pd.concat([metadata_k,data_tot_metadata],axis=1)
        i = i + 1

logging.info( basin + " # cells: " + str(i) )

df_elev.set_index('id', inplace=True)
elev = df_elev['elevation']

precipitation_yearly_mean = precipitation.resample('Y').sum()

precipitation_yearly_mean_mean = precipitation_yearly_mean.mean()

precipitation_df = pd.DataFrame(columns=['id', 'elevation', 'precipitation'])
for id in precipitation_yearly_mean_mean.index:
    if elev[id] != -999:
            # if prec > 400:
        precipitation_df = precipitation_df.append({'id':str(id), 'elevation':elev[str(id)], \
            'precipitation': precipitation_yearly_mean_mean[str(id)]}, ignore_index=True)
precipitation_df = precipitation_df.set_index('id')

# precipitation_df = pd.DataFrame(columns=['id', 'elevation', 'precipitation'])
# for id in elev.index:
#     for prec in precipitation_yearly_mean[str(id)].values:
#         if elev[id] != -999:
#                 # if prec > 400:
#             precipitation_df = precipitation_df.append({'id':str(id), 'elevation':elev[str(id)], \
#                 'precipitation': prec}, ignore_index=True)
# precipitation_df = precipitation_df.set_index('id')

diff_p = precipitation_df['precipitation']
elevation = precipitation_df['elevation']

fig, axs = instantiatePlot( "Elevation $[m]$", "Precipitation $[mm/year]$")

axs.scatter( elevation, diff_p, s=10 ) 

z1 = np.polyfit(elevation, diff_p, 1)
p1 = np.poly1d(z1)

cc_p  =  np.corrcoef(elevation, diff_p)
logging.info( "Reanalysis 11x8 correlation: " + str(cc_p[0][1]) )
axs.plot( elevation, p1(elevation), "r--" )

output_file_hd = output_path + 'meteo_' + basin + '_precipitation_rea11_over_elevation_hd.' + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig( output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600 ) 

## evaluation of parameter G
z_mean=precipitation_df['elevation'].mean()
logging.info( "mean elevation: " + str(z_mean) )
p_mean=precipitation_df['precipitation'].mean()
logging.info( "mean precipitation: " + str(p_mean) )

# gg = []
# for ind in precipitation_df.index:
#     z_i=precipitation_df['elevation'][ind]
#     p_i=precipitation_df['precipitation'][ind]
#     gg.append(evaluateParameterG(z_i=z_i, z_mean=z_mean, p_i=p_i, p_mean=p_mean))

# gg_arr = np.array(gg)
# logging.info( basin + " evaluated G with all points: " + str(gg_arr.mean()) )

param_g = evaluateParameterGfromSlope( p_mean, p1[1] )

logging.info( basin + " linear regression slope: " + str(p1[1]) )
logging.info( basin + " evaluated G: " + str(param_g) )