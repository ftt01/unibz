from lib import *
current = DataCollector()

### setting ###

#pathout= r'C:/Users/alber/Desktop/tesi/Risultati/Grafici_confronto_krig_rea_obs/Mar18-Giu18/Semivariogramma_2(AA12-18)/'
pathout = config["output_path"]

# Kriging resampling output data 
path_kr = r'D:/hydrology/projects/era5_bias/1_hydrometereological_data_comparison/scripts/kriging/AltoAdige/'
meteo_var = ['TMEAN' ,'P'] 

# Reanalysis extracted on Adige (closed to Bronzolo) catchment output data 
path_rea =r'D:/hydrology/data/GFS_models/ECMWF/ERA5Land-reanalysis/'
meteo_var_r = ['t2m' ,'ptot']

#Meteo station of subbasin
path_sub=r'D:/hydrology/projects/era5_bias/calibration_validation/hydro_modelling/'

IDs_cells  = [207,115,203,154,208,174]   # ID kriging resampling grid points and ID Reanalysis extracted on Adige catchment grid points
                   
# Meteo Station Datas
path_ms = r'D:/hydrology/data/AA_weather_data/'
ID_station=[13,16,21,101,191,193]
ID_label= ['Alpe_di_Siusi_Zallinger(1920slm)', \
            'Anterselva_di_Sopra(1320slm)', \
            'Bolzano(254slm)', \
            'Merano(333slm)', \
            'Selva_di_Val_Gardena(1570slm)', \
            'Silandro(718slm)']

t0 = dt.datetime(2010,1,1,1,0) 
t1 = dt.datetime(2019,12,31,23,0) 

dates = pd.date_range(t0, t1, freq='h')
dates_days = pd.date_range(t0, t1, freq='d')

ta = dt.datetime(2010,1,1,1,0) 
tb = dt.datetime(2019,12,31,23,0) 

#####

#prepare figure plot and DataFrames
my_dpi=100
# fig1 = plt.figure(figsize=(1500/my_dpi, 1000/my_dpi), dpi=my_dpi)
# fig2 = plt.figure(figsize=(1500/my_dpi, 1000/my_dpi), dpi=my_dpi)
bigframe1 = pd.DataFrame(index=IDs_cells,columns=['rmse','cc','mae'])
bigframe2 = pd.DataFrame(index=IDs_cells,columns=['rmse','cc','mae'])
bigframe3 = pd.DataFrame(index=IDs_cells,columns=['rmse','cc','mae'])
bigframe4 = pd.DataFrame(index=IDs_cells,columns=['rmse','cc','mae'])

