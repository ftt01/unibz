# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 12:15:19 2020

@author: Ariele Zanfei
"""

import Instances 
import numpy as np
import pandas as pd
import datetime
import joblib
import json

# suppress a warning
pd.options.mode.chained_assignment = None  # default='warn'

# =============================================================================
"""Main structure""" 
# =============================================================================

def main_model(    
    basin_id,
    streamflow_path,
    precipitation_path,
    temperature_path,
    start_date,
    end_date,
    output_path,
    n_output,
    lag_list_Q,
    lag_list_P,
    lag_list_T,
    batch,
    split_point,
    starting_hour,
    model_choice,
    grid_search=False,
    grid_search_epochs=100,
    grid_search_scorer=None,
    model_params=None,
    n=10):

    start_date = datetime.datetime.strptime(start_date, '%Y%m%d') + datetime.timedelta( hours=starting_hour )
    end_date =  datetime.datetime.strptime(end_date, '%Y%m%d')
    
    Manager = Instances.management_instance(
        string = streamflow_path,
        string_rain = precipitation_path,
        string_temp = temperature_path,
        weekend_exclusion = False, 
        year_exclusion = False,
        year_to_exclude = [], 
        mad_filter_value = None, 
        temporal_aggregation = 'hourly',
        standardize_data = False, 
        scaler_choice = 'minmax',
        start_date = start_date,
        end_date = end_date
    )
    
    """Modello previsionale base"""
    Model_creator = Instances.model_creation_instance(
        manager             = Manager, 
        model_type          = model_choice, #SVR MultiOutputSVR  Feed_forward   Lstm   ERNN    GRU
        lag_list            = lag_list_Q, 
        n_output            = n_output, 
        dummy_vars          = [
                                #'hour',       # variabile ora, 0, 1, 2 ...
                                #'day',       # giorno mensile, 0 il primo, 1 , 2 ..
                                # 'day type',   # 0 = workday, 1 = weekend
                                'month'      # 1 = gennaio, 2 = Febbraio ....,
                            ],
        rain_var            = True,
        rain_lags           = lag_list_P,
        rain_forecast       = True,
        rain_for_horizon    = n_output,
        temp_var            = True,
        temp_lags           = lag_list_T,
        temp_forecast       = True,
        temp_for_horizon    = n_output,
        day_cumsum          = True, 
        day_cumsum_horiz    = 7, 
        split_point         = split_point, 
        n_node              = [48, 96, 48], 
        n_layer             = 3, 
        act_function        = 'relu', 
        loss_function       = 'mse', 
        optimizer           = 'adam', 
        metrics             = 'mean_absolute_percentage_error', 
        soglia              = 100000,
        epochs              = grid_search_epochs, 
        batch_size          = batch, 
        grid_search         = grid_search,
        scorer              = grid_search_scorer,
        model_params        = model_params,
        cross_cycle         = 1,
        bagging_cycle       = 10, 
        do_cross_valid      = False, 
        do_bagging          =  False,
        starting_hour       = starting_hour,
        output_path         = output_path)
    
    #%%==================================================================
    """Post process"""
    # ===================================================================
    if grid_search == True:

        results = Model_creator.gs_results
        top_n_indices = results['mean_test_score'].argsort()[::-1][:n]  # Get the indices of the top n parameter sets
        top_n_params = [results['params'][i] for i in top_n_indices]  # Retrieve the top 10 parameter sets
        top_n_scores = [results['mean_test_score'][i] for i in top_n_indices]  # Retrieve the corresponding scores

        return zip(top_n_params, top_n_scores)
    else:
        # devo modificare le shapes
        Model_creator.real_concat.shape = (Model_creator.real_concat.size,1)
        Model_creator.model_concat.shape = (Model_creator.model_concat.size,1)

        post_prcessing = Instances.post_process_instance(
            model = Model_creator.model,
            d_m = Manager.d_m,
            real_concat = Model_creator.real_concat,
            model_concat = Model_creator.model_concat,
            test_year = 2022,
            correction = None, 
            want_complete_plot = True,
            want_partial_plot = False,
            want_boxplot = False,
            want_residuals = False,
            want_string = True, 
            want_minmax = False)

        # post_prcessing.p_p.plot_complete_prediction()

        #%%
        # post_prcessing.p_p.plot_partial_prediction(start_date = '2021-01-1',
        #                                            n_days = 360,
        #                                            y0 = 0, y1=70, save=True)




        # post_prcessing.p_p.plot_partial_prediction(start_date = '2022-10-15',
        #                                            n_days = 20,
        #                                            y0 = 0, y1=20, save=True)




        # post_prcessing.p_p.plot_partial_prediction(start_date = '2022-04-1',
        #                                            n_days = 120,
        #                                            y0 = 0, y1=10, save=True)




        # post_prcessing.p_p.plot_boxplot(time = 'monthly', error = 'ae')







        #%%

        # post_prcessing.p_p.plot_partial_prediction(start_date = '2021-06-14', n_days = 30*4)
        # print('\nfor that part:')
        # post_prcessing.p_p.errors(post_prcessing.p_p.df_real[datetime.date(2021,6,15):], 
        #                                           post_prcessing.p_p.df_test[datetime.date(2021,6,15):], 
        #                                           want_string = False, 
        #                                           want_minmax = False,
        #                                           Min = 1.4, Max = 4.5)    #1.4 4.5




        #%% Winter
        # only testing
        # real_df = post_prcessing.p_p.df_real[:datetime.date(2021,9,15)].copy()
        # forecast_df = post_prcessing.p_p.df_forcasted[:datetime.date(2021,9,15)].copy()
        # all data 
        real_df = post_prcessing.p_p.df_real.copy()
        forecast_df = post_prcessing.p_p.df_forcasted.copy()

        real_df[real_df['h average']==0]=0.1


        real_df = real_df.loc[(real_df.index.month==11) | \
                                                        (real_df.index.month==12) | \
                                                        (real_df.index.month==1) | \
                                                        (real_df.index.month==2)]

        forecast_df = forecast_df.loc[(forecast_df.index.month==11) | \
                                                        (forecast_df.index.month==12) | \
                                                        (forecast_df.index.month==1) | \
                                                        (forecast_df.index.month==2)]

        print('\nfor that part Winter:')
        post_prcessing.p_p.errors(real_df, forecast_df, 
                                    want_string = False, 
                                    want_minmax = False,
                                    Min = 1.4, Max = 4.5) 

        #%% Spring
        # real_df = post_prcessing.p_p.df_real[:datetime.date(2021,9,15)].copy()
        # forecast_df = post_prcessing.p_p.df_forcasted[:datetime.date(2021,9,15)].copy()
        # all data 
        real_df = post_prcessing.p_p.df_real.copy()
        forecast_df = post_prcessing.p_p.df_forcasted.copy()

        real_df[real_df['h average']==0]=0.1

        real_df = real_df.loc[(real_df.index.month==3) | \
                                                        (real_df.index.month==4) | \
                                                        (real_df.index.month==5) | \
                                                        (real_df.index.month==6)]

        forecast_df = forecast_df.loc[(forecast_df.index.month==3) | \
                                                        (forecast_df.index.month == 4) |
                                                        (forecast_df.index.month == 5) |
                                                        (forecast_df.index.month==6)]

        print('\nfor that part Spring:')
        post_prcessing.p_p.errors(real_df, forecast_df, 
                                                want_string = False, 
                                                want_minmax = False,
                                                Min = 1.4, Max = 4.5) 

        #%% Sommer
        # real_df = post_prcessing.p_p.df_real[:datetime.date(2021,9,15)].copy()
        # forecast_df = post_prcessing.p_p.df_forcasted[:datetime.date(2021,9,15)].copy()
        # all data 
        real_df = post_prcessing.p_p.df_real.copy()
        forecast_df = post_prcessing.p_p.df_forcasted.copy()


        real_df[real_df['h average']==0]=0.1

        real_df = real_df.loc[(real_df.index.month==7) | \
                                                        (real_df.index.month==8) | \
                                                        (real_df.index.month==9) | \
                                                        (real_df.index.month==10)]

        forecast_df = forecast_df.loc[(forecast_df.index.month==7) | \
                                                        (forecast_df.index.month == 8) |
                                                        (forecast_df.index.month == 9) |
                                                        (forecast_df.index.month==10)]

        print('\nfor that part Sommer:')
        post_prcessing.p_p.errors(real_df, forecast_df, 
                                                want_string = False, 
                                                want_minmax = False,
                                                Min = 1.4, Max = 4.5) 

        #%% Save a config file
        path_model = Model_creator.model.save_path
            
        config = {
            'basin' : basin_id,
            'w_ex' : Manager.w_ex,
            'year_exclusion' :        Manager.year_exclusion,
            'year_to_exclude' :       Manager.year_to_exclude, 
            'mad_filter_value' :      Manager.mad, 
            'temporal_aggregation' :  Manager.temp_aggr,
            'standardize_data':       Manager.std_data, 
            'scaler_choice' :         Manager.scaler_choice,
            #
            'model_type' :            Model_creator.model_type,
            'n_output' :              Model_creator.n_output,
            'lag_list' :              Model_creator.lag_list,
            'temp_var' :              Model_creator.temp_var,
            'temp_lags' :             Model_creator.temp_lags,
            'rain_var' :              Model_creator.rain_var,
            'rain_lags' :             Model_creator.rain_lags,
            'rain_forecast' :         Model_creator.rain_forecast,
            'rain_for_horizon' :      Model_creator.rain_for_horizon,
            'temp_forecast' :         Model_creator.temp_forecast,
            'temp_for_horizon' :      Model_creator.temp_for_horizon,
            'day_cumsum' :            Model_creator.day_cumsum,
            'day_cumsum_horiz' :      Model_creator.day_cumsum_horiz,
            'dummy_vars' :            Model_creator.dummy_vars,
            'starting_hour' :         Model_creator.starting_hour
        }

        # save the configuration file
        with open(path_model+'data.json', 'w') as fp:
            json.dump(config, fp ,indent=2)

        # save the scaler
        scaler_filename1 = "univariate_scaler.save"
        joblib.dump(Manager.univariate_scaler,
                    path_model + scaler_filename1)     
        scaler_filename2 = "multivariate_scaler.save"
        joblib.dump(Model_creator.full_scaler,
                    path_model +  scaler_filename2)
        
        return None