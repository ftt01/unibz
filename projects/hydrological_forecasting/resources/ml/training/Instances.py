# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:12:32 2021

@author: Ariele Zanfei
"""

from Dataset_management import Dataset_management
import Model_generator    
import functions
import numpy as np
import pandas as pd
import datetime


# =============================================================================
"""Classe per la gestione del dataset"""
# =============================================================================
class management_instance():
    
    """PARAMETRI:
    - string = nome del file
    - weekend_exclusion = True or false, esclude i weekend dal dataset
    - year_exclusion = True or false, escludi anni
    - year_to_exclude = quali anni vado ad escludere? lista
    - mad_filter_value = filtro mean absolute deviation intra day
    - standardize_data = True or false
    - temporal_aggregation = scelta per il resample
    - scaler_choice = alcuni implementati. minmax è il classico
    - 
    """
    
    def __init__(self, string, string_rain, string_temp, year_to_exclude,
                 mad_filter_value, temporal_aggregation, scaler_choice,
                 standardize_data=False, weekend_exclusion=False,
                 year_exclusion = False, var_name=None,
                 start_date=None, end_date=None):

        self.d_m = Dataset_management(string)
        self.orig_string = string
        self.string_rain = string_rain
        self.string_temp = string_temp
        self.w_ex = weekend_exclusion
        self.year_exclusion = year_exclusion
        self.year_to_exclude = year_to_exclude
        self.mad = mad_filter_value
        self.temp_aggr = temporal_aggregation
        self.std_data = standardize_data
        self.scaler_choice = scaler_choice
        self.var_name = var_name
        self.start_date = start_date
        self.end_date = end_date
        # runno il manage
        self.manage()
        
    # metodo che contiene tutti i metodi ordinati
    def manage(self):
        
        self.df_original = self.d_m.parsing_idro(self.start_date,
                                                 self.end_date)
        #exclude weekend?    
        self.d_m.weekend_exclusion(exclusion=False)
        #escludo anni?
        if self.year_exclusion==True:
            for y in self.year_to_exclude:
                self.d_m.year_exclusion(exclusion_bis=self.year_exclusion,
                                        year = y)
        else:
            self.d_m.year_exclusion(exclusion_bis=self.year_exclusion)
        # filtro per i nan    
        #self.d_m.nan_filter(method = 'fill with zero')
        # un primo filtraggio sugli zeri
        self.d_m.first_filter(filter_zeros=False)
        # filtraggio sui -999
        self.d_m.filter_999()
        # creo i dataset medi
        self.d_m.daily_average()
        self.d_m.hourly_average()
        # filtro sulla mean deviation intra daily
        self.df = self.d_m.MAD_daily_filter(filtering=False,
                                            mad_val = self.mad)
        # dopo i filtri ricreo le medie
        self.d_m.daily_average()
        self.d_m.hourly_average()
        # standardizzo i dati?
        self.d_m.standardize_data(std=self.std_data)
        # # data imputation
        self.d_m.nan_filter2(method = 'rebuild')
        # creo i vari dataset e scaler
        self.dataset_univariate = self.d_m.Temporal_aggregation(temporal_aggr=self.temp_aggr,
                                                                var_name=self.var_name)
        self.scaler_choice = self.scaler_choice
        _, self.univariate_scaler = self.d_m.Scaling(self.dataset_univariate,
                                                     self.scaler_choice)
        _, self.multivariate_scaler = self.d_m.Scaling(self.dataset_univariate,
                                                       self.scaler_choice)
        #pacf e plot 
        #self.pacf = self.d_m.Autocorrelation_analysis(nlags= 500)
        # self.d_m.plot_ts_basic(figsize =(19,5), start_date='2010-01-1' , save = False)



# =============================================================================
"""Classe per creazione del modello per forecasting"""
# =============================================================================
class model_creation_instance():

    """PARAMETRI:
         - manager = il file creato dalla classe management_instance
         - model_type = tipologia di modello da creare
         - lag_list = lista contenente i lag
         - n_output = numero output del modello
         - dummy_vars = lista con le dummy
         - do_cross_valid = True or False
         - do_bagging = True or False
         - n_node = lista con i nodi dei layer
         - n_layer = numero di layer
         - act_function = tipo di activation function da usare (e.g. relu)
         - loss_function = loss function del training
         - optimizer = scelta ottimizzatore (e.g. adam, adagrad ...)
         - metrics = metrica (accuracy)
         - epochs = numero di epoche training
         - batch_size = dimensione del batch
         - cross_cycle = numero cicli cross validation
         - bagging_cycle = numero cicli bagging
         - """
         
    def __init__(
            self, manager, model_type, lag_list, rain_lags, temp_lags, 
            n_output, dummy_vars, split_point, n_node, n_layer,
            act_function, loss_function, optimizer, metrics, soglia, epochs,
            batch_size, grid_search=False, scorer='rmse', model_params=None,
            temp_forecast=None, temp_for_horizon=None, 
            rain_for_horizon=None, rain_var=False,  
            rain_forecast=False, temp_var=False, day_cumsum=False,
            day_cumsum_horiz = None, cross_cycle=None,
            bagging_cycle=None, do_cross_valid=False, do_bagging=False,
            starting_hour=None, output_path='./'):
             
        self.mng = manager
        self.model_type = model_type
        self.grid_search = grid_search
        self.grid_search_scorer = scorer,
        if type(self.grid_search_scorer) == tuple:
            self.grid_search_scorer = self.grid_search_scorer[0]
        self.model_params = model_params
        self.lag_list = lag_list
        self.n_output = n_output
        self.dummy_vars = dummy_vars
        self.rain_var = rain_var
        self.rain_lags = rain_lags
        self.rain_forecast = rain_forecast
        self.rain_for_horizon=rain_for_horizon
        self.temp_forecast = temp_forecast
        self.temp_for_horizon = temp_for_horizon
        self.day_cumsum = day_cumsum
        self.day_cumsum_horiz = day_cumsum_horiz
        self.temp_var = temp_var
        self.temp_lags = temp_lags
        self.split_point = split_point
        self.n_node = n_node
        self.n_layer = n_layer
        self.act_function = act_function
        self.loss_function = loss_function
        self.optimizer = optimizer
        self.metrics = metrics
        self.soglia = soglia
        self.epochs = epochs
        self.batch_size = batch_size
        self.cross_cycle = cross_cycle
        self.bagging_cycle = bagging_cycle
        self.cv = do_cross_valid
        self.bag = do_bagging
        self.starting_hour = starting_hour
        self.save_path = output_path
        # lancio il model creator
        self.model_creation()
        
    # metodo che contiene tutti i metodi ordinati  per creare il modello  
    def model_creation(self):
        #genero il modello 
        self.model = Model_generator.Model_generator(
            self.mng.dataset_univariate,
            model_type=self.model_type,
            data_manager = self.mng.d_m,
            univariate_scaler = self.mng.univariate_scaler,
            multivariate_scaler = self.mng.multivariate_scaler,
            n_output = self.n_output,
            manager = self.mng,
            grid_search = self.grid_search,
            model_params = self.model_params,
            save_path = self.save_path)

        #compongo il dataset con i lag e la struttura per output
        self.dataset_multivariate = self.model.lag_selector(
            other_var=True,
            lista_lag = self.lag_list,
            n_output=self.n_output,
            temperature=self.temp_var,
            temp_lags = self.temp_lags,
            rainfall=self.rain_var,
            rain_lags= self.rain_lags,
            rain_forecast=self.rain_forecast,
            rain_for_horizon=self.rain_for_horizon,
            temp_forecast = self.temp_forecast,
            temp_for_horizon = self.temp_for_horizon,
            day_cumsum_rain = self.day_cumsum,
            day_cumsum_horiz_rain = self.day_cumsum_horiz
        )
        if self.starting_hour !=None:
            self.starting_date = datetime.datetime(
                self.dataset_multivariate.index[1].year,
                self.dataset_multivariate.index[1].month,
                self.dataset_multivariate.index[1].day,
                self.starting_hour) + datetime.timedelta(hours = 24)
            # faccio partire il dataset multivariate da li
            self.dataset_multivariate = self.dataset_multivariate[self.starting_date:]
            self.mng.dataset_univariate = self.mng.dataset_univariate[self.starting_date:]
            self.model.dataset = self.model.dataset[self.starting_date:]

        #aggiungo le dummy variables
        self.dataset_multivariate = self.model.dummy_variable(self.dummy_vars)
        #faccio lo shuffle se richiesto
        self.shuffle_dataset = self.model.dataset_shuffle(cross_valid=self.cv,
                                                          bagging = self.bag)
        #riscalo il nuovo dataset multivariato
        self.scaled, self.scaler = self.mng.d_m.Scaling(self.shuffle_dataset,
                                                        self.mng.scaler_choice)
        
        # =============================================================================
        #         Questa opzione con commentata la sopra per usare scaler diversi.
        #         Ricordare di andare in Model_generator e modificare lag_selector
        # self.scaled = self.shuffle_dataset.values
        # =============================================================================
        
        #calcolarmi tutta la time series scalata mi serve per la parte di comparison
        self.full_scaled, self.full_scaler = self.mng.d_m.Scaling(
            self.dataset_multivariate, self.mng.scaler_choice)
        #vado a suddividere il dataset in train e test
        self.train_X, self.train_y, self.test_X, self.test_y = self.model.test_train_splitter(
            scaled_dataset=self.scaled,
            split_point = self.split_point,
            flip_data =False)
        #faccio un salvataggio utile
        self.model.input_saver(self.full_scaled)
        ## here the grid_search if requested
        if self.grid_search == True:
            self.gs_results = self.model.model_grid_search(
                train_X = self.train_X,
                train_y = self.train_y,
                test_X  = self.test_X,
                test_y  = self.test_y,
                model   = self.model_type,
                loss    = self.loss_function,
                scorer  = self.grid_search_scorer,
                optimizer   = self.optimizer,
                param_grid  = self.model_params,
                epochs      = self.epochs)
        else:
            ## creo il modello nella sua struttura vuota
            self.model.model_creation(
                train_X = self.train_X,
                n_node = self.n_node,
                n_layer = self.n_layer,
                act_function = self.act_function,
                optimizer = self.optimizer,
                loss_function = self.loss_function) 
            ## vado a inizializzare il training
            self.forecasting_model = self.model.Train(
                loss = self.loss_function,
                optimizer = self.optimizer,
                metrics = self.metrics,
                soglia = self.soglia,
                train_X = self.train_X,
                train_y = self.train_y,
                test_X = self.test_X,
                test_y = self.test_y,
                epochs = self.epochs,
                batch = self.batch_size,
                cross_cycle = self.cross_cycle,
                bagging_cycle = self.bagging_cycle)
            #vado a rigenerare riscalando gli output i risultati
            self.real_concat, self.model_concat = self.model.first_prediction(
                self.train_X, self.test_X, self.train_y, self.test_y)

# =============================================================================
"""Classe per processare i risultati e vedere un po di plot"""
# =============================================================================
class post_process_instance():

    """PARAMETRI:
         - 
         - """
         
    def __init__(self, model, d_m,  real_concat, model_concat, test_year,
                 correction=None, want_complete_plot = True, 
                 want_partial_plot = True, want_boxplot = True,
                 want_residuals = True, want_string=True, want_minmax=None, res=None):
        self.model = model
        self.d_m = d_m
        self.real_concat = real_concat
        self.model_concat = model_concat
        self.test_year = test_year
        self.correction = correction
        self.want_string = want_string
        self.want_minmax = want_minmax
        self.want_partial_plot = want_partial_plot
        self.want_boxplot = want_boxplot
        self.want_complete_plot = want_complete_plot
        self.want_residuals = want_residuals
        # runno l'istanza
        self.post_process(res)
        
    
    def post_process(self, res):
        
        self.p_p = functions.post_processing(self.model, self.d_m)
        self.real, self.test, self.train = self.p_p.Dataframe_gen(
            bias_correction=self.correction)
        #self.p_p.plot_history()
        # cerco le date che dividono il dataset in train e test
        date0 = self.real.index.date[0]
        date_end_train = self.train.index.date[-self.train.isna().sum().values[0]]
        # print some information
        print('\nfirst date:' , date0)
        print('\nend train date:' , date_end_train)
        print('\nfinal date:' , self.real.index.date[-1])
        # per sicurezza aggiungo un giorno
        date_end_train = date_end_train 
        print('\nfor train part:')
        # tolgo un giorno per evitare i nan
        train_string = self.p_p.errors(self.real[date0 : date_end_train- datetime.timedelta(days=1)], 
                                       self.train[date0 : date_end_train- datetime.timedelta(days=1)], 
                                       want_string = self.want_string, 
                                       want_minmax = self.want_minmax,
                                       Min = 1.4, Max = 4.5)
        
        print('\nfor test part:')
        #aggiungo un giorno per evitare i nan
        test_string = self.p_p.errors(self.real[date_end_train + datetime.timedelta(days=1):], 
                                      self.test[date_end_train + datetime.timedelta(days=1):], 
                                      want_string = self.want_string, 
                                      want_minmax = self.want_minmax,
                                      Min = 1.4, Max = 4.5)
        
        # save data
        self.model.model_saver(do_you_want_to_save=True, error_string= '\nTRAIN:\n' + \
                               train_string + '\n\nTEST:\n' + test_string)
        self.p_p.saver_result()
        # plot di tutta la time series
        if  self.want_complete_plot== True:
            self.p_p.plot_complete_prediction()
        # plot parziale con parametri da scegliere
        if  self.want_partial_plot== True:
            self.p_p.plot_partial_prediction(start_date = '2018-01-01', n_days = 300)
            self.p_p.plot_partial_prediction(start_date = '2018-01-01', n_days = 30)
        # plotto boxplot degli errori (che scelgo)
        if  self.want_boxplot== True:
            self.p_p.plot_boxplot(time='monthly', error='ae', dataset = None)
        # plotto i residui
        if  self.want_residuals== True:
            self.p_p.plot_differences(time='hourly', year=None)

        if res != None:
            res[1].append(
                (res[0],
                self.p_p.best_model(
                    self.real[date_end_train + datetime.timedelta(days=1):], 
                    self.test[date_end_train + datetime.timedelta(days=1):])
                )
            )