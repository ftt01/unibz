# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 10:33:21 2019

@author: arie9
"""

from platypus import NSGAII, NSGAIII, EpsMOEA, SMPSO  
from platypus import Problem, Real #, Integer
import matplotlib.pyplot as plt
from platypus import operators
import numpy as np
import pandas as pd


class Hydro_optimization(Problem):
    
    def __init__(self, n_var, n_obj, n_constr, Q_in, Prezzi):
        super(Hydro_optimization, self).__init__(n_var, n_obj, n_constr)
        self.types[:] = [Real(0, 5), Real(0, 3)]
        self.constraints[:] = "<=0"
        self.Q_in = Q_in
        self.Prezzi = Prezzi
                
    def evaluate(self, solution):#, Q_in, Prezzi):
        Q_in = self.Q_in
        Prezzi = self.Prezzi
        x = solution.variables[0]
        y = solution.variables[1]
        solution.objectives[:] = [Q_in.sum()*x, Prezzi.sum()*y]
        solution.constraints[:] = [-x + y - 1, x + y - 7]
    
    

idro = pd.read_csv('out_ENSEMBLE_mean_flow.txt',skiprows=1, header=None, engine='python')
idro.index = pd.to_datetime(idro[0], format="%Y-%m-%d %H:%M" )
idro.drop(columns=idro.columns[[-1]], inplace=True) 
for i in range (idro.shape[1]-1):
    idro.drop(columns=idro.columns[[-2]], inplace=True) 
idro = idro.rename(columns = {idro.columns[0]: "Q_in"})  

econ = pd.read_csv('input/eco/2019_E0.txt', sep=',',  encoding='utf-8' )
econ.index = pd.to_datetime(econ['Date'], format="%Y-%m-%d %H:%M" )
econ.drop(columns=econ.columns[[-2]], inplace=True) 

econ = pd.merge(econ,idro, left_index=True, right_index=True).drop(columns=['Q_in'])



#
#algorithm = NSGAII(Hydro_optimization(2,2,2,idro['Q_in'],econ['Prices']))
#algorithm.run(1000)
#
#Variabili = list()
#Obiettivi = list()
#df_variabili = pd.DataFrame()
#df_fobiettivo = pd.DataFrame()
#nvar = 2
#
#for j in range (nvar):
#    Variabili.append([s.variables[j] for s in algorithm.result])
#    df_variabili[j] = Variabili[j]
#
#for j in range (nvar):
#    Obiettivi.append([s.objectives[j] for s in algorithm.result])
#    df_fobiettivo[j] = Obiettivi[j]
#
#df = pd.concat([df_variabili, df_fobiettivo], axis=1, ignore_index = True)
#
#df_variabili.to_csv('Variabili.txt', index=False)










