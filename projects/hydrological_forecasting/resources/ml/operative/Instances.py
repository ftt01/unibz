# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:12:32 2021

@author: Ariele Zanfei
"""

from Dataset_management import Dataset_management
import Model_generator
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
                 start_date=None, end_date=None, ens_id=None):

        self.d_m = Dataset_management(string)
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
        self.ens_id = ens_id  
        # runno il manage
        self.manage()
        
    # metodo che contiene tutti i metodi ordinati
    def manage(self):
        
        self.df_original = self.d_m.parsing_idro(self.start_date,
                                                 self.end_date,
                                                 self.ens_id)
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
         
    def __init__(self, manager, model_type, lag_list, rain_lags, temp_lags, 
                 n_output, dummy_vars, split_point, n_node, n_layer,
                 act_function, loss_function, optimizer, metrics, soglia, epochs,
                 batch_size, temp_forecast=None, temp_for_horizon=None, 
                 rain_for_horizon=None, rain_var=False,  
                 rain_forecast=False, temp_var=False, day_cumsum=False,
                 day_cumsum_horiz = None, cross_cycle=None,
                 bagging_cycle=None, do_cross_valid=False, do_bagging=False, starting_hour=None):
             
        self.mng = manager
        self.model_type = model_type
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
        # lancio il model creator
        self.model_creation()
        

    # metodo che contiene tutti i metodi ordinati  per creare il modello  
    def model_creation(self):
        #genero il modello 
        self.model = Model_generator.Model_generator(self.mng.dataset_univariate,
                                     model_type=self.model_type,
                                     data_manager = self.mng.d_m,
                                     univariate_scaler = self.mng.univariate_scaler,
                                     multivariate_scaler = self.mng.multivariate_scaler,
                                     n_output = self.n_output,
                                     manager = self.mng)

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
            day_cumsum_horiz_rain = self.day_cumsum_horiz)
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

        # faccio partire il dataset multivariate da li
        self.dataset_multivariate = self.dataset_multivariate[self.starting_date:]
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
        self.train_X, self.train_y, self.test_X, self.test_y = \
            self.model.test_train_splitter(scaled_dataset=self.scaled,
                                           split_point = self.split_point,
                                           flip_data =False)
        #faccio un salvataggio utile
        self.model.input_saver(self.full_scaled) 
        #creo il modello nella sua struttura vuota
        self.model.model_creation(train_X = self.train_X,
                                  n_node = self.n_node,
                                  n_layer = self.n_layer,
                                  act_function = self.act_function) 
        #vado a inizializzare il training
        self.forecasting_model = self.model.Train(loss = self.loss_function,
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
                                                  bagging_cycle = self.bagging_cycle
                                                  )
        #vado a rigenerare riscalando gli output i risultati
        self.real_concat, self.model_concat = self.model.first_prediction(
            self.train_X, self.test_X, self.train_y, self.test_y)




# =============================================================================
"""Classe per fare il forecast operativo""" #, string_flow, string_rain, string_temp
# =============================================================================
class operative_flow_forecast():
    # "C:\Python_directory\Rainfall_runoff_forecasting\MODEL AND NEW DATA\Seganli_clean\Dati_Daniele\to_forecast\filled_streamflow\mean"
    def __init__(self, date_as_number,
                 start_date, end_date,
                 prediction_model, path_data, 
                 quantiles_flow=None, 
                 quantiles_rain=None,
                 quantiles_temp=None):
        if quantiles_flow != None:
            self.string_flow = path_data + 'streamflow/' +\
                quantiles_flow + '/' + str(date_as_number)+'.csv'
        else:
            self.string_flow = path_data + 'streamflow/' +\
                str(date_as_number)+'.csv'
        if quantiles_rain != None:
            self.string_rain = path_data + 'precipitation/' +\
                quantiles_rain + '/' + str(date_as_number)+'.csv'
        else:
            self.string_rain = path_data + 'precipitation/' +\
                str(date_as_number)+'.csv'
        if quantiles_temp != None:
            self.string_temp= path_data + 'temperature/' +\
                quantiles_temp + '/' + str(date_as_number)+'.csv'
        else:
            self.string_temp= path_data + 'temperature/' +\
                str(date_as_number)+'.csv'
        
        self.start_date = start_date
        self.end_date = end_date
        self.prediction_model = prediction_model
        self.path_data = path_data
        
        # self.mng = self.orig_model.mng
        # lancio il metodo
        # self.import_meteo_forecast()
        # self.flow_forecast()
        
        
    def import_meteo_forecast(self, weekend_exclusion, year_exclusion,
                              year_to_exclude, mad_filter_value, 
                              temporal_aggregation, standardize_data,
                              scaler_choice, univariate_scaler,
                              multivariate_scaler):
        
        self.Manager = management_instance(string = self.string_flow, 
                                      string_rain = self.string_rain,
                                      string_temp = self.string_temp,
                                      weekend_exclusion    = weekend_exclusion, 
                                      year_exclusion       = year_exclusion,
                                      year_to_exclude      = year_to_exclude, 
                                      mad_filter_value     = mad_filter_value, 
                                      temporal_aggregation = temporal_aggregation,
                                      standardize_data     = standardize_data, 
                                      scaler_choice        = scaler_choice,
                                      start_date           = self.start_date,
                                      end_date             = self.end_date)
        # inserisco in self
        self.univariate_scaler   = univariate_scaler
        self.multivariate_scaler = multivariate_scaler
        # override degli scaler
        self.Manager.univariate_scaler   = self.univariate_scaler
        self.Manager.multivariate_scaler = self.multivariate_scaler
        
        
    def flow_forecast(self, model_type, n_output, lag_list, temp_var,
                      temp_lags, rain_var, rain_lags, rain_forecast,
                      rain_for_horizon, temp_forecast, temp_for_horizon,
                      day_cumsum, day_cumsum_horiz, dummy_vars, ens_id=None):  
        # print(ens_id)
        self.model = Model_generator.Model_generator(self.Manager.dataset_univariate,
                                     model_type = model_type,
                                     data_manager = self.Manager.d_m,
                                     univariate_scaler = self.Manager.univariate_scaler,
                                     multivariate_scaler = self.Manager.multivariate_scaler,
                                     n_output = n_output,
                                     manager = self.Manager)
        # HO UN DUBBIO SU COME SCALO TEMP E RAIN!
        #compongo il dataset con i lag e la struttura per output
        self.dataset_multivariate = self.model.lag_selector(
            other_var        = True,
            lista_lag        = lag_list,
            n_output         = n_output,
            temperature      = temp_var,
            temp_lags        = temp_lags,
            rainfall         = rain_var,
            rain_lags        = rain_lags,
            rain_forecast    = rain_forecast,
            rain_for_horizon = rain_for_horizon,
            temp_forecast    = temp_forecast,
            temp_for_horizon = temp_for_horizon,
            day_cumsum_rain  = day_cumsum,
            day_cumsum_horiz_rain = day_cumsum_horiz,
            ens_id = ens_id)
        
        #SCALERRRRRRRRRRRRRRRR
        
        # aggiungo le dummy variables
        self.dataset_multivariate  = self.model.dummy_variable(dummy_vars)
        # override dello shuffle
        self.model.shuffle_dataset = self.model.dataset.copy()
        self.shuffle_dataset       = self.model.dataset.copy()
        self.model.cross_valid     = False
        self.model.bagging         = False
        #riscalo il nuovo dataset multivariato
        self.scaled = self.multivariate_scaler.transform(
            self.shuffle_dataset.values)
        #vado a suddividere il dataset in train e test
        self.train_X, self.train_y, self.test_X, self.test_y = \
            self.model.test_train_splitter(scaled_dataset=self.scaled,
                                           split_point = 0)
        #vado a rigenerare riscalando gli output i risultati
        self.testPredict = self.model.prediction(self.test_X, 
                                           self.prediction_model)