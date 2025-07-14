# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 09:00:56 2019

@author:ariele
Questo modulo permette l'utilizzo della support vector regressio come metodo 
per modellare una timew series e farne il forecast
"""

import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.multioutput import RegressorChain, MultiOutputRegressor

from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, r2_score, mean_squared_error

def mean_absolute_percentage_error(y_true, y_pred):
    """Custom function to calculate mean absolute percentage error (MAPE)"""
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

class SVR_gridsearch():

    def __init__(self, scorer):
        if scorer == 'rmse':
            self.scoring = make_scorer(mean_squared_error, squared=False)  # Create RMSE scorer
        elif scorer == 'mse':
            self.scoring = make_scorer(mean_squared_error, squared=True)  # Create MSE scorer
        elif scorer == 'r2':
            self.scoring = make_scorer(r2_score)  # Create R2 scorer
        elif scorer == 'mape':
            self.scoring = make_scorer(mean_absolute_percentage_error)  # Create R2 scorer
        else:
            self.scoring = None
    
    def SVR_model(self, train_X, train_y, param_grid={'kernel':['rbf'],'epsilon':[0.001],'C':[1.0]}):
        self.gs_model = GridSearchCV(SVR(), param_grid, cv=5, n_jobs=-1, scoring=self.scoring)
        self.gs_model.fit(train_X, train_y)
        return self.gs_model
    
    
    
    # def LinearRegression_model(self, estimator, param_grid={}):
    #     self.gs_model = GridSearchCV(estimator, param_grid, cv=5, n_jobs=-1)
    
    # def KNeighborsRegressor_model(self, estimator, param_grid={}):
    #     self.gs_model = GridSearchCV(estimator, param_grid, cv=5, n_jobs=-1)
    
    # def DecisionTreeRegressor_model(self, estimator, param_grid={}):
    #     self.gs_model = GridSearchCV(estimator, param_grid, cv=5, n_jobs=-1)

class SVR_generator():
    
    def __init__(self, scorer):
        if scorer == 'rmse':
            self.scoring = make_scorer(mean_squared_error, squared=False)  # Create RMSE scorer
        elif scorer == 'mse':
            self.scoring = make_scorer(mean_squared_error, squared=True)  # Create MSE scorer
        elif scorer == 'r2':
            self.scoring = make_scorer(r2_score)  # Create R2 scorer
        elif scorer == 'mape':
            self.scoring = make_scorer(mean_absolute_percentage_error)  # Create R2 scorer
        else:
            self.scoring = None
    
    def SVR_model(self, model_type, n_output=1, kernel='rbf', eps=0.001, C=1, grid_search=False):
        if n_output>1:
        #Chained Multioutput Regression:The first model in the sequence uses
        #the input and predicts one output; the second model uses the input 
        #and the output from the first model to make a prediction; the third 
        #model uses the input and output from the first two models to make a 
        #prediction, and so on.
            self.model_type = model_type
            if grid_search == True:
                model = SVR()
            else:
                model = SVR(kernel=kernel, epsilon=eps, C=C)
            self.model = RegressorChain(model)
        else:
        #normal SVR
            self.model_type = model_type
            if grid_search == True:
                self.model = SVR()
            else:
                self.model = SVR(kernel=kernel, epsilon=eps, C=C)
        return self.model
    
    """Questo crea un modello per ogni output. Non è un modello chained"""
    def MultiOutputSVR_model(self, model_type, kernel='rbf', eps=0.001, C=1, grid_search=False):
        self.model_type = model_type
        if grid_search == True:
            model = SVR()
        else:
            model = SVR(kernel=kernel, epsilon=eps, C=C)
        self.model = MultiOutputRegressor(model)
        return self.model

    def MultiOutputSVR_gs(self, train_X, train_y, param_grid={'kernel':['rbf'],'epsilon':[0.001],'C':[1.0]}):
        multi_output_svr_model = self.MultiOutputSVR_model(model_type="MultiOutputSVR")
        self.gs_model = GridSearchCV(
            multi_output_svr_model, param_grid, cv=5, n_jobs=-1, scoring=self.scoring)
        self.gs_model.fit(train_X, train_y)
        return self.gs_model.cv_results_
    
    # def LinearRegression_model(self, model_type): 
    #     self.model_type = model_type
    #     self.model = LinearRegression()
    #     return self.model
    
    # def KNeighborsRegressor_model(self, model_type): 
    #     self.model_type = model_type
    #     self.model = KNeighborsRegressor()
    #     return self.model
    
    # def DecisionTreeRegressor_model(self, model_type): 
    #     self.model_type = model_type
    #     self.model = DecisionTreeRegressor()
    #     return self.model