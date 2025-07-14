from lib import *

import glob

### setting###

#pathout= r'C:/Users/alber/Desktop/tesi/Risultati/Grafici_confronto_krig_rea_obs/Mar18-Giu18/Semivariogramma_2(AA12-18)/'
pathout = config["output_path"]

# Kriging resampling output data 
# path_kr = r'D:/hydrology/projects/era5_bias/1_hydrometereological_data_comparison/scripts/kriging/AltoAdige/'
meteo_var = ['TMEAN' ,'P'] 

# Reanalysis extracted on Adige (closed to Bronzolo) catchment output data 
# path_rea =r'D:/hydrology/data/GFS_models/ECMWF/ERA5Land-reanalysis/'
meteo_var_r = ['t2m' ,'ptot']

#Meteo station of subbasin
path_sub=r'D:/hydrology/projects/era5_bias/calibration_validation/hydro_modelling/'

t0 = dt.datetime(2010,1,1,1,0) 
t1 = dt.datetime(2019,12,31,23,0) 
 
for var in meteo_var:
    for var_r in meteo_var_r:
        if var=='TMEAN' and var_r=='t2m':
            #-------------------Grafici BOXPLOT BASIN------------------------------------------------------
            #basins=['Passirio','Senales','Plan']
            basins=['Plan']
            #-------------------boxplot 10 years--------------------
            for basin in basins:  
                
                df_t=pd.DataFrame()
                box_t=pd.DataFrame()
                t_stations = path_sub + basin + '/meteo/kriging/observations/temperature/'
                t_file_tot = glob.glob(t_stations+'*.csv')
                for t_file in t_file_tot:
                    data_tot = pd.read_csv(t_file,index_col=0,parse_dates=True,skiprows=4,names=['values'])
                    data_tot=data_tot[t0:t1]
                    df_t=pd.concat([df_t,data_tot],axis=1)
                box_t_k=df_t.mean(axis=1)   
                    
                df_t=pd.DataFrame()
                box_t=pd.DataFrame()
                t_stations=path_sub +  basin+'/meteo/reanalysis/observations/temperature/'
                t_file_tot = glob.glob(t_stations+'*.csv')
                for t_file in t_file_tot:
                    data_tot = pd.read_csv(t_file,index_col=0,parse_dates=True,skiprows=4,names=['values'])
                    data_tot=data_tot[t0:t1]
                    df_t=pd.concat([df_t,data_tot],axis=1)
                box_t_r=df_t.mean(axis=1) 
                    
                box_t= box_t_k - box_t_r

                output_file = pathout + "meteo\\" + basin + "\\temperature\\monthly\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_monthly_bias_kr11-rea.' + output_format
                createBoxPlot( box_t, "Time $[month]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, scale_factor=0.5, my_dpi=50 )

                output_file_hd = pathout + "meteo\\" + basin + "\\temperature\\monthly\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_monthly_bias_kr11-rea_hd.' + output_format
                createBoxPlot( box_t, "Time $[month]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, scale_factor=0.5, my_dpi=600 )

                output_file = pathout + "meteo\\" + basin + "\\temperature\\hourly\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea.' + output_format
                createBoxPlot( box_t, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

                output_file_hd = pathout + "meteo\\" + basin + "\\temperature\\hourly\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_hd.' + output_format
                createBoxPlot( box_t, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )
                    
                #-------------------boxplot seasonal--------------------     
                box_t_jan=box_t.loc[(box_t.index.month==1)]
                box_t_feb=box_t.loc[(box_t.index.month==2)]
                box_t_mar=box_t.loc[(box_t.index.month==3)]
                box_t_apr=box_t.loc[(box_t.index.month==4)]
                box_t_may=box_t.loc[(box_t.index.month==5)]
                box_t_jun=box_t.loc[(box_t.index.month==6)]
                box_t_jul=box_t.loc[(box_t.index.month==7)]
                box_t_aug=box_t.loc[(box_t.index.month==8)]
                box_t_sep=box_t.loc[(box_t.index.month==9)]
                box_t_oct=box_t.loc[(box_t.index.month==10)]
                box_t_nov=box_t.loc[(box_t.index.month==11)]
                box_t_dec=box_t.loc[(box_t.index.month==12)]

                box_t_w=pd.concat([box_t_jan,box_t_feb,box_t_mar])
                box_t_sp=pd.concat([box_t_apr,box_t_may,box_t_jun])
                box_t_su=pd.concat([box_t_jul,box_t_aug,box_t_sep])
                box_t_a=pd.concat([box_t_oct,box_t_nov,box_t_dec])

                output_file = pathout + "meteo\\" + basin + "\\temperature\\hourly\\seasonal\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_winter.' + output_format
                createBoxPlot( box_t_w, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )
                
                output_file_hd = pathout + "meteo\\" + basin + "\\temperature\\hourly\\seasonal\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_winter_hd.' + output_format
                createBoxPlot( box_t_w, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

                output_file = pathout + "meteo\\" + basin + "\\temperature\\hourly\\seasonal\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_spring.' + output_format
                createBoxPlot( box_t_sp, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

                output_file_hd = pathout + "meteo\\" + basin + "\\temperature\\hourly\\seasonal\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_spring_hd.' + output_format
                createBoxPlot( box_t_sp, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

                output_file = pathout + "meteo\\" + basin + "\\temperature\\hourly\\seasonal\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_summer.' + output_format
                createBoxPlot( box_t_su, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )

                output_file_hd = pathout + "meteo\\" + basin + "\\temperature\\hourly\\seasonal\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_summer_hd.' + output_format
                createBoxPlot( box_t_su, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )

                output_file = pathout + "meteo\\" + basin + "\\temperature\\hourly\\seasonal\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_autumn.' + output_format
                createBoxPlot( box_t_a, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, period="H", scale_factor=0.5, my_dpi=50 )
                
                output_file_hd = pathout + "meteo\\" + basin + "\\temperature\\hourly\\seasonal\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_bias_kr11-rea_autumn_hd.' + output_format
                createBoxPlot( box_t_a, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, period="H", scale_factor=0.5, my_dpi=600 )