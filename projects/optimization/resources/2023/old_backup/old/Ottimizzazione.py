# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 18:19:28 2019

@author: arie9
"""

from platypus import NSGAII, NSGAIII, EpsMOEA, SMPSO  
from platypus import Problem, Real #, Integer
import matplotlib.pyplot as plt
from platypus import operators
import numpy as np
import pandas as pd

plt.rc('font', size = 12, weight='bold')

class Hydro_optimization(Problem):
    
    """Inizializzo la classe"""
    def __init__(self, n_var, n_obj, n_constr, Q_min, Q_max, h_min, h_max,
                 Q_in, Prezzi):
        super(Hydro_optimization, self).__init__(n_var, n_obj, n_constr)
        self.types[:] = Real(Q_min, Q_max)
        self.constraints[:] = ">=0"
        self.Q_in = Q_in
        self.Prezzi = np.asarray(Prezzi)
        self.ore = Q_in.shape[0]
        self.directions[:] = Problem.MAXIMIZE
        self.Q_max = Q_max
        self.h_min = h_min
        self.h_max = h_max
        
    """metodo per definire le proprietà dell'impianto come il salto e le
    perdite idrauliche"""    
    def impianto(self):
        salto_lordo = 50
        self.dH = salto_lordo
    
    """metodo per definire le proprietà della macchina"""    
    def turbina(self, Q):
        q = np.array([])
        q = Q/self.Q_max
        q_p = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        n_p = [0.4, 0.55, 0.66, 0.76, 0.84, 0.90, 0.93, 0.92, 0.87, 0.80]
        self.rend = np.interp(q, q_p, n_p)
    
    """metodo per definire la curva di volume"""    
    def curva_volume(self, solution):
        self.v_0 = 200000
        A = 31250
        a = 0.0
        b = 1/A
        c = 0.0
        d = 0.0
        V = list()
        v_i = list()
        self.cond = 1
        self.ht = list()
        for i in range(self.ore):
            v_i.append((self.Q_in[i] - solution.variables[i])*60*60)
            V.append(np.sum(v_i[:i]) + self.v_0)
            self.ht.append(a + b*V[i] + c*np.power(V[i],2) + d*np.power(V[i],3))
            if (self.ht[i]<self.h_min) or (self.ht[i]>self.h_max):
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
        # non mi piace, lo voglio sotto calcolo matriciale in numpy
#        for i in range(self.ore):
#            Q_in = self.Q_in[i]
#            prezzi = self.Prezzi[i]
#            Q_out = solution.variables[i] 
#            self.impianto()
#            self.turbina(Q_out)
#            f_conv = 9.81/1000
#            produzione.append(f_conv*Q_out*self.dH*self.rend*prezzi)
#            portate.append(Q_in-Q_out)
        
        Q_in = self.Q_in
        prezzi = self.Prezzi
        Q_out = np.asarray(solution.variables) 
        self.impianto()
        self.turbina(Q_out)
        f_conv = 9.81/1000
        produzione = (f_conv*Q_out*self.dH*self.rend*prezzi)
        portate = (Q_in-Q_out)
            
        self.obj1 = np.sum(produzione)
        self.obj2 = np.sum(portate)
        
    """Funzione per assegnare le funzioni obj e i constraint al problema"""             
    def evaluate(self, solution):
        #assegno le function in maniera pulita
        self.obj_function(solution)
        solution.objectives[0] = self.obj1
        solution.objectives[1] = self.obj2
        #assegno i constraint in maniera pulita se ci sono
        self.constraint_gen(solution)
        solution.constraints[0] = self.constr1
        #solution.constraints[1] = self.constr2
            
"""Funzione per fare il parsing dei dati idrologici"""
def parsing_idro():
    idro = pd.read_csv('Dati/out_ENSEMBLE_mean_flow.txt',skiprows=1, header=None, engine='python')
    idro.index = pd.to_datetime(idro[0], format="%Y-%m-%d %H:%M" )
    idro.drop(columns=idro.columns[[-1]], inplace=True) 
    for i in range (idro.shape[1]-1):
        idro.drop(columns=idro.columns[[-2]], inplace=True) 
    idro = idro.rename(columns = {idro.columns[0]: "Q_in"})  
    return idro
"""Funzione per fare il parsing dei prezzi"""
def parsing_economics():
    econ = pd.read_csv('Dati/prices_example.txt', sep='\t')
    econ.index = pd.to_datetime(econ['Date'], format="%Y-%m-%d %H:%M" )
    econ.drop(columns=econ.columns[[-2]], inplace=True) 
    return econ

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
    
"""Funzione per fare il plot delle manovre 'migliori' ma è complesso in
quanto è difficile trovare la miglior soluzione"""
def plotter(Soluzioni):
    solution = list()
    max_f1, max_f2, best = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    max_f1 = Soluzioni[Soluzioni[Soluzioni.columns[-2]] == 
                       Soluzioni[Soluzioni.columns[-2]].max()]
    max_f2 = Soluzioni[Soluzioni[Soluzioni.columns[-1]] == 
                       Soluzioni[Soluzioni.columns[-1]].max()]
    # zero solo è il dataframe in cui la massa è conservata
    zero_sol = Soluzioni[Soluzioni.index == [Soluzioni[Soluzioni.columns[-1]].
                                             abs().argsort()[:1].values[0]]]
    # un po di conti per trovare la distanza euclidea, ma considerando il peso 
    # totalmente diverso di prezzi e portate, si può provare adimensionalizzand
    f1_mean = Soluzioni[Soluzioni.columns[-2]].mean()
    f2_mean = Soluzioni[Soluzioni.columns[-1]].mean()
    a = np.sqrt(np.power(Soluzioni[Soluzioni.columns[-2]]/f1_mean,2)
    +np.power(Soluzioni[Soluzioni.columns[-1]]/f2_mean,2))
    b = a.max()
    best = Soluzioni[Soluzioni.index == a.index[a == b][0]]
    #mostriamo i valori delle funzioni obiettivo dei 3 individui
    print('BEST F1: f1 ed f2', max_f1[max_f1.columns[[-2,-1]]].values)
    print('BEST F2: f1 ed f2', max_f2[max_f2.columns[[-2,-1]]].values)
    print('BEST   : f1 ed f2', best[best.columns[[-2,-1]]].values)
    print('ZERO   : f1 ed f2', zero_sol[zero_sol.columns[[-2,-1]]].values)
    #drop delle f obiettivo, rimangono solo le manovre
    max_f1.drop(columns=max_f1.columns[[-1,-2]], inplace=True)
    max_f2.drop(columns=max_f2.columns[[-1,-2]], inplace=True)
    best.drop(columns=best.columns[[-1,-2]], inplace=True)
    zero_sol.drop(columns=zero_sol.columns[[-1,-2]], inplace=True)
    solution.append(max_f1)
    solution.append(max_f2)
    solution.append(zero_sol)
    #plot
    plt.figure(figsize=(18, 8)) 
    plt.plot(max_f1.transpose())  
    plt.plot(max_f2.transpose()) 
    #plt.plot(best.transpose()) 
    plt.plot(zero_sol.transpose()) 
    plt.gca().legend(('Massimo guadagno','Massimo risparmio acqua','Bilancio'))
    plt.xlabel('orario')
    plt.ylabel('Qout (m^3/s)')
    plt.show()
    
    # ora la parte dei plot del livello del serbatoio
    ht = pd.DataFrame(columns=[0,1,2])
    idro = parsing_idro()
    Q_in = idro['Q_in']
    for j in range(3):
        h = list()
        v_i = list()
        for i in range(Soluzioni.shape[1]-2):
            v_i.append((Q_in[i] - solution[j].values.transpose()[i])*60*60)
            V = np.sum(v_i)+200000 
            h.append((1/31250)*V)
        ht[j] = h
    # plot del livello    
    plt.figure(figsize=(18, 8)) 
    plt.plot(ht[0])
    plt.plot(ht[1])
    plt.plot(ht[2])
    plt.gca().legend(('Massimo guadagno','Massimo risparmio acqua','Bilancio'))
    plt.xlabel('orario')
    plt.ylabel('h(m)')
    plt.show()
    
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
    econ = pd.merge(econ,idro, left_index=True,
                    right_index=True).drop(columns=['Q_in'])
    
    # plot dei prezzi
    plt.figure(figsize=(18, 5)) 
    plt.plot(econ['Prices'].values)  
    plt.gca().legend(('Prices Forecast'))
    plt.show()
    # plot idrologico
    plt.figure(figsize=(18, 5)) 
    plt.plot(idro['Q_in'])
    plt.gca().legend(('Q_in Forecast'))
    plt.show()
    
    #parametri per l'algoritmo
    pop = 200
    n_gen = 100000
    p_c = 0.9
    p_m = 0.25
    n_var = 48
    n_obj = 2
    n_constr = 1
    Q_min = 0
    Q_max = 12.5
    h_min = 2
    h_max = 10

    algorithm = algorithm_creation(string, pop, p_c, p_m, Hydro_optimization
                                    (n_var, n_obj, n_constr, Q_min, Q_max,
                                     h_min, h_max, idro['Q_in'],
                                     econ['Prices'].values))
    algorithm.run(n_gen)
    
    #metodologia per graficare il fronte di Pareto
    fig = plt.figure(figsize = (18, 6))
    ax = fig.add_subplot(111)
    ax.scatter([s.objectives[0] for s in algorithm.result],
               [s.objectives[1] for s in algorithm.result])
    plt.xlabel('Guadagno')
    plt.ylabel('Qin - Qout')
    plt.show()   
    
    # per sport e vedere ste variabili
    var_saver(algorithm)
    
    
# ===================================================================
"""Main launcher"""
# ===================================================================
if __name__ == "__main__":
    main()    
    Soluzioni = pd.read_csv('Solution.txt', engine='python')
    
    plotter(Soluzioni)
    







