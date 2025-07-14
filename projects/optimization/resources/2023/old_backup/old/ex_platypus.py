# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 11:17:26 2018

@author: arie9
"""

from platypus import NSGAII, NSGAIII, EpsMOEA, SMPSO  
from platypus import Problem, Real #, Integer
import matplotlib.pyplot as plt
from platypus import operators
import numpy as np
import pandas as pd


class Hydro_optimization(Problem):
    
    ore = 4 #le ore da analizzare del forecast
    """Inizializzo la classe"""
    def __init__(self, n_var, n_obj, n_constr, Q_in, Prezzi):
        super(Hydro_optimization, self).__init__(n_var, n_obj, n_constr)
        self.types[:] = [Real(0, 5), Real(0, 3)]
        self.constraints[:] = "<=0"
        self.Q_in = Q_in
        self.Prezzi = Prezzi
    
    """metodo della classe per generare i constraint. occhio al numero"""    
    def constraint_gen(self, solution):
        x = solution.variables[0]
        y = solution.variables[1]
        self.constr1 = np.power((x-5),2) + np.power(y,2) - 25
        self.constr2 = -1 * np.power((x-8),2) -1 * np.power((y+3),2) + 7.7
        

    """Funzione generare le funzioni obiettivo del problema. Care che self.Q_in
    dovrà essere le portate in ingresso e Prezzi il costo orario di Energia"""    
    def obj_function(self, solution):
        Q_in = self.Q_in
        Prezzi = self.Prezzi
        x = solution.variables[0]
        y = solution.variables[1]
        self.obj1 = np.power(4*x,2)  + np.power(4*y,2) + Q_in[1]
        self.obj2 = np.power((x-5),2) + np.power((y-5),2) + Prezzi[1]
        
    """Funzione per assegnare le funzioni obj e i constraint al problema"""             
    def evaluate(self, solution):
        #assegno le function in maniera pulita
        self.obj_function(solution)
        solution.objectives[0] = self.obj1
        solution.objectives[1] = self.obj2
        #assegno i constraint in maniera pulita 
        self.constraint_gen(solution)
        solution.constraints[0] = self.constr1
        solution.constraints[1] = self.constr2
        
        
"""Funzione per fare il parsing dei dati idrologici"""
def parsing_idro():
    df_idro = pd.read_csv('Dati/idro.txt', sep=',')
    # ...
    return df_idro
"""Funzione per fare il parsing dei prezzi"""
def parsing_economics():
    df_prezzi = pd.read_csv('Dati/economico.txt', sep=',')
    # ...
    return df_prezzi

"""Genera l'algoritmo genetico selezionato. Per ora facciamolo easy, ma
dopo mettiamo anche la possibilità di scegliere anche altri algoritmi
pop = numero di popolazione
p_c = probabilità di crossover binario
p_m = prbabilità di mutazione polinomiale"""
def algorithm_creation(string, pop, p_c, p_m, problem):
    
    if string == 'NSGAII':
        
        algorithm = NSGAII(problem, population_size=pop,
                           variator = operators.SBX(probability=p_c),
                           mutation = operators.PM(probability=p_m),
                           selector = operators.TournamentSelector(2),  
                           comparator = operators.ParetoDominance()
                           )
    elif string == 'NSGAIII':
        algorithm = NSGAIII(problem, divisions_outer=10, population_size=pop,
                           variator = operators.SBX(probability=p_c),
                           mutation = operators.PM(probability=p_m),
                           selector = operators.TournamentSelector(2),  
                           comparator = operators.ParetoDominance()
                           )
    elif string == 'EpsMOEA':
        algorithm = EpsMOEA(problem, epsilons =0.5, population_size=pop,
                            variator = operators.SBX(probability=p_c),
                            mutation = operators.PM(probability=p_m),
                            selector = operators.TournamentSelector(2), 
                            comparator = operators.ParetoDominance()
                            )
        # devo adattare il codice per i PSO se serve
    elif string == 'SMPSO':
        algorithm = SMPSO(problem, swarm_size=100, leader_size=100,
                            mutation_probability = 0.1,
                            mutation_perturbation = 0.5
                            )    
    return algorithm



"""Main code. Qui quasi tutti i parametri sono definiti. la stringa permette
di scegliere quale algoritmo testare"""
def main():
    # seleziona qui l'algoritmo che vuoi usare
    string = 'NSGAII'
    # parsing dei dati
    idro = parsing_idro()
    econ = parsing_economics()
    #parametri per l'algoritmo
    pop = 100
    n_gen = 10000   
    p_c = 0.9
    p_m = 0.25
    n_var = 2
    n_obj = 2
    n_constr = 2

    algorithm = algorithm_creation(string, pop, p_c, p_m, Hydro_optimization
                                    (n_var, n_obj, n_constr,
                                     idro['Q_in'],econ['prezzi']))
    algorithm.run(n_gen)
    
    #metodologia per graficare il fronte di Pareto
    fig = plt.figure(figsize = (15, 6))
    ax = fig.add_subplot(111)
    ax.scatter([s.objectives[0] for s in algorithm.result],
               [s.objectives[1] for s in algorithm.result])
    plt.show()   
    
    # per sport e vedere ste variabili
    first_variable = [s.objectives[0] for s in algorithm.result]
    second_variable = [s.objectives[1] for s in algorithm.result]
    print(first_variable)
    print(second_variable)
    
# ===================================================================
"""Main launcher"""
# ===================================================================
if __name__ == "__main__":
    main()    
    
    
    
    
    
    



