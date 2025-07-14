# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 10:06:21 2019

@author: ariele
"""

import numpy as np
import pandas as pd
import random
import datetime
import os
from Deep_learning_module import Deep_learning
from SVR_module import SVR_generator
from SVR_module import SVR_gridsearch
import joblib
import Instances
from keras import backend as K


class Model_generator():
    
    """inizializzazione della classe. la classe data_manager contiene tutte
    le operazioni sul dato eseguite, e quindi tutti gli attributi self. Gli
    scaler sono utili per operazioni sui dati e per la parte di prediction.
    Quello univariate funziona su shape(n, 1), quello multivariate (n, nvar)"""
    def __init__(
            self, dataset, model_type, data_manager, univariate_scaler,
            multivariate_scaler, n_output, manager, grid_search=False, model_params=None,
            save_path = './'):

        self.model_type = model_type
        if self.model_type != 'imputation':
            self.dataset = dataset.fillna(method='ffill')
            self.dataset_univariate = dataset.fillna(method='ffill')
        else:
            self.dataset = dataset.copy()
            self.dataset_univariate = dataset.copy()
        self.d_m = data_manager
        self.univariate_scaler = univariate_scaler
        self.multivariate_scaler = multivariate_scaler
        self.n = dataset.index.size
        self.history_list = list()
        self.n_output = n_output 
        self.manager = manager
        self.grid_search = grid_search
        self.model_params = model_params,
        if model_params != None:
            self.model_params = self.model_params[0]           
        self.save_path = save_path    
    
    """Funzione per dataset multivariato. lista lag ordinata! Nei cicli bisogna 
    ricordare che se segno il lag 168, io voglio tenere quest'ultimo. quindi,
    eliminero i valori fino a 168-1. Le prime istanze if-else servono per fare
    in modo che il metodo venga riutilizzato senza necessità di fornire la 
    lista lag di nuovo oppure il dataset univarato. Analogamente si può fornire
    un diverso dataset con il warning che dopo il riutilizzo vine modificato il
    self.dataset.
    Nel metodo è stato aggiunto anche la possibilità di mettere  i time step
    successivi per fare il forecast many to many. Il loro numero è
    rappresentato dalla variabile n_output. Chiaramente, perchè la cosa
    abbia senso, anche i lag vanno messi con criterio (no sovrapposti)"""
    def lag_selector(self, other_var=None, lista_lag=None, n_output=None, 
                     dataset=None, temperature=None, rain_lags= None,
                     rain_for_horizon = None, rain_forecast=None,
                     temp_lags=None, rainfall=None, temp_forecast=None,
                     temp_for_horizon=None, day_cumsum_rain=False, 
                     day_cumsum_horiz_rain=None):
        if isinstance(dataset, type(None)) == True:
            self.dataset = self.dataset_univariate.copy()
        else:
            self.dataset = dataset
        if lista_lag==None:
            lista_lag=self.lista_lag
        else:
            self.lista_lag = lista_lag
        if n_output==None:
            n_output=self.n_output
        else:
            self.n_output = n_output
        if other_var==None:
            other_var=self.other_var
            temperature = self.temperature
            rainfall = self.rainfall
            rain_forecast = self.rain_forecast
            temp_forecast = self.temp_forecast
            day_cumsum_rain = self.day_cumsum_rain
        else:
            self.day_cumsum_rain = day_cumsum_rain
            self.temp_forecast = temp_forecast
            self.other_var = other_var
            self.rainfall = rainfall
            self.temperature = temperature
            self.rain_forecast = rain_forecast
        dataset = self.dataset.copy()
        n_lags = len(lista_lag)
        # aggiungo i lag di streamflow
        for i in range(n_lags):
            if i == 0:
                lag = lista_lag[i]
                df_lag = dataset.copy()
                for j in range(lag):
                    self.dataset = self.dataset.drop(self.dataset.index[[0]])
                    df_lag = df_lag.drop(df_lag.index[[self.n-j-1]])        
                name = 'lag'+str(lag)
                self.dataset[name] = df_lag.values
            else:
                lag = lista_lag[i]
                lag0 = lista_lag[0]
                df_lag = dataset.copy()
                for j in range(lag0-lag):
                    df_lag = df_lag.drop(df_lag.index[[0]])
                for j in range(lag):
                    a = df_lag.index.size
                    df_lag = df_lag.drop(df_lag.index[[a-1]])                   
                name = 'lag'+str(lag)
                self.dataset[name] = df_lag.values    
        # aggiungo gli 'output'
        df_output = self.dataset.iloc[:,0].copy()
        for i in range(self.n_output-1):
            df_lag = df_output.copy()
            df_lag = df_lag.shift(-i-1)
            self.dataset.insert(0,'t+'+str(i+1),df_lag.values)
            
        # =============================================================================
        #         # #QUI SCALO IL DATO CON SCALER DIVERSI
        #         # _, self.data_scaler = self.d_m.Scaling(self.dataset,
        #         #                                        self.manager.scaler_choice)
        #         # self.dataset[self.dataset.columns] = self.data_scaler.transform(
        #         #     self.dataset[self.dataset.columns])
        #         # aggiungo qui le altre variabili con 
        # =============================================================================
        
        if self.other_var==True:
            self.add_rainfall(rainfall = self.rainfall, lags= rain_lags,
                              day_cumsum = self.day_cumsum_rain, 
                              day_cumsum_horiz = day_cumsum_horiz_rain)
            self.add_rain_forecast(rainfall = self.rain_forecast,
                                   rain_for_horizon = rain_for_horizon)
            self.add_temperature(temperature = self.temperature, lags=temp_lags) 
            self.add_temp_forecast(temperature = self.temp_forecast,
                                   temp_for_horizon = temp_for_horizon)               
        #se non sto imputando elimino i nan
        if self.model_type != 'imputation':
            self.dataset = self.dataset.dropna()
        self.n_var = self.dataset.columns.size
        return self.dataset
    

    """Funzione per dataset multivariato. deve dare le dummy variables e.g. 
    la variabile ora oppure giorno. vanno messe in una lista di stringhe.
    Analogamente al lag selectore le istanze if-else permettono di riusare
    la function senza dover dare la lista di dummy vars di nuovo"""
    def dummy_variable(self, dummy_vars=None, dataset=None):
        if isinstance(dataset, type(None)) == True:
            pass
        else:
            self.dataset = dataset
        if dummy_vars==None:
            dummy_vars=self.dummy_vars
        else:
            self.dummy_vars=dummy_vars
        if ('hour' in dummy_vars):
            self.dataset['hour'] = self.dataset.index.hour
        if ('day' in dummy_vars):
            self.dataset['day'] = self.dataset.index.weekday       
        if ('day type' in dummy_vars):
            self.dataset['day type'] = ((pd.DatetimeIndex(
                    self.dataset.index).dayofweek) // 5 == 1).astype(float)
        if ('month' in dummy_vars):
            self.dataset['month'] = self.dataset.index.month   
        return self.dataset    
    
    """Aggiungere variabili tipo la t media o la sooma come rolling:
        - df = dataframe da cui partire
        - method = mean? sum?
        - horizon = 24->day oppure altre ore"""
    def extra_var(self, df, method, horizon):
        df = pd.DataFrame(df)
        if method=='sum':
            df_1dsum = df.rolling(horizon, min_periods=1).sum()
        elif method=='mean':
            df_1dsum = df.rolling(horizon, min_periods=1).mean()
        df_1dsum = pd.DataFrame(df_1dsum)
        df_1dsum.index = df.index
        return df_1dsum
        
    """Funzione per dataset multivariato. variabili pioggia"""    
    def add_rainfall(self, rainfall, lags, day_cumsum, day_cumsum_horiz):
        if rainfall==True:
            print('\nimporting rainfall historical dataset')
            Manager_rain = Instances.management_instance(
                string = self.manager.string_rain, 
                string_rain = None,
                string_temp=None,
                weekend_exclusion=self.manager.w_ex, 
                year_exclusion = self.manager.year_exclusion,
                year_to_exclude = self.manager.year_to_exclude, 
                mad_filter_value = self.manager.mad, 
                temporal_aggregation = self.manager.temp_aggr,
                standardize_data=self.manager.std_data, 
                scaler_choice =  self.manager.scaler_choice,
                var_name = 'h average rain',
                start_date = self.manager.start_date,
                end_date = self.manager.end_date)
            # creo un modello fittizzio solo per usare i metodi di questa classe
            self.model_rain = Model_generator(
                Manager_rain.dataset_univariate,
                model_type=None,
                data_manager = Manager_rain.d_m,
                univariate_scaler = Manager_rain.univariate_scaler,
                multivariate_scaler = Manager_rain.multivariate_scaler,
                n_output = self.n_output,
                manager = Manager_rain)
            # creo così il dataframe che m serve con le piogge
            self.df_multi_rain = self.model_rain.lag_selector(other_var=False,
                                                              lista_lag = lags,
                                                              n_output=1)
            # aggiungo ulteriori variabili se richiesto (cumulate e medie)
            if day_cumsum==True:
                for i in range(day_cumsum_horiz):
                    df_1dsum = self.extra_var(df = self.df_multi_rain['h average rain'],
                                              method='sum', horizon=24*(i+1))
                    self.df_multi_rain['day_rain_sum'+str(i+1)] = df_1dsum.values
 
            # faccio collimare i due dataset in uno solo creando l'unione degli index
            new_index = self.df_multi_rain.index.union(self.dataset.index)
            rain_new_df = pd.DataFrame(index = new_index,
                                       columns = self.df_multi_rain.columns,
                                       data = self.df_multi_rain)
            self.dataset = pd.merge(self.dataset, rain_new_df,
                                    how='inner', left_index=True, right_index=True)
            
    """Funzione per dataset multivariato. variabile temepratura se presente"""    
    def add_temperature(self, temperature, lags):
        if temperature==True:
            print('\nimporting temperature historical dataset')
            Manager_temp = Instances.management_instance(
                string = self.manager.string_temp, 
                string_rain = None,
                string_temp=None,
                weekend_exclusion=self.manager.w_ex, 
                year_exclusion = self.manager.year_exclusion,
                year_to_exclude = self.manager.year_to_exclude, 
                mad_filter_value = self.manager.mad, 
                temporal_aggregation = self.manager.temp_aggr,
                standardize_data=self.manager.std_data, 
                scaler_choice =  self.manager.scaler_choice,
                var_name = 'h average temp',
                start_date = self.manager.start_date,
                end_date = self.manager.end_date)
            # creo un odello fittizzio solo per usare i metodi di questa classe
            self.model_temp = Model_generator(
                Manager_temp.dataset_univariate,
                model_type=None,
                data_manager = Manager_temp.d_m,
                univariate_scaler = Manager_temp.univariate_scaler,
                multivariate_scaler = Manager_temp.multivariate_scaler,
                n_output = self.n_output,
                manager = Manager_temp)
            # creo così il dataframe che m serve con le piogge
            self.df_multi_temp = self.model_temp.lag_selector(other_var=False,
                                                              lista_lag = lags,
                                                              n_output=1)
            # faccio collimare i due dataset in uno solo creando l'unione degli index
            new_index = self.df_multi_temp.index.union(self.dataset.index)
            rain_new_df = pd.DataFrame(index = new_index,
                                       columns = self.df_multi_temp.columns,
                                       data = self.df_multi_temp)
            self.dataset = pd.merge(self.dataset, rain_new_df,
                                    how='inner', left_index=True, right_index=True)
            
    """Funzione per dataset multivariato. variabili pioggia previsionali"""    
    def add_rain_forecast(self, rainfall, rain_for_horizon):
        if rainfall==True:
            print('\nimporting rainfall forecast dataset')
            Manager_rain = Instances.management_instance(
                string = self.manager.string_rain, 
                string_rain = None,
                string_temp=None,
                weekend_exclusion=self.manager.w_ex, 
                year_exclusion = self.manager.year_exclusion,
                year_to_exclude = self.manager.year_to_exclude, 
                mad_filter_value = self.manager.mad, 
                temporal_aggregation = self.manager.temp_aggr,
                standardize_data=self.manager.std_data, 
                scaler_choice =  self.manager.scaler_choice,
                var_name = 'h average rain_for',
                start_date = self.manager.start_date,
                end_date = self.manager.end_date)
            # creo un modello fittizzio solo per usare i metodi di questa classe
            self.model_rain_forec = Model_generator(
                Manager_rain.dataset_univariate,
                model_type=None,
                data_manager = Manager_rain.d_m,
                univariate_scaler = Manager_rain.univariate_scaler,
                multivariate_scaler = Manager_rain.multivariate_scaler,
                n_output = self.n_output,
                manager = Manager_rain)
            # creo così il dataframe che m serve con le piogge
            self.df_multi_rain_for = self.model_rain_forec.lag_selector(other_var=False,
                                                                    lista_lag = [],
                                                                    n_output = rain_for_horizon)
            # faccio collimare i due dataset in uno solo creando l'unione degli index
            new_index = self.df_multi_rain_for.index.union(self.dataset.index)
            rain_new_df = pd.DataFrame(index = new_index,
                                       columns = self.df_multi_rain_for.columns,
                                       data = self.df_multi_rain_for)
            self.dataset = pd.merge(self.dataset, rain_new_df,
                                    how='inner', left_index=True, right_index=True) 
            
    """Funzione per dataset multivariato. variabili pioggia previsionali"""    
    def add_temp_forecast(self, temperature, temp_for_horizon):
        if temperature==True:
            print('\nimporting temperature forecast dataset')
            Manager_temp = Instances.management_instance(
                string = self.manager.string_rain, 
                string_rain = None,
                string_temp=None,
                weekend_exclusion=self.manager.w_ex, 
                year_exclusion = self.manager.year_exclusion,
                year_to_exclude = self.manager.year_to_exclude, 
                mad_filter_value = self.manager.mad, 
                temporal_aggregation = self.manager.temp_aggr,
                standardize_data=self.manager.std_data, 
                scaler_choice =  self.manager.scaler_choice,
                var_name = 'h average rain_for',
                start_date = self.manager.start_date,
                end_date = self.manager.end_date)
            # creo un modello fittizzio solo per usare i metodi di questa classe
            self.model_temp_forec = Model_generator(
                Manager_temp.dataset_univariate,
                model_type=None,
                data_manager = Manager_temp.d_m,
                univariate_scaler = Manager_temp.univariate_scaler,
                multivariate_scaler = Manager_temp.multivariate_scaler,
                n_output = self.n_output,
                manager = Manager_temp)
            # creo così il dataframe che m serve con le piogge
            self.df_multi_temp_for = self.model_temp_forec.lag_selector(other_var=False,
                                                                    lista_lag = [],
                                                                    n_output = temp_for_horizon)
            # faccio collimare i due dataset in uno solo creando l'unione degli index
            new_index = self.df_multi_temp_for.index.union(self.dataset.index)
            temp_new_df = pd.DataFrame(index = new_index,
                                       columns = self.df_multi_temp_for.columns,
                                       data = self.df_multi_temp_for)
            self.dataset = pd.merge(self.dataset, temp_new_df,
                                    how='inner', left_index=True, right_index=True) 
    
    """Funzione per fare la cross validation splittando il dataset in anni. 
    Siccome vorrei non fare errori, farei il ciclo nel main. L'input 
    cross_valid se True fa lo shuffle dei dati, se False no e li lascia cosi.
    self.last_year nel caso di cross valid è il vero test"""
    def dataset_shuffle(self, cross_valid, bagging):
        self.cross_valid = cross_valid
        self.bagging = bagging
        if cross_valid==True or self.bagging==True:
            dataset_year = list()
            for i in range(self.dataset.index.year.unique().size):
                dataset_year.append(self.dataset[self.dataset.index.year == 
                                                 self.dataset.index.year.unique()[i]])
            self.last_year =  dataset_year[-1]
            del [dataset_year[-1]]
            # random.shuffle(dataset_year)
            self.shuffle_dataset = pd.concat(dataset_year, ignore_index=False)
        else:
            self.shuffle_dataset = self.dataset
            
        return self.shuffle_dataset     
    
    
    """Funzione che prende in input il punto di split e mi ritorna i set di 
    Train e Testing. Va specificato il tipo di modello, perchè a seconda
    le shape degli input e output cambiano"""
    def test_train_splitter(self, scaled_dataset, split_point=None,
                            flip_data=False):
        if split_point == None:
            pass
        else:
            self.split_point = split_point
        # tronco le sequenze se sto chiedendo di predire sequenze
        seq_to_seq_dataset = scaled_dataset[range(0, scaled_dataset.shape[0], self.n_output), :]
        # n_train_hours = int(round(seq_to_seq_dataset[:,0].size*self.split_point)) 
        n_train_hours = int(round(self.shuffle_dataset.index.size/self.n_output*self.split_point)) 
        # divido in train e testing
        train = seq_to_seq_dataset[:n_train_hours, :]
        test = seq_to_seq_dataset[n_train_hours:, :]
        # =========================================================================
        #   Verrà utilizzata questa nomenclatura per la suddivisione del dataset:
        #   - Train_X e Test_X sono le parti del dataset 'precedenti, ovvero gli 
        #   input effettivi del modello
        #   - Train_y e test_y sono invece quelli successivi, gli output
        # =========================================================================
        if self.model_type == 'Lstm' or self.model_type == 'ERNN' \
        or self.model_type == 'GRU' or self.model_type =='bidirectional_Lstm' \
        or self.model_type == 'Mixture1' or self.model_type == 'Mixture3':
            
            # train_X, train_y = train[:, 1:], train[:, 0]
            # test_X, test_y = test[:, 1:], test[:, 0]
            train_X, train_y = train[:, self.n_output:], train[:, 0:self.n_output]            
            test_X, test_y = test[:, self.n_output:], test[:, 0:self.n_output]
            # reshape input to be 3D [samples, timesteps, features]
            train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
            test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1])) 
            train_y = train_y[:,::-1]
            test_y = test_y[:,::-1]
            
        elif self.model_type == 'Mixture2' or self.model_type == 'Mixture4' :
            train_X, train_y = train[:, self.n_output:], train[:, 0:self.n_output]            
            test_X, test_y = test[:, self.n_output:], test[:, 0:self.n_output]
            #reshape input to be 3D [samples, timesteps, features]. Il terzo 
            # numero è quanti input do ad ogni timestep, ovvero in e out
            train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
            test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
            train_y = train_y.reshape((train_y.shape[0], 1, train_y.shape[1]))
            train_y = train_y[:,:,::-1]
            test_y = test_y.reshape((test_y.shape[0], 1, test_y.shape[1]))
            test_y = test_y[:,:,::-1]
        
        elif self.model_type == 'Feed_forward' or self.model_type == 'Mixture2' \
        or self.model_type == 'Mixture4' :
            train_X, train_y = train[:, self.n_output:], train[:, 0:self.n_output]            
            test_X, test_y = test[:, self.n_output:], test[:, 0:self.n_output]
            #reshape input to be 3D [samples, timesteps, features]. Il terzo 
            # numero è quanti input do ad ogni timestep, ovvero in e out
            train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
            test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
            train_y = train_y.reshape((train_y.shape[0], 1, train_y.shape[1]))
            train_y = train_y[:,:,::-1]
            test_y = test_y.reshape((test_y.shape[0], 1, test_y.shape[1]))
            test_y = test_y[:,:,::-1]
                        
        elif self.model_type == 'SVR' or self.model_type == 'LinearRegression' \
         or self.model_type == 'KNeighborsRegressor' \
             or self.model_type == 'DecisionTreeRegressor' \
                 or self.model_type == 'MultiOutputSVR' \
                     or self.model_type == 'imputation' \
                         or self.model_type == 'SARIMAX':
            train_X, train_y = train[:, self.n_output:], train[:, 0:self.n_output]            
            test_X, test_y = test[:, self.n_output:], test[:, 0:self.n_output]
            train_X = train_X.reshape((train_X.shape[0], train_X.shape[1]))
            test_X = test_X.reshape((test_X.shape[0], test_X.shape[1]))
            train_y = train_y.reshape((train_y.shape[0], self.n_output))
            test_y = test_y.reshape((test_y.shape[0], self.n_output))
        
        if flip_data ==True:
            train_X = np.fliplr(train_X)
            train_y = np.fliplr(train_y)
            test_X = np.fliplr(test_X)
            test_y = np.fliplr(test_y)
        return train_X, train_y, test_X, test_y
    
    
    """Metodo che mi permette di salvare i diversi input dei modelli. 
    Questa operazione è neccasria per la comparison successiva"""
    def input_saver(self, scaled_dataset):
        train = scaled_dataset[:, :]
        train = train[range(0, train.shape[0], self.n_output), :]
        self.input1 = list()  #RNN
        self.input2 = list()  #Feed_forward
        self.input3 = list()  #SVR
        #tipo input 1
        train_X, train_y = train[:, self.n_output:], train[:, 0:self.n_output]  
        train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1])) 
        self.input1.append([train_X, train_y])    
        #tipo input 2
        train_X, train_y = train[:, self.n_output:], train[:, 0:self.n_output] 
        train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
        train_y = train_y.reshape((train_y.shape[0], 1, train_y.shape[1]))
        self.input2.append([train_X, train_y])   
        #tipo input 3
        train_X, train_y = train[:, self.n_output:], train[:, 0:self.n_output]     
        train_X = train_X.reshape((train_X.shape[0], train_X.shape[1]))
        train_y = train_y.reshape((train_y.shape[0], self.n_output))
        self.input3.append([train_X, train_y])   
        
    
    """Funzione per generare il modello deep neural network. La selezione 
    avviene a seconda della stringa data nella function di train-test"""  
    def model_creation(self, train_X=None, n_node=None, n_layer=None, 
                       act_function=None, scorer=None, optimizer=None, loss_function=None):
        self.n_node = n_node
        self.n_layer = n_layer
        self.act_function = act_function

        if self.model_type == 'SVR':
            if self.model_params != None:
                self.model_generator = SVR_generator(scorer=scorer)
                self.model = self.model_generator.SVR_model(
                    self.model_type, self.n_output,
                    kernel=self.model_params["estimator__kernel"],
                    eps=self.model_params["estimator__epsilon"],
                    C=self.model_params["estimator__C"],
                    grid_search=self.grid_search)
            else:
                self.model_generator = SVR_generator(scorer=scorer)
                self.model = self.model_generator.SVR_model(
                    self.model_type, self.n_output)

        elif self.model_type == 'MultiOutputSVR':
            if self.model_params != None:
                self.model_generator = SVR_generator(scorer=scorer)
                self.model = self.model_generator.MultiOutputSVR_model(
                    self.model_type,
                    kernel=self.model_params["estimator__kernel"],
                    eps=self.model_params["estimator__epsilon"],
                    C=self.model_params["estimator__C"],
                    grid_search=self.grid_search)
            else:
                self.model_generator = SVR_generator(scorer=scorer)
                self.model = self.model_generator.MultiOutputSVR_model(
                    self.model_type)
                    
        elif self.model_type == 'LinearRegression':
            self.model_generator = SVR_generator(scorer=scorer)
            self.model = self.model_generator.LinearRegression_model(self.model_type)
        elif self.model_type == 'KNeighborsRegressor':
            self.model_generator = SVR_generator(scorer=scorer)
            self.model = self.model_generator.KNeighborsRegressor_model(self.model_type)
        elif self.model_type == 'DecisionTreeRegressor':
            self.model_generator = SVR_generator(scorer=scorer)
            self.model = self.model_generator.DecisionTreeRegressor_model(self.model_type)
        # elif self.model_type == 'SARIMAX':
        #     self.model = Arima_generator().sarimax_gen(train_X)
        else:
            self.model = Deep_learning(
                optimizer=optimizer,
                loss=loss_function
            ).FeedForward(
                train_X      = train_X, 
                n_output     = self.n_output, 
                n_node       = self.n_node,
                act_function = self.act_function)
    
    """Function to create the grid search, and to run it"""
    def model_grid_search(self, 
        train_X, train_y, test_X, test_y, model='MultiOutputSVR', loss='r2', scorer='rmse', optimizer='adam',
        param_grid={'kernel':['rbf'],'epsilon':[0.001],'C':[1.0]},
        epochs=None):
        try:
            if model == 'SVR':
                self.model_generator = SVR_generator(scorer=scorer)
                self.grid_search_results = self.model_generator.SVR_model(train_X, train_y, param_grid)
            elif model == 'MultiOutputSVR':
                self.model_generator = SVR_generator(scorer=scorer)
                self.grid_search_results = self.model_generator.MultiOutputSVR_gs(train_X, train_y, param_grid)
            elif model == 'Feed_forward':
                self.model_generator = Deep_learning(optimizer=optimizer, loss=loss, scorer=scorer, epochs=epochs)
                self.grid_search_results = self.model_generator.FeedForward_gs(
                    train_X=train_X, train_y=train_y, param_grid=param_grid)
            # elif self.model_type == 'LinearRegression':
            #     self.grid_search = SVR_gridsearch().SVR_model(self.model, param_grid)
            # elif self.model_type == 'KNeighborsRegressor':
            #     self.grid_search = SVR_gridsearch().SVR_model(self.model, param_grid)
            # elif self.model_type == 'DecisionTreeRegressor':
            #     self.grid_search = SVR_gridsearch().SVR_model(self.model, param_grid)
        except Exception as e:
            print("Must initialize before the model.")
            print(e)
            raise

        return self.grid_search_results

        # ## reshape train_X and train_y
        # train_X_reshaped = np.reshape(train_X, (train_X.shape[0], -1))
        # train_y_reshaped = np.reshape(train_y, (train_y.shape[0], -1))              

    """Funzione per fare il compile e il fit del model in maniera breve"""
    def fitting_compiling(self, loss, optimizer, metrics, soglia, train_X, 
                          train_y, test_X, test_y, epochs, batch):
        if self.model_type == 'SVR' or self.model_type == 'LinearRegression' \
                or self.model_type == 'KNeighborsRegressor' \
                    or self.model_type == 'DecisionTreeRegressor'\
                        or self.model_type == 'MultiOutputSVR':
            self.model.fit(train_X,train_y)
        elif self.model_type =='SARIMAX':
            self.model = self.model.fit(disp=True)
        else:
            self.model.compile(loss = loss, optimizer = optimizer, metrics = [metrics])              
            hist = self.model.fit(train_X, train_y, epochs=epochs, 
                                  batch_size=batch,
                                  validation_data=(test_X, test_y),
                                  verbose=2, shuffle=False)
            if hist.history['val_' +metrics][-1] > soglia and \
                hist.history[metrics][-1]> soglia:    
                print('SOMETHING WENT WRONG!')
                simulation_is_fine=0
                session = K.get_session()
                for layer in self.model.layers: 
                     for v in layer.__dict__:
                         v_arg = getattr(layer,v)
                         if hasattr(v_arg,'initializer'):
                             initializer_method = getattr(v_arg, 'initializer')
                             initializer_method.run(session=session)
                             print(f'reinitializing layer {layer.name}.{v}')
            else:
                self.history_list.append(hist)
                self.var=1     #esco dal while           
        # se sto facendo bagging devo appendere il modello e crearne un'altro
        if self.bagging==True:
            self.bootsrap_ensamble.append(self.model)
            self.model_creation(train_X,  self.n_node, self.n_layer,
                                self.act_function)
            
        
        
    """Funzione per inizializzare il training del modello. se sono specificati
    i cicli della cross validation l procedura consiste in una serie di 
    funzioni: fit -> loop -> shuffle -> scale -> test-train -> fit -> again"""
    def Train(self, loss, optimizer, metrics, soglia, train_X, train_y, test_X, 
              test_y, epochs, batch, cross_cycle=None, bagging_cycle=None):
        # per salvare un output alla fine le inizializzo come self
        self.batch = batch
        self.epochs = epochs
        self.metrics = metrics
        self.soglia = soglia
        self.loss = loss
        self.optimizer = optimizer
        self.cross_cycle = cross_cycle
        self.bagging_cycle = bagging_cycle
        if self.cross_valid==False and self.bagging==False:
            print('\n\nClassic Train operation: \n')
            self.fitting_compiling(loss, optimizer, metrics, soglia, train_X,
                                   train_y, test_X, test_y, epochs, batch)
            return self.model
            
        elif self.cross_valid==True and self.bagging==False:
            self.fitting_compiling(loss, optimizer, metrics, soglia, train_X,
                                   train_y, test_X, test_y, epochs, batch)
            for i in range(cross_cycle-1):
                print('\n\nCross validation iteration:', i+1, '\n')
                self.dataset_shuffle(self.cross_valid, self.bagging)
                scaled = self.multivariate_scaler.fit_transform(self.shuffle_dataset.values)
                train_X, train_y, test_X, test_y = self.test_train_splitter(scaled)
                self.fitting_compiling(loss, optimizer, metrics, soglia, train_X,
                                       train_y, test_X, test_y, epochs, batch)
            return self.model
                
        elif self.cross_valid==False and self.bagging==True:
            self.bootsrap_ensamble = list()
            self.fitting_compiling(loss, optimizer, metrics, soglia, train_X,
                                   train_y, test_X, test_y, epochs, batch)
            for i in range(bagging_cycle-1):
                print('\n\nBootstrap aggregation iteration:', i+1, '\n')
                self.dataset_shuffle(self.cross_valid, self.bagging)
                scaled = self.multivariate_scaler.fit_transform(self.shuffle_dataset.values)
                train_X, train_y, test_X, test_y = self.test_train_splitter(scaled)
                self.fitting_compiling(loss, optimizer, metrics, soglia, train_X,
                                       train_y, test_X, test_y, epochs, batch)
            return self.bootsrap_ensamble
        
        elif self.cross_valid==True and self.bagging==True:
            self.bootsrap_ensamble = list()
            self.fitting_compiling(loss, optimizer, metrics, soglia, train_X,
                                   train_y, test_X, test_y, epochs, batch)
            for i in range(bagging_cycle-1):
                print('\n\nBootstrap aggregation with cross validation iteration:', i+1, '\n')
                for j in range(cross_cycle-1):
                    self.var = 0
                    while self.var == 0:
                        print('\n\ncross validation iteration:', j+1, '\n')
                        self.dataset_shuffle(self.cross_valid, self.bagging)
                        scaled = self.multivariate_scaler.fit_transform(self.shuffle_dataset.values)
                        train_X, train_y, test_X, test_y = self.test_train_splitter(scaled)
                        self.fitting_compiling(loss, optimizer, metrics, soglia, train_X,
                                                train_y, test_X, test_y, epochs, batch)
                    self.bagging =False #così posso fare la cross validation
                self.bagging =True
            return self.bootsrap_ensamble
                
        
    
    """Prediction input-output easy. modifica già la shape dell'output"""
    def prediction(self, input_x, model=None):
        if model==None:
            model=self.model
        if self.model_type=='SARIMAX':
            for i in range(input_x.size):
                output_y = self.model.forecast(self.n_output)
        else:
            output_y = model.predict(input_x)
            # modify shapes of train arrays and invert scale
            output_y = np.fliplr(output_y)
            output_y = output_y.reshape((output_y.shape[0]*(self.n_output), 1))
        # se ho standardizzato e riscalato i dati
        if self.d_m.std == True:
            output_y = self.d_m.std_scaler.inverse_transform(output_y)
        return output_y
    
    
    """Fare la prediction del train e del testing ordinati per vedere le prime
    performances del modello. dopo aver fatto le prediction bisogna riscalare
    i dati con lo scaling singolo e poi modificare tutte le shapes. Nel caso
    di cross validation il dataset viene ricostruito e i vettori di test e
    train sistemati in maniera da avere nel test solo l'ultimo anno lasciato.
    Nel caso di bagging, vanno fatte le prediction con i vari modelli, e 
    successivamente le stesse vanno mediate, per ottenerne una stabile"""    
    def first_prediction(self, train_X, test_X, train_y, test_y, model=None, scaler=None):
        if model==None:
            model=self.model
        if self.cross_valid == True or self.bagging==True:
            # ricostruisco il dataset originale
            scaled_full_dataset =  self.multivariate_scaler.fit_transform(self.dataset)
            train_X, train_y, test_X, test_y = \
                self.test_train_splitter(scaled_full_dataset, split_point=1)
        else:
            pass
        if self.bagging == True:
            train_predict, test_predict = list(), list()
            for i in range(self.bagging_cycle):
                model = self.bootsrap_ensamble[i]
                train_predict.append(self.prediction(train_X, model))
                test_predict.append(self.prediction(test_X, model))
            # faccio la media delle prediction di tutti gli ensamble
            self.trainPredict = np.array([np.mean(k) for k in zip(*train_predict)])
            self.testPredict = np.array([np.mean(k) for k in zip(*test_predict)])
            # modifico la shape perche sia (n_val,1)
            self.trainPredict.shape = (self.trainPredict.shape[0], 1)
            self.testPredict.shape = (self.testPredict.shape[0], 1)
        else:
            # make prediction clasic way
            self.trainPredict = self.prediction(train_X, model)
            self.testPredict = self.prediction(test_X, model)
        # per l'ordine con cui creo il dataset multivariate, le prediction e
        # i vettori y sono inversi rispetto al tempo. devo flippare
        train_y = np.fliplr(train_y)
        test_y = np.fliplr(test_y)
        # modify shapes of train and test original arrays and invert scale
        train_y = train_y.reshape((train_y.shape[0]*(self.n_output), 1))
        test_y = test_y.reshape((test_y.shape[0]*(self.n_output), 1))
        # se ho standardizzato i dati
        if self.d_m.std == True:
            train_y = self.d_m.std_scaler.inverse_transform(train_y)
            test_y = self.d_m.std_scaler.inverse_transform(test_y)
        # dataset iniziale shiftato giusto
        real_concat = np.concatenate((train_y, test_y), axis=None)    
        real_concat.shape = (real_concat.size, 1)
        self.real_concat = self.univariate_scaler.inverse_transform(real_concat)
        model_concat = np.concatenate((self.trainPredict, self.testPredict), axis=None)
        model_concat.shape = (model_concat.size, 1)
        self.model_concat = self.univariate_scaler.inverse_transform(model_concat)
        return self.real_concat, self.model_concat
    
    
    """Funzione per fare le prediction utilizzando altre prediction, in cui
    n_day è il numero di giorni da predire, n_agg indica ogni quante ore
    aggiorno il dataset utilizzando veri valori (e.g. se 6 alla sesta ora i 
    valori di input sono quelli veri) e start_date il giorno di partenza.
    L'otput è un dataframe contenete date prediction e real. Nell'istanza per
    scegliere quando fare l'update si valuta se il rapporto tra la variabile
    del ciclio i e n_agg è un numero intero. Se ciò non accade viene modificato
    il dataset originale con la prediction precedente e viene rieseguito tutto
    il processo di aggiunta variabili e ricalamento fino a fare prediction
    NOTA! Quando faccio la prediction per start date, la sto facendo proprio
    in quell'ora li, perchè il dataset è stato costruito per dare in input i
    valori precedenti, e quindi la mia prediction viene fatta per quel 
    momento preciso. Il mio vettore y è la prima colonna del dataset"""
    def roll_prediction(self, n_day, n_agg, start_date, model=None):
        if model==None:
            model=self.model
        self.df_roll = pd.DataFrame(index=range(n_day*24),
                                    columns=['predicted', 'date', 'real'])
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        dataset = self.dataset.copy()
        dataset_univ = self.dataset_univariate.copy()
        scaled_df = pd.DataFrame(index=self.dataset.index,
                                 columns =self.dataset.columns,
                                 data = self.multivariate_scaler.fit_transform(dataset))
        for i in range(n_day*24):
            if float(i/n_agg).is_integer()==True or i==0:
                Start = scaled_df[scaled_df.index==start_date +
                                     datetime.timedelta(hours=i)]    
                print('updated!', i/n_agg)
            else:
                dataset_univ[dataset_univ.index==start_date +
                             datetime.timedelta(hours=i)] = self.df_roll['predicted'][i-1]
                self.lag_selector(dataset=dataset_univ)
                self.dummy_variable()
                dataset = self.dataset.copy()
                scaled_df = pd.DataFrame(index=self.dataset.index,
                                         columns =self.dataset.columns,
                                         data = self.multivariate_scaler.fit_transform(dataset))
                Start = scaled_df[scaled_df.index==start_date +
                                     datetime.timedelta(hours=i)]            
            _, _, test_X, test_y= self.test_train_splitter(Start.values, split_point=0)
            self.df_roll['predicted'][i] = self.prediction(test_X)
            self.df_roll['date'][i] = start_date + datetime.timedelta(hours=i)
            self.df_roll['real'][i] = self.dataset_univariate[self.dataset_univariate.index
                        == start_date + datetime.timedelta(hours=i)].values
        self.df_roll.index = pd.to_datetime(self.df_roll['date'],
                                            format="%Y-%m-%d %H:%M:%S")
        del self.df_roll['date']
        return self.df_roll
                
    
    """funzione per salvare il modello in una path che si autogenera per poi
    fare futuri confronti.
    NOTA: VIENE CHIAMATO IN POST PROCESS"""        
    def model_saver(self, do_you_want_to_save, error_string = None):
        self.do_you_want_to_save = do_you_want_to_save
        if do_you_want_to_save == True:
            # creo i contenuti del logfile
            log_string = \
            'model generated in ' + self.save_path + '\n\n' + \
            'architettura del modello usata:  ' + self.model_type + '\n' +\
            'batch size used:                 ' + str(self.batch) + '\n' + \
            'numero di epoche:                ' + str(self.epochs) + '\n' + \
            'metrica usata:                   ' + str(self.metrics) + '\n' + \
            'loss function:                   ' + str(self.loss) + '\n' + \
            'ottimizzatore:                   ' + str(self.optimizer) + '\n' + \
            'coss validation cicli:           ' + str(self.cross_cycle) + '\n' + \
            'bootstrap aggregation cicli:     ' + str(self.bagging_cycle) + '\n'
            if error_string !=None:
                log_string = log_string + '\n' + error_string
                
            # creo la cartella output se non esiste
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            # salvo il logfile che ho generato come stringa
            with open(self.save_path + '/' + 'logfile.txt', 'w') as tfile:
                tfile.write(log_string)
            #salvo il modello
            if self.bagging == True:
                i=1
                for model in self.bootsrap_ensamble:
                    os.makedirs(self.save_path + '/' + str(i))
                    if self.model_type == 'SVR' or self.model_type == 'LinearRegression' \
                        or self.model_type == 'KNeighborsRegressor' \
                            or self.model_type == 'DecisionTreeRegressor' \
                                or self.model_type == 'MultiOutputSVR':
                        joblib.dump(model, self.save_path + '/' + self.model_type + '_model.joblib')
                    else:
                        model.save(self.save_path + '/' + str(i) + '/' + self.model_type + '_model.h5')
                    i = i+1
            else:
                if self.model_type == 'SVR' or self.model_type == 'LinearRegression' \
                    or self.model_type == 'KNeighborsRegressor' \
                        or self.model_type == 'DecisionTreeRegressor' \
                            or self.model_type == 'MultiOutputSVR':
                    joblib.dump(self.model, self.save_path + '/' + self.model_type + '_model.joblib')
                else:
                    self.model.save(self.save_path + '/' + self.model_type + '_model.h5')
        else:
            pass