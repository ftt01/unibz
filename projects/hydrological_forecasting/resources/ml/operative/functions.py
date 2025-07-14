# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 10:07:14 2019

@author: ariele
"""

import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import datetime
import seaborn


class post_processing():
    
    def __init__(self, model, manager):
        self.model = model
        self.d_m = manager
        #self.n_data = model.dataset.index.size
        self.n_data = model.real_concat.size
        
        
    """rigenero tre dataframe con index, conteneti il dataframe con le misure 
    reali, il dataframe del modello con la parte train e il dataframe con il 
    modello parte test. La parte di indici è già stata fatta quando ho creato
    il dataset. Infatti la prima colonna del dataset multivariato corrisponde
    al vettore_y (e.g. train_y e test_y) che servono per validare il modello.
    In altre parole è già tutto shiftato di 1hr e quindi non serve rifarlo
    bias_correction contiene le correzioni da applicare al modello"""
    def Dataframe_gen(self, bias_correction=None):
        self.df_real = pd.DataFrame(index=range(self.n_data), 
                                    columns=['h average'])
        self.df_forcasted = pd.DataFrame(index=range(self.n_data), 
                                         columns=['h average'])
        self.df_forcasted_uncorrected = pd.DataFrame(index=range(self.n_data), 
                                                     columns=['h average'])
        self.df_train = pd.DataFrame(index=range(self.n_data),
                                     columns=['h average'])
        self.df_test = pd.DataFrame(index=range(self.n_data), 
                                    columns=['h average'])
        if isinstance(bias_correction, type(None)) == True:
            self.df_real['h average'] = self.model.real_concat[:, 0]
            self.df_forcasted['h average'] = self.model.model_concat[:, 0]
            self.df_train['h average'][0:len(self.model.trainPredict)] = \
                self.model.model_concat[0:len(self.model.trainPredict),0]
            self.df_test['h average'][len(self.model.trainPredict):] = \
                self.model.model_concat[len(self.model.trainPredict):,0]
        else:
            self.df_real['h average'] = self.model.real_concat[:, 0]
            self.df_forcasted['h average'] = self.model.model_concat[:, 0] + bias_correction[:, 0]
            self.df_forcasted_uncorrected['h average'] = self.model.model_concat[:, 0]
            self.df_train['h average'][0:len(self.model.trainPredict)] = \
                self.model.model_concat[0:len(self.model.trainPredict),0] + \
                    bias_correction[0:len(self.model.trainPredict),0]
            self.df_test['h average'][len(self.model.trainPredict):] = \
                self.model.model_concat[len(self.model.trainPredict):,0] + \
                    bias_correction[len(self.model.trainPredict):,0] 
                
        self.df_train['h average'] = self.df_train['h average'].astype('float64')
        self.df_test['h average'] = self.df_test['h average'].astype('float64')
        #ricreo l'indice
        index = pd.date_range(start = self.model.dataset.index[0],
                              periods = self.n_data, freq='H')
        self.df_forcasted.index = index
        self.df_forcasted_uncorrected.index = index
        self.df_real.index = index
        self.df_train.index = index 
        self.df_test.index = index
            
        return self.df_real, self.df_test, self.df_train
        
    """Richiamare questa permette di plottare le history del training"""    
    def plot_history(self):
        for i in range(len(self.model.history_list)):
            history = self.model.history_list[i]
            plt.figure(figsize=(14, 4))
            plt.plot(history.history['loss'], label='train')
            plt.plot(history.history['val_loss'], label='test')
            plt.legend()
            plt.show()
            
    """Richiamare questa permette di plottare tutta la prediction della serie
    storica in ballo"""  
    def plot_complete_prediction(self):        
        fig, ax = plt.subplots(figsize=(18, 5))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=18))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.plot(self.df_real)
        ax.plot(self.df_train, alpha=0.4)
        ax.plot(self.df_test, color='green', alpha=0.4)
        
        ax.set_xlabel('hour')
        ax.set_ylabel('Consumption (l/s)')
        ax.set_title('Hourly Forecasting')
        ax.legend(('real consumption','train prediction','test prediction'))
        ax.grid(True)       
        fig.autofmt_xdate()
        plt.savefig('immagini/complete_Sardagna_Feed_forward.png', dpi=300, bbox_inches='tight')
        plt.show() 
        
    """Fuzione per fare i plot di solo una parte della time series"""    
    def plot_partial_prediction(self, start_date, n_days):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = start_date + datetime.timedelta(days = n_days)
        fig, ax = plt.subplots(figsize=(18, 6))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H')) 
        ax.format_xdata = mdates.DateFormatter('%Y-%m')
        ax.plot(self.df_real[start_date:end_date])
        ax.plot(self.df_train[start_date:end_date])
        ax.plot(self.df_test[start_date:end_date])
        ax.set_xlabel('hour')
        ax.set_ylabel('Consumption (l/s)')
        ax.set_title('Hourly Forecasting')
        ax.legend(('real consumption','train prediction','test prediction'))
        ax.grid(True)       
        fig.autofmt_xdate()
        #plt.savefig('partial.png', dpi=600, bbox_inches='tight'))
        plt.show()
        
    """Fuzione per fare i plot della roll-prediction"""
    def plot_rolled_prediction(self, df_roll):
        df = pd.merge(df_roll , self.df_test, left_index=True, right_index=True)
        fig, ax = plt.subplots(figsize=(18, 6))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) 
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.plot(df['real'])
        ax.plot(df['predicted'])
        ax.plot(df['h average'])
        ax.set_xlabel('hour')
        ax.set_ylabel('Consumption (l/s)')
        ax.set_title('Hourly Forecasting')
        ax.legend(('real consumption','roll prediction','test prediction'))
        ax.grid(True)       
        fig.autofmt_xdate()
        plt.show() 
        print('\n errors for roll prediction:\n')
        self.errors(df['real'],df['predicted'])
        print('\n errors for standard prediction:\n')
        self.errors(df['real'],df['h average'])
        return df
    
    """Fuzione per fare i plot di multiple roll-prediction. Nota bene che in 
    questa function df_roll deve essere una lista di df"""
    def plot_multiple_rolled_prediction(self, df_roll, figsize, save=None):
        df = pd.merge(self.df_test, df_roll[0][0], left_index=True, right_index=True)
        for i in range (len(df_roll[0])-1):
            df = pd.merge(df , df_roll[0][i+1]['predicted'], left_index=True,
                          right_index=True)
        fig, ax = plt.subplots(figsize=figsize)
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) 
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.plot(df)
        ax.set_xlabel('hour')
        ax.set_ylabel('Consumption (l/s)')
        #ax.set_title('Hourly Forecasting')
        ax.legend(('real consumption','1hr','2hr','6hr','12hr','24hr'))
        ax.grid(True)       
        fig.autofmt_xdate()
        if save==True:
            plt.savefig('plot_multiple_rolled_prediction.png', dpi=300,
                        bbox_inches='tight')
        plt.show() 
        return df
    
    
    
    """Voglio plottare i boxplot dell'errore medio assoluto sulla parte di
    test tramite boxplot su aggregazione temporale diversa che si può modif
    - hourly
    - daily
    - monthly"""
    def plot_boxplot(self, time, error, dataset=None):
        if isinstance(dataset, type(None)) == True:
            dataset=self.df_test
        if error=='mae':
            df = abs(self.df_real-dataset)
        elif error=='ae':
            df = (self.df_real-dataset)
        elif error=='mape':
            df = abs((self.df_real-dataset)/self.df_real)
        df = df.dropna()
        fig, ax = plt.subplots(figsize=(18,8))
        if time=='hourly':
            seaborn.boxplot(df.index.hour, df['h average'], ax=ax)
        elif time == 'daily':
            seaborn.boxplot(df.index.dayofweek, df['h average'], ax=ax)
        elif time == 'monthly':
            seaborn.boxplot(df.index.month, df['h average'], ax=ax)
        ax.set(xlabel=time, ylabel='error distribution')
        ax.axhline(y=0, xmin=-1, xmax=32)
        #plt.savefig('box.png', dpi=300)
        plt.show() 
    
    """Voglio plottare le differenze tra ts reale e ts modellata con:
        time = aggregazione temporale di base
        """
    def plot_differences(self, time, year=None):
        if time == 'daily':
            time = 'D'
        elif time == 'weekly':
            time = 'w'
        elif time == 'monthly':
            time = 'm'
        elif time == 'hourly':
            time = 'H'
        if year == None:
            df_real = self.df_real.resample(time).mean()
            df_test = self.df_test.resample(time).mean()
            df_train = self.df_train.resample(time).mean()
        else:
            df_real = self.df_real[self.df_real.index.year==year].resample(time).mean()
            df_test = self.df_test[self.df_real.index.year==year].resample(time).mean()
            df_train = self.df_train[self.df_real.index.year==year].resample(time).mean()
        # plot
        fig, ax = plt.subplots(figsize=(18, 6))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.plot(df_real-df_train)
        #ax.plot(df_train)
        ax.plot(df_real-df_test)
        ax.set_xlabel(time)
        ax.set_ylabel('Consumption (l/s)')
        ax.set_title('Hourly Forecasting')
        ax.legend(('real consumption','train prediction','test prediction'))
        ax.grid(True)       
        fig.autofmt_xdate()
        #plt.savefig('differ.png', dpi=300)
        plt.show()
        
    
    """Funzione per fare easy il mean absolute percantage error"""
    def mean_absolute_percentage_error(self, y_true, y_pred): 
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        y_true = y_true.reshape(y_true.size,)
        y_pred = y_pred.reshape(y_pred.size,)
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    """ Funzione per calcolare i dataframe dei minimi e dei massimi"""
    def min_max(self, Min, Max, reale, forecast):
        min_df = pd.merge(reale[reale<Min].dropna(),
                          forecast, left_index=True,
                          right_index=True)
        max_df = pd.merge(reale[reale>Max].dropna(),
                          forecast, left_index=True,
                          right_index=True)
        return min_df, max_df
    
    
    """Funzione per calcolare gli errori sui minimi e massimi"""    
    def min_max_errors(self, Min, Max, reale, forecast):
        min_df, max_df = self.min_max(Min, Max, reale, forecast)
        self.mse_min = mean_squared_error(min_df.iloc[:,0].values,
                                          min_df.iloc[:,1].values)
        self.mse_max = mean_squared_error(max_df.iloc[:,0].values,
                                          max_df.iloc[:,1].values)
        print('MSE MINIMI: ', round(self.mse_min,3),'\t\tMSE MASSIMI: ' ,
              round(self.mse_max,3))
        self.rmse_min = math.sqrt(mean_squared_error(min_df.iloc[:,0].values,
                                                     min_df.iloc[:,1].values))
        self.rmse_max = math.sqrt(mean_squared_error(max_df.iloc[:,0].values,
                                                     max_df.iloc[:,1].values))
        print('RMSE MINIMI: ', round(self.rmse_min,3),'\t\tRMSE MASSIMI: ' ,
              round(self.rmse_max,3))
        self.mae_min = mean_absolute_error(min_df.iloc[:,0].values,
                                           min_df.iloc[:,1].values)
        self.mae_max = mean_absolute_error(max_df.iloc[:,0].values,
                                           max_df.iloc[:,1].values)
        print('MAE MINIMI: ', round(self.mae_min,3),'\t\tMAE MASSIMI: ' ,
              round(self.mae_max,3))
        self.r2_min = r2_score(min_df.iloc[:,0].values, min_df.iloc[:,1].values)
        self.r2_max = r2_score(max_df.iloc[:,0].values, max_df.iloc[:,1].values)
        print('R2 MINIMI: ', round(self.r2_min,3),'\t\tR2 MASSIMI: ' ,
              round(self.r2_max,3))
        self.mape_min = self.mean_absolute_percentage_error(min_df.iloc[:,0].values,
                                                            min_df.iloc[:,1].values)
        self.mape_max = self.mean_absolute_percentage_error(max_df.iloc[:,0].values,
                                                            max_df.iloc[:,1].values)
        print('MAPE MINIMI: ', round(self.mape_min,3),'\t\tMAPE MASSIMI: ' ,
              round(self.mape_max,3))
        

        
    """Calcola root mean squared error. sono aggiunte anche le metriche sui 
    minimi, i cui estremi vanno fissati. Nel caso venga richiesta, ritorna
    la stringa necessaria per il logfile di output"""
    def errors(self, reale, forecast, want_string=True, want_minmax=False,
               Min = None, Max = None):
        mse = mean_squared_error(reale, forecast)
        print('MSE:  %.3f ' % (mse))
        rmse = math.sqrt(mean_squared_error(reale, forecast))
        print('RMSE: %.3f ' % (rmse))
        mae = mean_absolute_error(reale, forecast)
        print('MAE:  %.3f ' % (mae))
        r2 = r2_score(reale, forecast)
        print('R2:   %.3f ' % (r2))
        mape = self.mean_absolute_percentage_error(reale, forecast)
        print('MAPE: %.3f ' % (mape))
        # creo una error string da inserire nel logfile
        if want_string == True:
            error_string = \
            'risultati del modello sulla serie temporale: \n' + \
            '   MSE:       ' + str(round(mse, 3)) + '\n' +\
            '   RMSE:      ' + str(round(rmse, 3))  + '\n' +\
            '   MAE:       ' + str(round(mae, 3)) + '\n' +\
            '   R2:        ' + str(round(r2, 3)) + '\n' +\
            '   MAPE:      ' + str(round(mape, 3))  + '\n'
        if want_minmax == True:
            self.min_max_errors(Min, Max, reale, forecast)
            error_string_min = \
            '\nrisultati del modello sulla serie temporale sui MINIMI: \n' + \
            '   MSE:       ' + str(round(self.mse_min, 3)) + '\n' +\
            '   RMSE:      ' + str(round(self.rmse_min, 3))  + '\n' +\
            '   MAE:       ' + str(round(self.mae_min, 3)) + '\n' +\
            '   R2:        ' + str(round(self.r2_min, 3)) + '\n' +\
            '   MAPE:      ' + str(round(self.mape_min, 3))  + '\n'
            error_string_max = \
            '\nrisultati del modello sulla serie temporale sui MASSIMI: \n' + \
            '   MSE:       ' + str(round(self.mse_max, 3)) + '\n' +\
            '   RMSE:      ' + str(round(self.rmse_max, 3))  + '\n' +\
            '   MAE:       ' + str(round(self.mae_max, 3)) + '\n' +\
            '   R2:        ' + str(round(self.r2_max, 3)) + '\n' +\
            '   MAPE:      ' + str(round(self.mape_max, 3))  + '\n'
            error_string = error_string + error_string_min + error_string_max
        try:
            return error_string
        except UnboundLocalError:
            pass

    """Salviamo un bel dataframe contente la ts real e la forecast"""
    def saver_result(self):
        if self.model.do_you_want_to_save == True:
            newdf = self.df_real.copy()
            newdf['train_forecast'] = self.df_train['h average']
            newdf['test_forecast'] = self.df_test['h average']
            newdf.to_csv(self.model.newpath + '/results.csv', sep=';',
                         encoding='utf-8', index=True)
        else:
            pass






        











