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



class SVR_generator():
    
    def __init__(self):
        pass
    
    def SVR_model(self, model_type, n_output): 
        if n_output>1:
        #Chained Multioutput Regression:The first model in the sequence uses
        #the input and predicts one output; the second model uses the input 
        #and the output from the first model to make a prediction; the third 
        #model uses the input and output from the first two models to make a 
        #prediction, and so on.
            self.model_type = model_type
            model = SVR(kernel='rbf', epsilon=0.001)
            self.model = RegressorChain(model)
        else:
        #normal sSVR
            self.model_type = model_type
            self.model = SVR(kernel='rbf', epsilon=0.001)
        return self.model
    
    """Questo crea un modello per ogni output. Non è un modello chained"""
    def MultiOutputSVR_model(self, model_type): 
        self.model_type = model_type
        model = SVR(kernel='rbf', epsilon=0.001)
        self.model = MultiOutputRegressor(model)
        return self.model
    
    def LinearRegression_model(self, model_type): 
        self.model_type = model_type
        self.model = LinearRegression()
        return self.model
    
    def KNeighborsRegressor_model(self, model_type): 
        self.model_type = model_type
        self.model = KNeighborsRegressor()
        return self.model
    
    def DecisionTreeRegressor_model(self, model_type): 
        self.model_type = model_type
        self.model = DecisionTreeRegressor()
        return self.model
        
        