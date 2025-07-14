from lib import *
current = DataCollector()

## -----------------Grafici diff con la quota---------------- ##

diff_p_elev = pd.read_csv('D:\\projects\\era5_bias\\01_preprocessing\\meteo\\diff_media_temporale_ptot.csv',index_col=0)
diff_t_elev = pd.read_csv('D:\\projects\\era5_bias\\01_preprocessing\\meteo\\diff_media_temporale_t2m.csv',index_col=0)           
elev = pd.read_csv('D:\\projects\\era5_bias\\01_preprocessing\\meteo\\diff_media_temporale_ptot.csv',index_col=0)

diff_p_elev.reset_index(drop=True, inplace=True)
diff_t_elev.reset_index(drop=True, inplace=True)
elev.reset_index(drop=True, inplace=True)

diff_p=diff_p_elev[diff_p_elev.columns[3]]
diff_t=diff_t_elev[diff_t_elev.columns[3]]
elevation=diff_p_elev[diff_p_elev.columns[2]]

fig, axs = instantiatePlot( "Precipitation $[mm/year]$", "Elevation $[m]$", output_format='png', scale_factor=0.5 )

axs.scatter( diff_p, elevation, s=10, label='Precipitation bias')  
z1 = np.polyfit(diff_p,elevation, 1)
z2 = np.polyfit(diff_t,elevation, 1)
p1 = np.poly1d(z1)
p2 = np.poly1d(z2)

#cc_p  =  np.corrcoef(diff_p,elevation)
#cc_t  =  np.corrcoef(diff_t,elevation)
# dai grafici non c'è correlazione specifica!!!! cc bassi

axs.plot( diff_p, p1(diff_p), "r--" ) 

output_file = current.config["output_path"] + "meteo\\altoAdige\\precipitation\\over_elevation\\" \
    + 'meteo_AA_bias_precipitation_over_elevation.' + output_format
    
mkNestedDir(getPathFromFilepath(output_file))
fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50 )

output_file_hd = current.config["output_path"] + "meteo\\altoAdige\\precipitation\\over_elevation\\" \
    + 'meteo_AA_bias_precipitation_over_elevation_hd.' + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig( output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600 )                    

################################################################
fig, axs = instantiatePlot( "Temp. bias $[\degree C]$", "Elevation $[m]$", output_format='png', scale_factor=0.5 )

axs.scatter(diff_t,elevation, s=10, label='Temp. bias')
z1 = np.polyfit(diff_p,elevation, 1)
z2 = np.polyfit(diff_t,elevation, 1)
p1 = np.poly1d(z1)
p2 = np.poly1d(z2)

#cc_p  =  np.corrcoef(diff_p,elevation)
#cc_t  =  np.corrcoef(diff_t,elevation)
# dai grafici non c'è correlazione specifica!!!! cc bassi

axs.plot( diff_t, p2(diff_t), "r--")

output_file = current.config["output_path"] +  "meteo\\altoAdige\\temperature\\over_elevation\\" \
    + 'meteo_AA_bias_temperature_over_elevation.' + output_format

mkNestedDir(getPathFromFilepath(output_file))
fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50 )

output_file_hd = current.config["output_path"] +  "meteo\\altoAdige\\temperature\\over_elevation\\" \
    + 'meteo_AA_bias_temperature_over_elevation_hd.' + output_format

mkNestedDir(getPathFromFilepath(output_file_hd))
fig.savefig( output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600 )