for var in meteo_var:
    for var_r in meteo_var_r:
        
        if var=='TMEAN' and var_r=='t2m':
            
            for i,ID_cell in enumerate(IDs_cells):
                
                file=path_kr + var + '/' +str(ID_cell) + '.csv'
                file_r=path_rea  + var_r + '/' + str(ID_cell) + '.csv'
                meteo_var_ms='temperature'
                station = ID_station[i] 
                station_label = ID_label[i] 
                file_ms=path_ms + meteo_var_ms + '/' + str(station) + '.txt'
                
                data = pd.read_csv(file,index_col=0,parse_dates=True, skiprows=4, names=['values'])
                data_r = pd.read_csv(file_r,index_col=0,parse_dates=True, skiprows=4, names=['values'])
                data_ms = pd.read_csv(file_ms,index_col=0,parse_dates=True, skiprows=4, names=['values'])
                
                data=data[t0:t1]
                data_r=data_r[t0:t1]
                data_ms=data_ms[t0:t1]
                data[data == -999] = None
                data_r[data_r == -999] = None
                data_ms[data_ms == -999] = None
                
                data = data.resample('d').mean()
                data_r = data_r.resample('d').mean()
                data_ms = data_ms.resample('d').mean()                
                
                ##COEFF STATISTICI kriging vs reanalysis
                Ndata = len(data) 
                rmse = np.sqrt((1/Ndata) * np.sum((data.values - data_r.values)**2 ))       
                cc  =  np.corrcoef(data['values'],data_r['values'])
                mae=(np.sum(np.abs(data['values'] - data_r['values']) ))/Ndata
                bigframe1.loc[ID_cell]['rmse'] = rmse
                bigframe1.loc[ID_cell]['cc'] = cc[0][1]
                bigframe1.loc[ID_cell]['mae'] = mae
                            
                data = data.resample('MS').mean()
                data_r = data_r.resample('MS').mean()
                data_ms = data_ms.resample('MS').mean()
                 
                # #plot delle 6 stazioni
                # ax = fig1.add_subplot(6, 2, i+1)
                # ax.plot(data,label='kriging')
                # ax.plot(data_r,label='reanalysis')
                # #ax.plot(data_ms,label='obs')
                # ax.set_ylabel(' temperature $[\degree C]$')
                # #ax.set_ylabel(var+unit)
                # ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
                # ax.set_title( ' temperature - ' + str(ID_cell) + '_cell [' + str(station_label) + ']')
                # ax.legend()


            # fig1.savefig(pathout +'comparison_'+var_r+'_krig_vs_rea.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=600)     
            # bigframe1.to_csv(pathout+'statistics_krigin_vs_rean_'+var_r+'.txt',index_label='ID_grid')
            # bigframe3.to_csv(pathout+'statistics_datas_vs_rean_'+var_r+'.txt',index_label='ID_grid')

            #-------------------------------Grafici ECDF TEMPERATURA--------------------------------------------
            # DataFrame per l'ECDF
            df_k=pd.DataFrame() # dataframe kriging with all data in the directory
            metadata_k=pd.DataFrame() # metadata of the df_k files

            spatial_mean_k=pd.DataFrame(columns= ['dates','values']) # spatial mean kriging
            s_sort_k=pd.DataFrame(columns=['values']) # spatial mean kriging sorted
            s_frame_k=pd.DataFrame() # spatial orde#fdb863 mean kriging
            e_s_k=pd.DataFrame()
            a_s_k=pd.DataFrame(columns=['values'])
            
            t_frame_k=pd.DataFrame() # temporal mean kriging ECDF

            season_k=pd.DataFrame() ### ?

            temporal_mean_k=pd.DataFrame() # temporal mean kriging
            t_sort_k=pd.DataFrame() # temporal sorted mean kriging
            e_t_k=pd.DataFrame()
            a_t_k=pd.DataFrame(columns=['values'])

            #raster_k=pd.DataFrame()  # media temporale kriging

            ### 

            df=pd.DataFrame() # dataframe reanalysis with all data in the directory
            metadata=pd.DataFrame() # metadata of the df files

            spatial_mean=pd.DataFrame(columns= ['dates','values'])  # spatial mean reanalysis
            s_sort=pd.DataFrame(columns=['values']) # spatial mean reanalysis sorted
            s_frame=pd.DataFrame(columns=['values','ecdf']) # spatial orde#fdb863 mean reanalysis
            e_s=pd.DataFrame(columns=['ecdf'])
            a_s=pd.DataFrame(columns=['ecdf'])
            
            t_frame=pd.DataFrame() # temporal mean reanalysis ECDF

            season=pd.DataFrame() ### ?

            temporal_mean=pd.DataFrame() # temporal mean reanalysis
            t_sort=pd.DataFrame() # temporal sorted mean reanalysis
            e_t=pd.DataFrame()
            a_t=pd.DataFrame(columns=['values'])

            #raster=pd.DataFrame() # media temporale reanalysis

            diff_t=pd.DataFrame()
            #

            import glob
            ### assemblo la matrice per fare le medie spaziali e temporali - kriging
            f = path_kr +  'TMEAN/'
            file_tot = glob.glob(f+'*.csv')
            for file in file_tot:
                data_tot = pd.read_csv( file, index_col=0, parse_dates=True, skiprows=4, names=['values'] )
                data_tot_metadata = pd.read_csv( file, index_col=0, parse_dates=True, names=['values'] ) 
                data_tot = data_tot[t0:t1]
                data_tot_metadata = data_tot_metadata[0:3]
                #data_tot[data_tot == -999] = None
                #data_tot = data_tot.resample('d').mean()
                df_k=pd.concat([df_k,data_tot],axis=1)
                metadata_k=pd.concat([metadata_k,data_tot_metadata],axis=1)           
            
            ### assemblo la matrice per fare le medie spaziali e temporali - Reanalysis
            f=path_rea  + 't2m/'
            file_tot = glob.glob(f+'*.csv')
            for file in file_tot:
                data_tot = pd.read_csv(file,index_col=0,parse_dates=True,skiprows=4,names=['values'])
                data_tot_metadata = pd.read_csv(file,index_col=0,parse_dates=True,names=['values'])
                data_tot=data_tot[t0:t1]
                data_tot_metadata=data_tot_metadata[0:4]
                data_tot[data_tot == -999] = None
                #data_tot = data_tot.resample('d').mean()
                df=pd.concat([df,data_tot],axis=1)
                metadata=pd.concat([metadata,data_tot_metadata],axis=1)

            ### MEDIA SPAZIALE - Reanalysis           
            spatial_mean = df.mean(axis=1)
            # spatial_mean.to_csv(pathout+'media_spaziale_reanalysis_t2m_.csv',index=True) 
            s_frame = evaluateECDF( spatial_mean )
            # s_sort=spatial_mean.sort_values()
            # s_sort.reset_index(drop=True, inplace=True)
            # #s_sort=np.log(s_sort)
            # lenght_s=len(s_sort)+1
            # ss=range(1,lenght_s)
            # for s in ss:
            #     s=(s/(lenght_s+1)) *100 
            #     a_s.loc['index']=s
            #     e_s=pd.concat([e_s,a_s],axis=0)           
            # e_s.reset_index(drop=True, inplace=True)       
            # s_frame=pd.concat([e_s,s_sort],axis=1)
            # s_frame.columns=['ecdf','values']
            # s_frame.set_index('values', inplace=True)
                    
            ### MEDIA TEMPORALE - Reanalysis
            season=df.resample('Y').mean()
            season=season.groupby(season.index.month).mean()
            season[season == 0] = None
            
            temporal_mean=df.mean(axis=0)
            t_frame = evaluateECDF( temporal_mean )

            # t_sort=temporal_mean.sort_values()
            # t_sort =  t_sort.iloc[:-1]
            # t_sort.reset_index(drop=True, inplace=True)  
            # lenght_t=len(t_sort)+1
            # print(lenght_t)
            # ts=range(1,lenght_t)
            # for t in ts:
            #     t=(t/(lenght_t+1))*100 
            #     a_t.loc['index']=t
            #     e_t=pd.concat([e_t,a_t],axis=0)                
            # e_t.reset_index(drop=True, inplace=True) 
            # t_frame=pd.concat([e_t,t_sort],axis=1)
            # t_frame.columns=['ecdf','values']
            # t_frame.set_index('values', inplace=True)
           
            ### MEDIA SPAZIALE - kriging          
            spatial_mean_k=df_k.mean(axis=1)
            #spatial_mean_k.to_csv(pathout+'media_spaziale_kriging_t2m_.csv',index=True) 

            s_frame_k = evaluateECDF( spatial_mean_k )

            # s_sort_k=spatial_mean_k.sort_values()
            # s_sort_k.reset_index(drop=True, inplace=True) 
            # #s_sort_k=np.log(s_sort_k)
            # lenght_s_k=len(s_sort_k)+1
            # ss_k=range(1,lenght_s_k)
            # for s in ss_k:
            #     s=(s/(lenght_s_k+1)) *100 
            #     a_s_k.loc['index']=s
            #     e_s_k=pd.concat([e_s_k,a_s_k],axis=0)
            # e_s_k.reset_index(drop=True, inplace=True)       
            # s_frame_k=pd.concat([e_s_k,s_sort_k],axis=1)
            # s_frame_k.columns=['ecdf','values']
            # s_frame_k.set_index('values', inplace=True)

            #MEDIA TEMPORALE - kriging 
            season_k=df_k.resample('Y').mean()                          ### ?
            season_k=season_k.groupby(season_k.index.month).mean()      ### ?
            season_k[season_k == 0] = None
            
            temporal_mean_k=df_k.mean (axis=0)   
            t_frame_k = evaluateECDF( temporal_mean_k )    

            # t_sort_k=temporal_mean_k.sort_values()
            # t_sort_k =  t_sort_k.iloc[:-1]
            # t_sort_k.reset_index(drop=True, inplace=True)   
            # lenght_t_k=len(t_sort_k)+1
            # print(lenght_t_k)
            # ts_k=range(1,lenght_t_k)
            # for t in ts_k:
            #     t=(t/(lenght_t_k+1))*100 
            #     a_t_k.loc['index']=t
            #     e_t_k=pd.concat([e_t_k,a_t_k],axis=0)                 
            # e_t_k.reset_index(drop=True, inplace=True) 
            # t_frame_k=pd.concat([e_t_k,t_sort_k],axis=1)
            # t_frame_k.columns=['ecdf','values']
            # t_frame_k.set_index('values', inplace=True)


            #----------------------------------Grafici MEDIE TEMPORALI------------------------------------------------------
            plots = []

            plt_conf = {}
            plt_conf["label"] = "Reanalysis"
            plots.append( (s_frame, plt_conf) )

            plt_conf = {}
            plt_conf["label"] = "Kriging 11x8"
            plots.append( (s_frame_k, plt_conf) )

            if var == 'P':

                output_file = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_'  + var + '_ECDF_over_time.' + output_format
                createPlot( plots, "Temperature $[mm]$", "ECDF", output_file, \
                    scale_factor=0.5, my_dpi=50)

                output_file_hd = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_'  + var + '_ECDF_over_time_hd.' + output_format
                createPlot( plots, "Temperature $[mm]$", "ECDF", output_file_hd, \
                    scale_factor=0.5, my_dpi=600)

                output_file = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_'  + var + '_ECDF_over_time_log.' + output_format
                createPlot( plots, "Temperature $[mm]$", "ECDF", output_file, \
                    xscale='log', scale_factor=0.5, my_dpi=50)

                output_file_hd = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_'  + var + '_ECDF_over_time_hd_log.' + output_format
                createPlot( plots, "Temperature $[mm]$", "ECDF", output_file_hd, \
                    xscale='log', scale_factor=0.5, my_dpi=600)
            
            elif var == 'TMEAN':

                output_file = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_'  + var + '_ECDF_over_time.' + output_format
                createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file, \
                    scale_factor=0.5, my_dpi=50)

                output_file_hd = pathout + "meteo\\altoAdige\\temperature\\" \
                     + 'meteo_AA_'  + var + '_ECDF_over_time_hd.' + output_format
                createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file_hd, \
                    scale_factor=0.5, my_dpi=600)

                output_file = pathout + "meteo\\altoAdige\\temperature\\" \
                     + 'meteo_AA_'  + var + '_ECDF_over_time_log.' + output_format
                createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file, \
                    xscale='log', scale_factor=0.5, my_dpi=50)

                output_file_hd = pathout + "meteo\\altoAdige\\temperature\\" \
                     + 'meteo_AA_'  + var + '_ECDF_over_time_hd_log.' + output_format
                createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file_hd, \
                    xscale='log', scale_factor=0.5, my_dpi=600)

            # my_dpi=100
            # fig3, axs = plt.subplots(1,figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
            # axs.plot(s_frame,label='reanalysis',linewidth=3)  
            # axs.plot(s_frame_k,label='kriging')
            # axs.set_ylabel(' ECDF',fontsize=40)
            # axs.set_xlabel(' Temp $[\degree C]$',fontsize=40)
            # axs.tick_params( labelsize=40)          
            # axs.legend(fontsize=40) #,bbox_to_anchor=(1.05, 1), loc='upper left'  
            # #axs.set_title('ECDF - Hourly spatial temperature mean ',fontsize=80)               
            # fig3.savefig(pathout +'ECDF_'+var+'_high_resolution.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=600)
            # fig3.savefig(pathout +'ECDF_'+var+'.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=30)
            
            # raster=pd.concat([metadata.T,season.T],axis=1)
            # raster_k=pd.concat([metadata_k.T,season_k.T],axis=1)
            # raster.to_csv(pathout+'media_temporale_reanalysis_t2m_.csv',index=False) 
            # raster_k.to_csv(pathout+'media_temporale_kriging_t2m_.csv',index=False) 
            

            #----------------------------------Grafici MEDIE SPAZIALI------------------------------------------------------
           
            mean_r=pd.DataFrame()
            mean_k=pd.DataFrame()
            
            mean_r=df.mean(axis=1)
            mean_k=df_k.mean(axis=1)
            
            mean_r_avg = mean_r.groupby([mean_r.index.month, mean_r.index.day]).mean()
            mean_r_avg_365 = mean_r_avg.drop(mean_r_avg.index[59]) #cutoff the 29th of February
            mean_r_avg_365.reset_index(drop=True, inplace=True)

            mean_k_avg=mean_k.groupby([mean_k.index.month,mean_k.index.day]).mean()
            mean_k_avg_365=mean_k_avg.drop(mean_k_avg.index[59]) #cutoff the 29th of February
            mean_k_avg_365.reset_index(drop=True, inplace=True)

            year=pd.date_range(start='1/1/13', end='12/31/13')
            mean_r_avg_365.index=year
            mean_k_avg_365.index=year


            mean_r_month=mean_r.resample('MS').mean()
            mean_k_month=mean_k.resample('MS').mean()       
            mean_r_avg_365=mean_r_avg_365.resample('MS').mean()
            mean_k_avg_365=mean_k_avg_365.resample('MS').mean()            
            
            mean = mean_k_month-mean_r_month

            if var == "P":

                output_file = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_' + var + '_boxplot_mounthly_spatial_bias_kr11-rea.' + output_format
                createBoxPlot( mean, "Time $[month]$", "Precipitation bias $[mm]$", \
                    output_file, output_format=output_format, scale_factor=0.5, my_dpi=50 )

                output_file_hd = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_' + var + '_boxplot_mounthly_spatial_bias_kr11-rea_hd.' + output_format
                createBoxPlot( mean, "Time $[month]$", "Precipitation bias $[mm]$", \
                    output_file_hd, output_format=output_format, scale_factor=0.5, my_dpi=600 )
            
            elif var == "TMEAN":

                output_file = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_' + var + '_boxplot_mounthly_spatial_bias_kr11-rea.' + output_format
                createBoxPlot( mean, "Time $[month]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, scale_factor=0.5, my_dpi=50 )

                output_file_hd = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_' + var + '_boxplot_mounthly_spatial_bias_kr11-rea_hd.' + output_format
                createBoxPlot( mean, "Time $[month]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, scale_factor=0.5, my_dpi=600 )

            
            
            # fig4, axs = plt.subplots(1,figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
            # axs=seaborn.boxplot(mean.index.month,mean.values)
            # axs.set_ylabel(ylabel= ' Temperature $[\degree C]$', fontsize =40.0) # Y label
            # axs.set_xlabel(xlabel='month', fontsize = 40) # X label
            # #axs.set_title('Alto Adige Monthly  Temp. bias',fontsize=80)
            # axs.tick_params( labelsize=40)
            # fig4.savefig(pathout +'boxplot_AA_monthly_'+var+'_high_resolution.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=600)
            # fig4.savefig(pathout +'boxplot_AA_monthly_'+var+'.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=30)       
   
           
            #MEDIAN_k=mean_k_avg_365.median()
            #MEDIAN_r=mean_r_avg_365.median()

            # fig5, axs = plt.subplots(1,figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
            # fig5.suptitle('-')
            
            # axs.plot(mean_r_avg_365,label='reanalysis')  
            # axs.plot(mean_k_avg_365,label='kriging') 
            #axs.axhline( MEDIAN_k, label='krig. median', color='r' )
            #axs.axhline( MEDIAN_r, label='rea. median', color='k' )

            # axs.tick_params( labelsize=40)
            # axs.set_ylabel(' Monthly temp. $[\degree C]$',fontsize=40)
            # axs.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
            # axs.legend(fontsize=40,bbox_to_anchor=(1.05, 1), loc='upper left') 
            # #axs.set_title('Alto Adige Monthly  temperature',fontsize=80)     
            # fig5.savefig(pathout +var+'media_spaziale.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=600)
            

            
            #-------------------Grafici BOXPLOT BASIN------------------------------------------------------
            basins=['Passirio','Senales']
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
                 
                box_t = box_t_k - box_t_r

                output_file = pathout + "meteo\\" + basin + "\\temperature\\monthly\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_monthly_temporal_bias_kr11-rea.' + output_format
                createBoxPlot( box_t, "Time $[month]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, my_dpi=50 )
                
                output_file_hd = pathout + "meteo\\" + basin + "\\temperature\\monthly\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_monthly_temporal_bias_kr11-rea_hd.' + output_format
                createBoxPlot( box_t, "Time $[month]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, my_dpi=600 )
            
                output_file = pathout + "meteo\\" + basin + "\\temperature\\monthly\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_temporal_bias_kr11-rea.' + output_format
                createBoxPlot( box_t, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, period="H", my_dpi=50 )

                output_file_hd = pathout + "meteo\\" + basin + "\\temperature\\monthly\\" \
                    + 'meteo_' + basin + '_temperature_boxplot_hourly_temporal_bias_kr11-rea_hd.' + output_format
                createBoxPlot( box_t, "Time $[hour]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, period="H", my_dpi=600 )
                                 
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
        
                # fig11, ax = plt.subplots(figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
                # seaborn.boxplot(box_t_w.index.hour,box_t_w.values, ax=ax)
                # ax.set_ylabel(ylabel=' Winter temp.  bias $[\degree C]$', fontsize = 40.0) # Y label
                # ax.set_xlabel(xlabel='hour', fontsize = 40) # X label
                # #ax.set_title(basin,fontsize=80)
                # ax.tick_params( labelsize=40)
                # ax.set_ylim((-10, 20))
                # plt.xticks(rotation=90)
                # plt.savefig(pathout+'Bias_T_boxplot_hourly_'+basin+'_high_resolution_winter.jpeg',format='jpeg', dpi=600) 
                # plt.savefig(pathout+'Bias_T_boxplot_hourly_'+basin+'_winter.jpeg',format='jpeg', dpi=30)                
                # plt.show() 
    
                # fig12, ax = plt.subplots(figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
                # seaborn.boxplot(box_t_sp.index.hour,box_t_sp.values, ax=ax)
                # ax.set_ylabel(ylabel='Spring Temperature $[\degree C]$', fontsize = 40.0) # Y label
                # ax.set_xlabel(xlabel='hour', fontsize = 40) # X label
                # #ax.set_title(basin,fontsize=80)
                # ax.tick_params( labelsize=40)
                # ax.set_ylim((-10, 20))
                # plt.xticks(rotation=90)
                # plt.savefig(pathout+'Bias_T_boxplot_hourly_'+basin+'_high_resolution_spring.jpeg',format='jpeg', dpi=600)        
                # plt.savefig(pathout+'Bias_T_boxplot_hourly_'+basin+'_spring.jpeg',format='jpeg', dpi=30)
                # plt.show()
                
                # fig13, ax = plt.subplots(figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
                # seaborn.boxplot(box_t_su.index.hour,box_t_su.values, ax=ax)
                # ax.set_ylabel(ylabel='Summer Temperature $[\degree C]$', fontsize =40.0) # Y label
                # ax.set_xlabel(xlabel='hour', fontsize = 40) # X label
                # #ax.set_title(basin,fontsize=80)
                # ax.tick_params( labelsize=40)
                # ax.set_ylim((-10, 20))
                # plt.xticks(rotation=90)
                # plt.savefig(pathout+'Bias_T_boxplot_hourly_'+basin+'_high_resolution_summer.jpeg',format='jpeg', dpi=600)        
                # plt.savefig(pathout+'Bias_T_boxplot_hourly_'+basin+'_summer.jpeg',format='jpeg', dpi=30)
                # plt.show() 
                
                # fig14, ax = plt.subplots(figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
                # seaborn.boxplot(box_t_a.index.hour,box_t_a.values, ax=ax)
                # ax.set_ylabel(ylabel='Autumn Temperature $[\degree C]$', fontsize = 40.0) # Y label
                # ax.set_xlabel(xlabel='hour', fontsize = 40) # X label
                # #ax.set_title(basin,fontsize=80)
                # ax.tick_params( labelsize=40)
                # ax.set_ylim((-10, 20))
                # plt.xticks(rotation=90)
                # plt.savefig(pathout+'Bias_T_boxplot_hourly_'+basin+'_high_resolution_autumn.jpeg',format='jpeg', dpi=600)        
                # plt.savefig(pathout+'Bias_T_boxplot_hourly_'+basin+'_autumn.jpeg',format='jpeg', dpi=30)
                # plt.show()            
            


####################################################################################################################            
####################################################################################################################            
####################################################################################################################                            
####################################################################################################################            
####################################################################################################################            

                
        if var=='P' and var_r=='ptot':
            
            for i,ID_cell in enumerate(IDs_cells):
                
                file=path_kr + var + '/' + str(ID_cell) + '.csv'
                file_r=path_rea  +var_r + '/hourly_ts/'  + str(ID_cell) + '.csv'
                meteo_var_ms='precipitation'
                station = ID_station[i] 
                station_label = ID_label[i] 
                file_ms=path_ms + meteo_var_ms + '/' + str(station) + '.txt'
                
                data = pd.read_csv(file,index_col=0,parse_dates=True, skiprows=4, names=['values'])
                data_r = pd.read_csv(file_r,index_col=0,parse_dates=True, skiprows=4, names=['values'])
                data_ms = pd.read_csv(file_ms,index_col=0,parse_dates=True, skiprows=4, names=['values'])
                
                data=data[ta:tb]
                data_r=data_r[t0:t1]
                data_ms=data_ms[ta:tb] 
                data[data == -999] = None
                data_r[data_r == -999] = None
                data_ms[data_ms == -999] = None                
                 
                data = data.resample('d').sum()  
                data_ms = data_ms.resample('d').sum()
                data_r=data_r.resample('d').sum()
                
                #converting dataframe in format float
                data = data.astype('float')
                data_r = data_r.astype('float')
                                
                # ##COEFF STATISTICI kriging vs reanalysis

                # Ndata = len(data)               
                # rmse = np.sqrt((1/Ndata) *  np.nansum((data - data_r)**2 ))           
                # cc  =  np.corrcoef(data['values'],data_r['values'])
                # mae=(np.nansum(np.abs(data['values'] - data_r['values']) ))/Ndata
                # bigframe2.loc[ID_cell]['rmse'] = rmse
                # bigframe2.loc[ID_cell]['cc'] = cc[0][1]
                # bigframe2.loc[ID_cell]['mae'] = mae
                    
                # data = data.resample('MS').sum()  
                # data_ms = data_ms.resample('MS').sum()
                # data_r=data_r.resample('MS').sum()
                
                # #how to find the maximum values of single station
                # print( data_ms['values'].idxmax() )
                                
                # ax = fig2.add_subplot(6, 2, i+1)
                # ax.plot(data,label='kriging')
                # ax.plot(data_r,label='reanalysis')
                # #ax.plot(data_ms,label='obs')
                # ax.set_ylabel('Prec. [mm/month]')
                # ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%y'))
                # ax.set_title( 'precipitation - ' + str(ID_cell)+ '_cell [' + str(station_label) + ']')
                # ax.legend()
                
                #COEFF STATISTICI datas (station) vs reanalysis
                # Ndata = len(data)
                # rmse = np.sqrt((1/Ndata) *  np.nansum((data - data_ms)**2 ))                  
                # cc  =  np.corrcoef(data['values'],data_ms['values'])
                # mae=(np.nansum(np.abs(data['values'] - data_ms['values']) ))/Ndata
                # bigframe4.loc[ID_cell]['rmse'] = rmse
                # bigframe4.loc[ID_cell]['cc'] = cc[0][1]   
                # bigframe4.loc[ID_cell]['mae'] = mae
            # fig2.savefig(pathout +'comparison_'+var_r+'_krig_vs_rea.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=600)     

            # bigframe2.to_csv(pathout+'statistics_krigin_vs_rean_'+var_r+'.txt',index_label='ID_grid')        
            # bigframe4.to_csv(pathout+'statistics_datas_vs_rean_'+var_r+'.txt',index_label='ID_grid')        
                
            
            #-------------------------------Grafici ECDF PRECIPITAZIONE--------------------------------------------
            
            # DataFrame per l'ECDF
            df=pd.DataFrame()
            season=pd.DataFrame()
            spatial_mean=pd.DataFrame(columns= ['dates','values'])
            temporal_mean=pd.DataFrame()
            t_sort=pd.DataFrame()
            s_sort=pd.DataFrame()
            e_s=pd.DataFrame()
            a_s=pd.DataFrame(columns=['values'])
            e_t=pd.DataFrame()
            a_t=pd.DataFrame(columns=['values'])
            s_frame=pd.DataFrame()
            t_frame=pd.DataFrame()
            metadata=pd.DataFrame()
            raster=pd.DataFrame()
            df_k=pd.DataFrame()
            season_k=pd.DataFrame()
            spatial_mean_k=pd.DataFrame(columns= ['dates','values'])
            temporal_mean_k=pd.DataFrame()
            t_sort_k=pd.DataFrame()
            s_sort_k=pd.DataFrame()
            e_s_k=pd.DataFrame()
            a_s_k=pd.DataFrame(columns=['values'])
            e_t_k=pd.DataFrame()
            a_t_k=pd.DataFrame(columns=['values'])
            s_frame_k=pd.DataFrame()
            t_frame_k=pd.DataFrame()
            metadata_k=pd.DataFrame()
            raster_k=pd.DataFrame()
            diff_p=pd.DataFrame()
            #

            
            ### assemblo la matrice per fare le medie spaziali e temporali - Reanalysis
            f=path_rea  +  'ptot/hourly_ts/'
            file_tot = glob.glob(f+'*.csv')
            for file in file_tot:
                data_tot = pd.read_csv(file,index_col=0,parse_dates=True, skiprows=4,names=['values'])
                data_tot_metadata = pd.read_csv(file,index_col=0,parse_dates=True,names=['values'])
                data_tot=data_tot[t0:t1]
                data_tot_metadata=data_tot_metadata[0:4]
                data_tot[data_tot == -999] = None
                data_tot = data_tot.resample('d').sum()
                df=pd.concat([df,data_tot],axis=1)
                metadata=pd.concat([metadata,data_tot_metadata],axis=1)

            
            ### assemblo la matrice per fare le medie spaziali e temporali - kriging
            f=path_kr +'P/'
            file_tot = glob.glob(f+'*.csv')
            for file in file_tot:
                data_tot = pd.read_csv(file,index_col=0,parse_dates=True,skiprows=4,names=['values'])
                data_tot_metadata = pd.read_csv(file,index_col=0,parse_dates=True,names=['values'])
                data_tot=data_tot[t0:t1]
                data_tot_metadata=data_tot_metadata[0:3]
                data_tot[data_tot == -999] = None
                data_tot = data_tot.resample('d').sum()
                df_k=pd.concat([df_k,data_tot],axis=1)
                metadata_k=pd.concat([metadata_k,data_tot_metadata],axis=1)


            ### MEDIA SPAZIALE - Ranalysis           
            spatial_mean=df.mean(axis=1)
            s_frame = evaluateECDF( spatial_mean )

            # spatial_mean.to_csv(pathout+'media_spaziale_reanalysis_ptot_.csv',index=True) 
            # s_sort=spatial_mean.sort_values()
            # s_sort.reset_index(drop=True, inplace=True)
            # #s_sort=np.log(s_sort)
            # lenght_s=len(s_sort)+1
            # ss=range(1,lenght_s)
            # for s in ss:
            #     s=(s/(lenght_s+1)) *100 
            #     a_s.loc['index']=s
            #     e_s=pd.concat([e_s,a_s],axis=0)      
            # e_s.reset_index(drop=True, inplace=True)       
            # s_frame=pd.concat([e_s,s_sort],axis=1)
            # s_frame.columns=['ecdf','values']
            # s_frame.set_index('values', inplace=True)

            ### MEDIA TEMPORALE - Reanalysis  
            season=df.resample('Y').sum()
            #season=df.resample('Q').sum()
            season=season.groupby(season.index.month).mean()
            season[season == 0] = None

            temporal_mean=df.mean(axis=0)   
            t_frame = evaluateECDF( temporal_mean )

            # t_sort=temporal_mean.sort_values()
            # t_sort = t_sort.iloc[1:]
            # t_sort.reset_index(drop=True, inplace=True)  
            # lenght_t=len(t_sort)+1
            # print(lenght_t)
            # ts=range(1,lenght_t)
            # for t in ts:
            #     t=(t/(lenght_t+1))*100
            #     a_t.loc['index']=t
            #     e_t=pd.concat([e_t,a_t],axis=0)       
            # e_t.reset_index(drop=True, inplace=True) 
            # t_frame=pd.concat([e_t,t_sort],axis=1)
            # t_frame.columns=['ecdf','values']
            # t_frame.set_index('values', inplace=True)
           
            ### MEDIA SPAZIALE - kriging          
            spatial_mean_k=df_k.mean(axis=1)
            s_frame_k = evaluateECDF( spatial_mean_k )
            
            # spatial_mean_k.to_csv(pathout+'media_spaziale_kriging_ptot_.csv',index=True) 
            # s_sort_k=spatial_mean_k.sort_values()
            # s_sort_k.reset_index(drop=True, inplace=True)
            # #s_sort_k=np.log(s_sort_k)
            # #s_sort_k.to_csv(pathout+'xxx1.txt',index=True) 
            # lenght_s_k=len(s_sort_k)+1
            # ss_k=range(1,lenght_s_k)
            # for s in ss_k:
            #     s=(s/(lenght_s_k+1)) *100 
            #     a_s_k.loc['index']=s
            #     e_s_k=pd.concat([e_s_k,a_s_k],axis=0)
           
            # e_s_k.reset_index(drop=True, inplace=True)       
            # s_frame_k=pd.concat([e_s_k,s_sort_k],axis=1)
            # s_frame_k.columns=['ecdf','values']
            # s_frame_k.set_index('values', inplace=True)

            ### MEDIA TEMPORALE - kriging 
            season_k=df_k.resample('Y').sum()
            #season_k=df_k.resample('Q').sum()
            season_k=season_k.groupby(season_k.index.month).mean()
            season_k[season_k == 0] = None
            
            temporal_mean_k=df_k.mean(axis=0)
            t_frame_k = evaluateECDF( temporal_mean_k )

            # t_sort_k=temporal_mean_k.sort_values()
            # t_sort_k =  t_sort_k.iloc[:-1]
            # t_sort_k.reset_index(drop=True, inplace=True)   
            # lenght_t_k=len(t_sort_k)+1
            # print(lenght_t_k)
            # ts_k=range(1,lenght_t_k)
            # for t in ts_k:
            #     t=(t/(lenght_t_k+1))*100 
            #     a_t_k.loc['index']=t
            #     e_t_k=pd.concat([e_t_k,a_t_k],axis=0)     
            # e_t_k.reset_index(drop=True, inplace=True) 
            # t_frame_k=pd.concat([e_t_k,t_sort_k],axis=1)
            # t_frame_k.columns=['ecdf','values']
            # t_frame_k.set_index('values', inplace=True)

            plots = []

            plt_conf = {}
            plt_conf["label"] = "Reanalysis"
            plots.append( (s_frame, plt_conf) )

            plt_conf = {}
            plt_conf["label"] = "Kriging 11x8"
            plots.append( (s_frame_k, plt_conf) )

            if var == "P":
                
                output_file = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_' + var + '_ECDF_over_time_log.' + output_format
                createPlot( plots, "Precipitation $[mm/hour]$", "ECDF", output_file, \
                    xscale='log', scale_factor=0.5, my_dpi=50)

                output_file_hd = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_' + var + '_ECDF_over_time_hd_log.' + output_format
                createPlot( plots, "Precipitation $[mm/hour]$", "ECDF", output_file_hd, \
                    xscale='log', scale_factor=0.5, my_dpi=600)

                output_file = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_' + var + '_ECDF_over_time.' + output_format
                createPlot( plots, "Precipitation $[mm/hour]$", "ECDF", output_file, \
                    scale_factor=0.5, my_dpi=50)

                output_file_hd = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_' + var + '_ECDF_over_time_hd.' + output_format
                createPlot( plots, "Precipitation $[mm/hour]$", "ECDF", output_file_hd, \
                    scale_factor=0.5, my_dpi=600)
            
            elif var == "TMEAN":
                
                output_file = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_' + var + '_ECDF_over_time_log.' + output_format
                createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file, \
                    xscale='log', scale_factor=0.5, my_dpi=50)

                output_file_hd = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_' + var + '_ECDF_over_time_hd_log.' + output_format
                createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file_hd, \
                    xscale='log', scale_factor=0.5, my_dpi=600)

                output_file = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_' + var + '_ECDF_over_time.' + output_format
                createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file, \
                    scale_factor=0.5, my_dpi=50)

                output_file_hd = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_' + var + '_ECDF_over_time_hd.' + output_format
                createPlot( plots, "Temperature $[\degree C]$", "ECDF", output_file_hd, \
                    scale_factor=0.5, my_dpi=600)

            # my_dpi=100
            # fig4, axs = plt.subplots(1,figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
            # fig4.suptitle('-')
            # axs.plot(s_frame,label='reanalysis',linewidth=3)  
            # axs.plot(s_frame_k,label='kriging')
            # axs.tick_params( labelsize=40)
            # axs.set_ylabel(' ECDF',fontsize=40)
            # axs.set_xlabel('Prec [mm/hour]',fontsize=40)      
            # axs.legend(fontsize=40)  #,bbox_to_anchor=(1.05, 1), loc='upper left'
            # #axs.set_title('ECDF - Hourly spatial precipitation mean ',fontsize=80)     
            # fig4.savefig(pathout +'ECDF_'+var+'_high_resolution.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=600)
            # fig4.savefig(pathout +'ECDF_'+var+'.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=30)
            
            # raster=pd.concat([metadata.T,season.T],axis=1)
            # raster_k=pd.concat([metadata_k.T,season_k.T],axis=1)
            
            # raster.to_csv(pathout+'media_temporale_reanalysis_ptot_.csv',index=False) 
            # raster_k.to_csv(pathout+'media_temporale_kriging_ptot_.csv',index=False)            
          
            #----------------------------------Grafici MEDIE SPAZIALI------------------------------------------------------
           
            mean_r=pd.DataFrame()
            mean_k=pd.DataFrame()
            
            mean_r=df.mean (axis=1)
            mean_k=df_k.mean (axis=1)
            mean_r_month=mean_r.resample('MS').sum()
            mean_k_month=mean_k.resample('MS').sum()            
            
            mean_r_avg=mean_r.groupby([mean_r.index.month,mean_r.index.day]).mean()
            mean_r_avg_365=mean_r_avg.drop(mean_r_avg.index[59])
            mean_k_avg=mean_k.groupby([mean_k.index.month,mean_k.index.day]).mean()
            mean_k_avg_365=mean_k_avg.drop(mean_k_avg.index[59])
            mean_k_avg_365.reset_index(drop=True, inplace=True)
            mean_r_avg_365.reset_index(drop=True, inplace=True)
            year=pd.date_range(start='1/1/13', end='12/31/13')
            mean_r_avg_365.index=year
            mean_k_avg_365.index=year
            
            mean_r_avg_365=mean_r_avg_365.resample('MS').sum()
            mean_k_avg_365=mean_k_avg_365.resample('MS').sum()
            
            mean=mean_k_month-mean_r_month

            if var == "P":

                output_file = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_' + var + '_boxplot_monthly_spatial_bias_kr11-rea.' + output_format
                createBoxPlot( mean, "Time $[month]$", "Prec. bias $[mm]$", \
                    output_file, output_format=output_format, scale_factor=0.5, my_dpi=50 )

                output_file_hd = pathout + "meteo\\altoAdige\\precipitation\\" \
                    + 'meteo_AA_' + var + '_boxplot_monthly_spatial_bias_kr11-rea_hd.' + output_format
                createBoxPlot( mean, "Time $[month]$", "Prec. bias $[mm]$", \
                    output_file_hd, output_format=output_format, scale_factor=0.5, my_dpi=600 )
            
            elif var == "TMEAN":

                output_file = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_' + var + '_boxplot_monthly_spatial_bias_kr11-rea.' + output_format
                createBoxPlot( mean, "Time $[month]$", "Temp. bias $[\degree C]$", \
                    output_file, output_format=output_format, scale_factor=0.5, my_dpi=50 )

                output_file_hd = pathout + "meteo\\altoAdige\\temperature\\" \
                    + 'meteo_AA_' + var + '_boxplot_monthly_spatial_bias_kr11-rea_hd.' + output_format
                createBoxPlot( mean, "Time $[month]$", "Temp. bias $[\degree C]$", \
                    output_file_hd, output_format=output_format, scale_factor=0.5, my_dpi=600 )

            # fig20, axs = plt.subplots(1,figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
            # axs=seaborn.boxplot(mean.index.month,mean.values)
            # axs.set_ylabel(ylabel= ' Precipitation [mm/month]', fontsize = 40.0) # Y label
            # axs.set_xlabel(xlabel='month', fontsize = 40) # X label
            # #axs.set_title('Alto Adige Monthly  precipitation bias',fontsize=80)
            # axs.tick_params( labelsize=40)
            # fig20.savefig(pathout +'boxplot_AA_monthly_'+var+'_high_resolution.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=600)
            # fig20.savefig(pathout +'boxplot_AA_monthly_'+var+'.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=30)       

            # MEDIAN_k=mean_k_avg_365.median()
            # MEDIAN_r=mean_r_avg_365.median()
            
            # diff=mean_k_avg_365-mean_r_avg_365
            # print(diff)
            
            
            # fig6, axs = plt.subplots(1,figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
            

            # axs.plot(mean_r_avg_365,label='reanalysis')  
            # axs.plot(mean_k_avg_365,label='kriging') 
            # axs.axhline(MEDIAN_k,label='krig. median',color='r')
            # axs.axhline(MEDIAN_r,label='rea. median',color='k')
            # axs.tick_params( labelsize=40)
            # axs.set_ylabel(' Prec. [mm/month]',fontsize=40)
            # axs.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
            # axs.legend(fontsize=40,bbox_to_anchor=(1.05, 1), loc='upper left') 
            # #axs.set_title('Alto Adige Monthly  precipitation ',fontsize=80)     
            # fig6.savefig(pathout +var+'media_spaziale.jpeg',format='jpeg', bbox_inches='tight',facecolor='w', dpi=600)

         
           
            #----------------------------------Grafici BOXPLOT BASIN------------------------------------------------------
            
            
            basins=['Passirio','Senales']
            #-------------------boxplot 10 years--------------------
            for basin in basins:  
                    
                df_t=pd.DataFrame()
                box_t=pd.DataFrame()
                t_stations=path_sub +  basin+'/meteo/kriging/observations/precipitation/'
                t_file_tot = glob.glob(t_stations+'*.csv')
                for t_file in t_file_tot:
                    data_tot = pd.read_csv(t_file,index_col=0,parse_dates=True,skiprows=4,names=['values'])
                    data_tot=data_tot[t0:t1]
                    df_t=pd.concat([df_t,data_tot],axis=1)
                box_t_k=df_t.mean(axis=1)   
                    
                df_t=pd.DataFrame()
                box_t=pd.DataFrame()
                t_stations=path_sub +  basin+'/meteo/reanalysis/observations/precipitation/'
                t_file_tot = glob.glob(t_stations+'*.csv')
                for t_file in t_file_tot:
                    data_tot = pd.read_csv(t_file,index_col=0,parse_dates=True,skiprows=4,names=['values'])
                    data_tot=data_tot[t0:t1]
                    df_t=pd.concat([df_t,data_tot],axis=1)
                box_t_r=df_t.mean(axis=1) 
                 
                box_t= box_t_k - box_t_r 
                box_t=box_t.resample('MS').sum()

                output_file = pathout + "meteo\\" + basin + "\\precipitation\\monthly\\" \
                    + 'meteo_' + basin + '_precipitation_boxplot_monthly_temporal_bias_kr11-rea.' + output_format
                createBoxPlot( box_t, "Time $[month]$", "Prec. bias $[mm/month]$", \
                    output_file, output_format=output_format, my_dpi=50 )

                output_file_hd = pathout + "meteo\\" + basin + "\\precipitation\\monthly\\" \
                    + 'meteo_' + basin + '_precipitation_boxplot_monthly_temporal_bias_kr11-rea_hd.' + output_format
                createBoxPlot( box_t, "Time $[month]$", "Prec. bias $[mm/month]$", \
                    output_file_hd, output_format=output_format, my_dpi=600 )

                # fig20, ax = plt.subplots(figsize=(2550/my_dpi, 1000/my_dpi), tight_layout = {'pad': 0}, dpi=my_dpi)
                # seaborn.boxplot(box_t.index.month,box_t.values, ax=ax)
                # ax.set_ylabel(ylabel= 'Prec bias [mm/month]', fontsize = 40.0) # Y label
                # ax.set_xlabel(xlabel='month', fontsize = 40) # X label
                # #ax.set_title(basin,fontsize=80)
                # ax.tick_params( labelsize=40)
                # ax.set_ylim((-130, 100))
                # plt.xticks(rotation=90)
                # plt.savefig(pathout+'boxplot_monthly_P_'+basin+'_high_resolution.jpeg',format='jpeg', dpi=600)    
                # plt.savefig(pathout+'boxplot_monthly_P_'+basin+'.jpeg',format='jpeg', dpi=30)   
                # plt.show()