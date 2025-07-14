# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 18:19:28 2019

@author: arie9
"""

from platypus import NSGAII, NSGAIII, EpsMOEA, SMPSO  
from platypus import Problem, Real
from platypus import Type
import matplotlib.pyplot as plt
from platypus import operators
import numpy as np
import pandas as pd
import time
import random
from functions import Optimisation_functions

plt.rc('font', size = 12, weight='bold')

"""Platyupus mi permette di generare una mia classe con il metodo che voglio
usare per definire il range delle variabili. in questo caso posso specificare
con il metodo round il numero di cifre decimali da usare. Devo dire che questo
è di alto livello, peccato che ci mette na vita a convergere ahahaha"""
class Custom_type(Type):
      
    def __init__(self, min_value, max_value):
        super(Custom_type, self).__init__()
        self.min_value = float(min_value)
        self.max_value = float(max_value)
        
    def rand(self):
        return round(random.uniform(self.min_value, self.max_value),6)
        
    def __str__(self):
        return "Real(%f, %f)" % (self.min_value, self.max_value)
    

class Hydro_optimization(Problem):
    
    """Inizializzo la classe"""
    def __init__(self, n_var, n_obj, n_constr, Q_min, Q_max, h_min, h_max,
                 Q_in, Prezzi, salto_lordo, L_mandata, ks_mandata, D, a, b, c,
                 d, v_0, A):
        super(Hydro_optimization, self).__init__(n_var, n_obj, n_constr)
        self.types[:] = Real(Q_min, Q_max) #Custom_type(Q_min, Q_max) #
        self.constraints[:] = ">=0"
        self.Q_in = Q_in
        self.Prezzi = np.asarray(Prezzi)
        self.ore = n_var #Q_in.shape[0]
        self.directions[:] = Problem.MAXIMIZE
        self.Q_max = Q_max
        self.h_min = h_min
        self.h_max = h_max
        self.salto_lordo = salto_lordo
        self.L_mandata = L_mandata
        self.ks = ks_mandata
        self.D = D
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.A = A
        self.v_0 = v_0
        
    """metodo per definire le proprietà dell'impianto come il salto e le
    perdite idrauliche. Inserito Strickler per ora come formulazione"""    
    def impianto(self, Q):
        # aggiungere h serbatoio
        alpha = (10.29*np.power(Q, 2))/(np.power(self.ks, 2)*np.power(self.D, 5.33))
        self.dH = self.salto_lordo - alpha * self.L_mandata
    
    """metodo per definire le proprietà della macchina"""    
    def turbina(self, Q):
        q = np.array([])
        q = Q/self.Q_max
        q_p = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        n_p = [0.4, 0.55, 0.66, 0.76, 0.84, 0.90, 0.93, 0.92, 0.87, 0.80]
        self.rend = np.interp(q, q_p, n_p)
    
    """metodo per definire la curva di volume"""    
    def curva_volume(self, solution):                
        
        try:
            Q_out = np.asarray(solution.variables) 
        except AttributeError:
            Q_out = np.asarray(solution.values)
        V = np.array([])
        v_i = np.zeros([self.ore])
        v0 = np.zeros([self.ore])
        v0.fill(self.v_0)
        self.cond = 1
        self.ht = np.array([])
        v_i = (self.Q_in.values - Q_out)*60*60
        # vettore dei volumi cumulati che parte dal volume iniziale
        V = np.cumsum(v_i) + v0
        self.ht = (self.a + self.b*V + self.c*np.power(V,2) + 
                   self.d*np.power(V,3))
        # setto le condizioni booleane in cui h deve essere compreso nel range
        cond1 = bool(any(ht < self.h_min for ht in self.ht))
        cond2 = bool(any(ht > self.h_max for ht in self.ht))
        if  cond1 == True or cond2 == True :
            self.cond =-1
                          
    """metodo della classe per generare i constraint. occhio al numero e se ci 
    sono, altrimenti posso anche lasciarlo e non li legge"""    
    def constraint_gen(self, solution):
        # implemento la curva dei volumi per il constraint sullo stoccaggio 
        # di acqua massimo e minimo nel serbatoio. ricordare che i constraint
        # sono espressioni che devono essere maggiori di zero   
        self.curva_volume(solution)
        self.constr1 = self.cond
    
    """Funzione generare le funzioni obiettivo del problema. Care che self.Q_in
    dovrà essere le portate in ingresso e Prezzi il costo orario di Energia"""    
    def obj_function(self, solution):
        produzione = list()
        portate = list()
        # conto della produzione idroelettrica
        Q_in = self.Q_in
        prezzi = self.Prezzi
        try:
            Q_out = np.asarray(solution.variables) 
        except AttributeError:
            Q_out = solution
        self.impianto(Q_out)
        self.turbina(Q_out)
        self.curva_volume(solution)
        f_conv = 9.81/1000
        produzione = (f_conv*Q_out*(self.dH+self.ht)*self.rend*prezzi)
        portate = (Q_in-Q_out)
            
        self.obj1 = np.sum(produzione)
        self.obj2 = np.sum(portate)
        return produzione
        
        
    """Funzione per assegnare le funzioni obj e i constraint al problema"""             
    def evaluate(self, solution):
        #assegno le function in maniera pulita
        self.obj_function(solution)
        solution.objectives[0] = self.obj1
        solution.objectives[1] = self.obj2
        #assegno i constraint in maniera pulita se ci sono
        self.constraint_gen(solution)
        solution.constraints[0] = self.constr1
        

"""Funzione per fare il salvataggio del file Solution ordinato con tutte le
variabili e le funzioni obiettivo per ogni individuo"""
def var_saver(algorithm):
    Variabili = list()
    Obiettivi = list()
    df_variabili = pd.DataFrame()
    df_fobiettivo = pd.DataFrame()
    df = pd.DataFrame()
    nvar = algorithm.problem.nvars
    nobj = algorithm.problem.nobjs
    
    for j in range (nvar):
        Variabili.append([s.variables[j] for s in algorithm.result])
        df_variabili[j] = Variabili[j]
    for j in range (nobj):
        Obiettivi.append([s.objectives[j] for s in algorithm.result])
        df_fobiettivo[j] = Obiettivi[j]
        
    df = pd.concat([df_variabili, df_fobiettivo], axis=1, ignore_index = True)    
    df.to_csv('Solution.txt', index=False)
    

    
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
    t = time.time()
    # =========================================================================
    """problem variables refer to:"""
    #     0 = idro e economia variabili, e selezionabili sotto
    #     1 = idro costante, economia variabile testing
    #     2 = idro variabile, economia costante testing
    # =========================================================================
    problem = 0 
    # =========================================================================
    """case variables refer to:"""
    #      Arfimax    +  ICHYMOD WRF   --> H2 E1
    #      Econ real  +  ICHYMOD WRF   --> H2 E0
    #      Arfimax    +  ICHYMOD PF    --> H1 E1
    #      Econ real  +  ICHYMOD PF    --> H1 E0
    #      Arfimax    +  Idro real     --> H0 E1
    #      Econ real  +  Idro real     --> H0 E0
    # =========================================================================
    idro_string = 'H1'
    eco_string = 'E1'
    date = '12_08_19'
    if idro_string == 'H0':
        problem = 3

    print('idrology: ' + idro_string + '\neconomy:  ' + eco_string)
    print('Hydropotimisation launched with '+string+'\nPlease wait... \n')
    
    #parametri per l'algoritmo
    pop = 200
    n_gen = 2000
    p_c = 0.9
    p_m = 0.25
    n_var = 24
    n_obj = 2
    n_constr = 1
    # impianto
    salto_lordo = 100
    L_mandata = 150
    ks_mandata = 80
    D = 2
    # parametri sistema fisico
    Q_min = 0
    Q_max = 5
    h_min = 0.5
    h_max = 3.5
    # Curva di volume
    a = 0
    b = 6*1e-5  #1/A
    c = -4*1e-10
    d = 8*1e-16
    v_0 = 100000
    A = 57600
    functions = Optimisation_functions(problem, idro_string, date, eco_string)
    # parsing dei dati
    idro = functions.parsing_idro(n_var)
    econ = functions.parsing_economics()
    econ = pd.merge(econ,idro, left_index=True,
                    right_index=True).drop(columns=['Q_in'])
    
    algorithm = algorithm_creation(string, pop, p_c, p_m, Hydro_optimization
                                    (n_var, n_obj, n_constr, Q_min, Q_max,
                                     h_min, h_max, idro['Q_in'],
                                     econ['Prices'].values, salto_lordo,
                                     L_mandata, ks_mandata, D, a, b, c, d, v_0,
                                     A))
    algorithm.run(n_gen)
    print('Elapsed time for simulation: %s ' % (time.time() - t))
    #metodologia per graficare il fronte di Pareto
    fig = plt.figure(figsize = (18, 6))
    ax = fig.add_subplot(111)
    ax.scatter([s.objectives[0] for s in algorithm.result],
               [s.objectives[1] for s in algorithm.result])
    plt.xlabel('Guadagno', fontsize=14)
    plt.ylabel('Qin - Qout', fontsize=14)
    plt.savefig('pareto.png', dpi=300)
    plt.show()   
    
    # salvataggio file soluzioni e plotter
    var_saver(algorithm)
    Soluzioni = pd.read_csv('Solution.txt', engine='python')
    functions.plotter(Soluzioni, algorithm, n_var)
    functions.output_generator(algorithm, n_var)
    
    return algorithm
# ===================================================================
"""Main launcher"""
# ===================================================================
if __name__ == "__main__":
    algorithm = main()    
    Soluzioni = pd.read_csv('Solution.txt', engine='python')
    Output = pd.read_csv('Output.txt',sep=';', engine='python')
    Output.index = pd.to_datetime(Output['0'], format="%Y-%m-%d %H:%M:%S" )
    Output.drop(columns=Output.columns[[0]], inplace=True) 





