# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 12:15:19 2020

@author: Ariele Zanfei
"""

import Instances 
import pandas as pd
import datetime
import os
import joblib
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#%==================================================================
"""Funzioni """ 
# ===================================================================
def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

def plot_forecast(df_to_plot, save_path = None,
                  display_plot = False,
                  df_ens = None, bands=False):
    if display_plot:
        fig, (ax1,ax2,ax3) = plt.subplots(3, figsize=(19, 10),
                                          gridspec_kw={'height_ratios': [3,1,1]})
        if isinstance(df_ens, type(None)) == False:
            for cols in df_ens.columns:
                if 'predicted' in cols:
                    if bands == False:
                        ax1.plot(df_ens[cols], color='grey', alpha=0.9, linewidth=0.6)
                    else:
                        pass
                elif 'rain' in cols:
                    ax2.plot(df_ens[cols], color='grey', alpha=0.9, linewidth=0.6)
                elif 'temp' in cols:
                    ax3.plot(df_ens[cols], color='grey', alpha=0.9, linewidth=0.6)
        if bands == True:
            ax1.fill_between(
                df_ens.index,
                df_ens[[col for col in df_ens.columns if 'predicted' in col]].quantile(q=0.05, axis=1), 
                df_ens[[col for col in df_ens.columns if 'predicted' in col]].quantile(q=0.95, axis=1),
                color='grey', alpha=0.2)
        ax1.plot(df_to_plot['predicted'], linewidth=1.5)
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%dT%H:%M')) 
        ax1.format_xdata = mdates.DateFormatter('%Y%m%dT%H:%M')
        ax1.legend()
        ax1.set_ylabel('Streamflow $[mc/s]$')
        ax1.get_yaxis().set_label_coords(-0.05,0.5)
        ax1.grid(True)
        #
        ax2.plot(df_to_plot['rain'], linewidth=1.5)
        ax2.xaxis.set_major_locator(mdates.HourLocator(interval=3))
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%dT%H:%M')) 
        ax2.format_xdata = mdates.DateFormatter('%Y%m%dT%H:%M')
        ax2.set_ylabel('Rain $[mm]$')
        ax2.get_yaxis().set_label_coords(-0.05,0.5)
        ax2.grid(True)
        #
        ax3.plot(df_to_plot['temp'], linewidth=1.5)
        ax3.xaxis.set_major_locator(mdates.HourLocator(interval=3))
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%dT%H:%M')) 
        ax3.format_xdata = mdates.DateFormatter('%Y%m%dT%H:%M')
        ax3.set_ylabel('Temp $[\degree C]$')
        ax3.get_yaxis().set_label_coords(-0.05,0.5)
        ax3.grid(True)
        #
        fig.autofmt_xdate()
        plt.savefig(save_path,
                    dpi=200, bbox_inches='tight', orientation='portrait')

def append_data(current_data, additional_data):

    current_data = current_data.reset_index()
    additional_data = additional_data.reset_index()

    current_data = pd.concat([current_data[current_data['index'].isin(
        additional_data['index']) == False], additional_data], ignore_index=True)

    # print(data)
    current_data.dropna(subset=['index'], inplace=True)
    current_data.sort_values(by=['index'], inplace=True)

    current_data = current_data.set_index('index')
    current_data = current_data[current_data.index.notnull()]

    return current_data
        
#%==================================================================
"""Main function """ 
# ===================================================================     
def main(
    start_date=None,
    model_path='../Model_repository/B001/SB001/26_09_2022/26_09_2022 at 09h 05m 06s/',
    input_data_path='../Model_repository/B001/SB001/R003/',
    output_path='../Forecasting/B001/SB001/R003/',
    type_of_simulation = 'ensemble'):
    
    # NOTA: type of simulation può essere o 'mean' o 'ensemble
    # =============================================================================
    # =============================================================================
    # # è fondamentale scegliere il model_path del modello, perchè poi le info sul bacino
    # # sono contenute nel json di config
    # # Quindi serve un model_path iniziale che sia già configurato su bacino
    # =============================================================================
    # =============================================================================

    f = open(model_path + 'data.json')
      
    # returns JSON object as a dictionary
    data = json.load(f)
      
    # Closing file
    f.close()
    
    # call it
    data['w_ex']
    
    
    # the prediction model is
    prediction_model = joblib.load(model_path + 'MultiOutputSVR_model.joblib')
    
    # univariate scaler
    univariate_scaler = joblib.load(model_path + 'univariate_scaler.save')
    
    # multivariate scaler
    multivariate_scaler = joblib.load(model_path + 'multivariate_scaler.save')
    
    
    #%==================================================================
    """Istanza vera del Forecasting operativo""" 
    # ===================================================================
    
    # questo deve diventare un today
    if start_date == None:
        date_to_forecast = datetime.datetime.now().date()# datetime.date(2022, 9, 26)
    else:
        date_to_forecast = datetime.datetime.strptime( start_date, '%Y%m%d' )

    prediction_date = date_to_forecast.strftime("%Y%m%d")
    
    file_to_forecast = to_integer(date_to_forecast)
    # aggiungo le ore e i minuti
    date_to_forecast = datetime.datetime(
        date_to_forecast.year,
        date_to_forecast.month,
        date_to_forecast.day, 
        data["starting_hour"], 0)
    
    # =============================================================================
    # inizializzo la classe fatta appositamente per fare forecast a seguito della
    # costituzione del modello
    # =============================================================================
    forecast_operativo = Instances.operative_flow_forecast(
                                date_as_number = file_to_forecast,
                                quantiles_flow = None,
                                quantiles_rain = type_of_simulation,
                                quantiles_temp = type_of_simulation, 
                                start_date     = date_to_forecast - datetime.timedelta(days=2),
                                end_date       = date_to_forecast + datetime.timedelta(days=2),
                                prediction_model = prediction_model,
                                path_data = input_data_path)
    
    # =============================================================================
    # Importo i dati, utilizzo il file di configurazione per riprodurre tutte le 
    # info sul fitting del modello
    # =============================================================================
    forecast_operativo.import_meteo_forecast(
        weekend_exclusion    = data['w_ex'], 
        year_exclusion       = data['year_exclusion'],
        year_to_exclude      = data['year_to_exclude'], 
        mad_filter_value     = data['mad_filter_value'], 
        temporal_aggregation = data['temporal_aggregation'], 
        standardize_data     = data['standardize_data'],
        scaler_choice        = data['scaler_choice'], 
        univariate_scaler    = univariate_scaler,
        multivariate_scaler  = multivariate_scaler)
    
    
    # =============================================================================
    # Inizializzo il metodo per fare il forecast. Anche quile info provengono 
    # dal file di configurazione
    # =============================================================================
    if type_of_simulation == 'ensemble':
        df_ensemble = pd.DataFrame(index = pd.date_range(
                start = date_to_forecast,
                end = date_to_forecast + datetime.timedelta(hours=data['n_output']-1),
                    freq='H'))
        for ens in range(20): #20 ensemble
            forecast_operativo.flow_forecast(
                model_type       = data['model_type'], 
                n_output         = data['n_output'], 
                lag_list         = data['lag_list'], 
                temp_var         = data['temp_var'],
                temp_lags        = data['temp_lags'], 
                rain_var         = data['rain_var'], 
                rain_lags        = data['rain_lags'], 
                rain_forecast    = data['rain_forecast'],
                rain_for_horizon = data['rain_for_horizon'], 
                temp_forecast    = data['temp_forecast'], 
                temp_for_horizon = data['temp_for_horizon'],
                day_cumsum       = data['day_cumsum'], 
                day_cumsum_horiz = data['day_cumsum_horiz'],
                dummy_vars       = data['dummy_vars'],
                ens_id = ens+1)
            
            # =============================================================================
            # Le istruzioni successive seevono esclusivamente per formattare l'output
            # =============================================================================
            print(file_to_forecast, 'ensemble:', str(ens+1))  
            
            # fillo il dataframe
            df_ensemble['predicted_'+str(ens)] = univariate_scaler.inverse_transform(
                                        forecast_operativo.testPredict)
            df_ensemble['real_'+str(ens)]      = forecast_operativo.Manager.df_original
            df_ensemble['rain_'+str(ens)]      = forecast_operativo.model.model_rain.dataset_univariate
            df_ensemble['temp_'+str(ens)]      = forecast_operativo.model.model_temp.dataset_univariate
        # # quello che ci interessa è:
        # df_ensemble = df_ensemble[date_to_forecast : 
        #                         date_to_forecast + datetime.timedelta(hours=37)]

    else:
        df_ensemble = None     
    # =============================================================================
    # reinizializzo la classe per fare il forecast solo con il mean
    # =============================================================================
    forecast_operativo = Instances.operative_flow_forecast(
                                date_as_number = file_to_forecast,
                                quantiles_flow = None,
                                quantiles_rain = 'mean',
                                quantiles_temp = 'mean', 
                                start_date     = date_to_forecast - datetime.timedelta(days=2),
                                end_date       = date_to_forecast + datetime.timedelta(days=2),
                                prediction_model = prediction_model,
                                path_data = input_data_path)
    # =============================================================================
    # Importo i dati nuovamente
    # =============================================================================
    forecast_operativo.import_meteo_forecast(
        weekend_exclusion    = data['w_ex'], 
        year_exclusion       = data['year_exclusion'],
        year_to_exclude      = data['year_to_exclude'], 
        mad_filter_value     = data['mad_filter_value'], 
        temporal_aggregation = data['temporal_aggregation'], 
        standardize_data     = data['standardize_data'],
        scaler_choice        = data['scaler_choice'], 
        univariate_scaler    = univariate_scaler,
        multivariate_scaler  = multivariate_scaler)
    
    # =============================================================================
    # Inizializzo il metodo per fare il forecast. Anche quile info provengono 
    # dal file di configurazione
    # =============================================================================
    forecast_operativo.flow_forecast(
        model_type       = data['model_type'], 
        n_output         = data['n_output'], 
        lag_list         = data['lag_list'], 
        temp_var         = data['temp_var'],
        temp_lags        = data['temp_lags'], 
        rain_var         = data['rain_var'], 
        rain_lags        = data['rain_lags'], 
        rain_forecast    = data['rain_forecast'],
        rain_for_horizon = data['rain_for_horizon'], 
        temp_forecast    = data['temp_forecast'], 
        temp_for_horizon = data['temp_for_horizon'],
        day_cumsum       = data['day_cumsum'], 
        day_cumsum_horiz = data['day_cumsum_horiz'],
        dummy_vars       = data['dummy_vars'],
        ens_id = None)
    
    # =============================================================================
    # Le istruzioni successive seevono esclusivamente per formattare l'output
    # =============================================================================
    print(file_to_forecast)    
    df_predict = pd.DataFrame(index = pd.date_range(
            start = date_to_forecast,
            end = date_to_forecast + datetime.timedelta(hours=data['n_output']-1),
                freq='H'))
    # fillo il dataframe
    df_predict['predicted'] = univariate_scaler.inverse_transform(
                                forecast_operativo.testPredict)
    df_predict['real']      = forecast_operativo.Manager.df_original
    df_predict['rain']      = forecast_operativo.model.model_rain.dataset_univariate
    df_predict['temp']      = forecast_operativo.model.model_temp.dataset_univariate
    # # quello che ci interessa è:
    # df_predict = df_predict[date_to_forecast : 
    #                         date_to_forecast + datetime.timedelta(hours=37)]    

            
    #%% Salvo il file (da modificare)
    new_path = output_path + prediction_date + "/"
    try:
        os.makedirs(new_path)
    except FileExistsError:
        pass
    
    # salvo un file singolo con il nome della data
    if type_of_simulation == 'ensemble':
        try:
            df_ensemble_flow = df_ensemble.filter(regex='predicted')
            df_ensemble_flow.to_csv(
                new_path + '/ens_forecast.csv',
                sep=',',encoding='utf-8', index=True, header=True,
                float_format='%.5f', index_label='index')
        except Exception as e:
            print("Exception: " + str(e))

    df_predict['predicted'].to_csv(
        new_path + '/forecast.csv', sep=',',
        encoding='utf-8', index=True, header=True,
        float_format='%.5f', index_label='index')
        
    #%% Salvo il plot in pdf
    # if type_of_simulation== 'ensemble':
    plot_forecast(df_to_plot = df_predict,
                  save_path = new_path + prediction_date +'.pdf',
                  display_plot = False,
                  df_ens = df_ensemble,
                  bands = False)
    
    plot_forecast(df_to_plot = df_predict,
                  save_path = new_path + prediction_date +'_bands.pdf',
                  display_plot = False,
                  df_ens = df_ensemble,
                  bands = True)
    
    # plot_forecast(df_to_plot = df_predict,
    #               save_path = output_path + 'last_run.pdf',
    #               display_plot = False,
    #               df_ens = df_ensemble,
    #               bands = False)
    
    # df_to_save = df_predict.copy()
    # # df_to_save[prediction_date] = df_to_save['predicted']
    # df_to_save.rename(columns={'predicted':prediction_date}, inplace=True)

    # indexes_to_save = []
    # first_day = df_to_save.index[0].day
    # for idx in df_to_save.index:
    #     c_day = idx.day
    #     if c_day == first_day:
    #         indexes_to_save.append( """Day{n}_H{m}""".format(n=1, m=str(idx.hour).zfill(2)) )
    #     else:
    #         indexes_to_save.append( """Day{n}_H{m}""".format(n=2, m=str(idx.hour).zfill(2)) )

    # df_to_save.index = indexes_to_save
    
    # try: #○ prova a sovrascrivere il file
    #     file_to_overwrite = pd.read_csv(output_path + '/forecast.csv',
    #                                     index_col = 'index')
    #     file_to_overwrite[prediction_date] = df_to_save[prediction_date].values
    #     file_to_overwrite.to_csv(
    #         output_path + '/forecast.csv', sep=',',encoding='utf-8', index=True, header=True,
    #         float_format='%.5f', index_label='index')
            
    # except FileNotFoundError: # se non lo trovo, lo creo
    #     df_to_save[prediction_date].to_csv(
    #         output_path + '/forecast.csv',
    #         sep=',',encoding='utf-8', index=True, header=True,
    #         float_format='%.5f', index_label='index')
            
    
    # #%% modify file
    # # df_to_save2.index = df_to_save2.index+datetime.timedelta(hours=24)
    # df_to_save2 = pd.DataFrame(df_predict[date_to_forecast+\
    #     datetime.timedelta(hours=14):]['predicted'])
    # df_to_save2.index.name = 'index'

    # try: #○ prova a sovrascrivere il file
    #     file_to_overwrite = pd.read_csv(output_path + '/forecast_1col.csv',
    #                                     index_col = 'index_CET')
    #     file_to_overwrite.index.name = 'index'              
    #     file_to_overwrite.index = pd.to_datetime(file_to_overwrite.index)

    #     file_to_overwrite = append_data(file_to_overwrite, df_to_save2)
        
    #     # file_to_overwrite = pd.concat([file_to_overwrite, df_to_save2], ignore_index=False)
    #     file_to_overwrite.to_csv(output_path + '/forecast_1col.csv', sep=',',encoding='utf-8', index=True, header=True,
    #                  float_format='%.5f', index_label='index_CET')
            
    # except FileNotFoundError: # se non lo trovo, lo creo
    #     df_to_save2.to_csv(output_path + '/forecast_1col.csv', sep=',',encoding='utf-8', index=True, header=True,
    #                  float_format='%.5f', index_label='index_CET')


# #%%==================================================================
# """Main Launcher """ 
# # ===================================================================  
# main(start_date = '20221001', 
#      model_path = '../Model_repository/B001/SB001/26_09_2022/26_09_2022 at 09h 05m 06s/',
#      input_data_path = '../Model_repository/B001/SB001/R003/',
#      output_path = 'output',
#      type_of_simulation = 'ensemble')