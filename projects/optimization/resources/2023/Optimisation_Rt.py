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
from functions import Output_collect
import datetime

# suppress a warning
pd.options.mode.chained_assignment = None  # default='warn'

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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
                 d, e, f, v_0, v_max, Q_out_constr):
        super(Hydro_optimization, self).__init__(n_var, n_obj, n_constr)

        self.types[:] = Real(Q_min, Q_max) #Custom_type(Q_min, Q_max) #
        self.directions[:] = Problem.MAXIMIZE
        self.constraints[:] = ">=0"
        self.Q_in = Q_in
        self.Prezzi = np.asarray(Prezzi)
        self.ore = n_var #Q_in.shape[0]
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
        self.e = e
        self.f = f
        self.v_max = v_max
        self.v_0 = v_0
        self.Q_out_constr = Q_out_constr
        
    """metodo per definire le proprietà dell'impianto come il salto e le
    perdite idrauliche. Inserito Strickler per ora come formulazione"""    
    def impianto(self, Q):
        # aggiungere h serbatoio
        alpha = (10.29*np.power(Q, 2))/(np.power(self.ks, 2)*np.power(self.D, 5.33))
        self.dH = self.salto_lordo - alpha * self.L_mandata
    
    """metodo per definire le proprietà della macchina. Interpolazione lineare
    nel caso di rendimento reale. Se const viene assegnato come valore true
    allora il rendimento assume valore constante"""    
    def turbina(self, Q, const):
        q = np.array([])
        q = Q/self.Q_max
        if const == False:
            q_p = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            n_p = [0.4, 0.55, 0.66, 0.76, 0.84, 0.90, 0.93, 0.92, 0.87, 0.80]
            self.rend = np.interp(q, q_p, n_p)
        else:
            self.rend = 0.75
        
        
    """metodo per definire la curva di volume. Instanza try except solo per 
    poter utilizzare la curva di volume durante i plot fornendo input diverso 
    dal formato che generalmente usa platypus"""    
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
        self.volumes = V
        # sto sfiorando, ovvero ho un volume maggiore del massimo?
        cond4 = bool(any(v < self.v_max for v in V))
        #se vero fisso quei volumi al massimo consentito
        if cond4 == True:
            cond5 = V < self.v_max
            V[cond5] = self.v_max
        self.ht = (self.a + self.b*V + self.c*V*V + self.d*V*V*V+ self.e*V*V*V*V + self.f*V*V*V*V*V)
        # setto le condizioni booleane in cui h deve essere compreso nel range
        cond1 = bool(any(ht < self.h_min for ht in self.ht))
        cond2 = bool(any(ht > self.h_max for ht in self.ht))
        # questa se permnetto lo sfioro
        if  cond1 == True:
            self.cond =-1
        if cond2 == True: #ovvero se supero h_max fisso li il tirante sto sfiorando
            cond3 = self.ht > self.h_max
            self.ht[cond3] = self.h_max
            
    """mando tutto a zero se il constrain dice che è zero"""        
    def forced_warm_solution(self, solution):
        solution.variables = [i * 0 for i in solution.variables]
                          
    """metodo della classe per generare i constraint. occhio al numero e se ci 
    sono, altrimenti posso anche lasciarlo e non li legge"""    
    def constraint_gen(self, solution):
        if self.Q_out_constr == 0:
            self.forced_warm_solution(solution)
        # implemento la curva dei volumi per il constraint sullo stoccaggio 
        # di acqua massimo e minimo nel serbatoio. ricordare che i constraint
        # sono espressioni che devono essere maggiori di zero   
        self.curva_volume(solution)
        self.constr1 = self.cond
        # secondo constraint sulla massima portata turbinabile giornaliera
        Q_out = np.asarray(solution.variables) 
        max_Q_out = self.Q_out_constr*24
        # il secondo constraint impostato tra il 10% sopra e sotto la portata 
        # vincolata turbinabile
        daily_turb = np.sum(Q_out) 
        max_turb = max_Q_out*1
        min_turb = max_Q_out*0.001
        if daily_turb > max_turb or daily_turb < min_turb:
            self.constr2 = -1
        else:
            self.constr2 = +1
    
    """Funzione generare le funzioni obiettivo del problema. Care che self.Q_in
    dovrà essere le portate in ingresso e Prezzi il costo orario di Energia
    Attenzione che nella produzione il salto è dh + la quota del serbatoio"""    
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
        self.turbina(Q_out, const=True)
        self.curva_volume(solution)
        f_conv = 9.81/1000
        #
        Rt = f_conv*self.rend*self.Prezzi.mean()* \
            (self.volumes[-1]-self.v_0) \
            *(((self.ht[0]+self.ht[-1])/2) - self.h_min)
        
        
        produzione = (f_conv*Q_out*(self.dH + self.ht - self.h_min)*self.rend*prezzi)
        portate = (Q_in-Q_out)
            
        self.obj1 = np.sum(produzione)
        self.obj2 = np.sum(portate)
        return produzione
        
        
    """Funzione per assegnare le funzioni obj e i constraint al problema"""             
    def evaluate(self, solution):
        self.obj_function(solution)
        self.constraint_gen(solution)
        #assegno le function in maniera pulita
        solution.objectives[0] = self.obj1
        #solution.objectives[1] = self.obj2
        #assegno i constraint in maniera pulita se ci sono
        solution.constraints[0] = self.constr1
        solution.constraints[1] = self.constr2
        
"""Regolarizzatore per il problema mono-obiettivo. Se il risultato viola il 
constraint della massima turbinabile ritorna la variabile cond come False"""    
def regularizer(Q_constr_turb,
                Q_out):
    cond = True
    # daily_turb = np.sum(np.asarray(Q_out))
    daily_turb = Q_out[:1].sum(axis=1).values[0]
    max_Q_out = Q_constr_turb*24
    print('optimized flow:  ',  daily_turb,
          '  constraint:  ',    max_Q_out)
    if daily_turb > 1.1 * max_Q_out:
        cond = False
    else:
        pass
    return cond

"""Regolarizzatore per il problema mono-obiettivo. Calcola il bilancio di 
volume nel serbatoio come volume iniziale + Qin - Qout sul giorno. Se il 
risultato è negativo vuol dire che lo sto obbligando a turbinare di più di
quel che c'è. Se ciò accade modifico il constraint per rispettare ciò e lo
do come output del metodo."""    
def regularizer2(Q_constr_turb, v_0, Q_in):
    daily_volume_constr_turb = Q_constr_turb*24*60*60
    daily_volume_inflow = np.sum(np.asarray(Q_in.values))*60*60
    balance = v_0 + daily_volume_inflow - daily_volume_constr_turb 
    if balance < 0:
        print('The basin is empty. Adjustment of the turbined volume\n')
        new_Q_constr = (v_0 + daily_volume_inflow)/24/60/60
    else:
        new_Q_constr = Q_constr_turb
    return new_Q_constr

"""Regolarizzatore per il problema mono-obiettivo. Calcola il bilancio di 
volume nel serbatoio come volume iniziale + Qin - Qout sul giorno. Se il 
risultato è tale da sfiorare perchè il serbatoio è pieno, vado a modificare
il constraint per turbinare tutta la quantità entrante, se possibile. Inoltre
va imposto il check che il constraint non superi la Qmax della macchina"""    
def regularizer3(Q_constr_turb, v_0, Q_in, v_max, Q_max):
    daily_volume_constr_turb = Q_constr_turb*24*60*60
    daily_volume_inflow = np.sum(np.asarray(Q_in.values))*60*60
    balance = v_0 + daily_volume_inflow - daily_volume_constr_turb 
    if balance > v_max:
        print('The basin is full. Adjustment of the turbined volume\n')
        new_Q_constr = daily_volume_inflow/24/60/60
        if new_Q_constr > Q_max: #check che non superi la Qmax della macchina
            new_Q_constr = Q_max*0.95
    else:
        new_Q_constr = Q_constr_turb
    return new_Q_constr

"""Funzione che modifica il constraint del volume turbinabile ogni giorno
sulla base di quanto il modello di prezzi si discosta dal prezzo medio
visto nel periodo precedente. Gli step sono:
    1. importo i prezzi reali
    2. calcolo il prezzo medio di riferimento considerando i prezzi del giorno,
    e conforntando con i prezzi dei 30 giorni precedenti. Moltiplico per un 
    coefficiente (+- 20%) legato al volume residuo
    3. quanti prezzi superano il mio valore di riferimento? così ho il numero
    di ore del giorno in cui questo accade
    4. il constraint è ottenuto poi moltiplicando il numero di ore per la
    turbinata massima e dividendo per 24 (Q media daily)"""
def price_constr(Q_constr_turb, the_date, vol_resid, vol_max, vol_min,
                 price, q_max_turb):
    econ_real = pd.read_csv('input/eco/prezzi_energia.csv', sep=',',
                       engine='python')
    econ_real.index = pd.to_datetime(econ_real['datetime'], format="%Y-%m-%d %H:%M:%S")
    econ_real.drop(columns=econ_real.columns[[0]], inplace=True) 
    # calcolo il prezzo di riferimento dei 30 giorni precedenti. Devo scegliere
    # il quantile che mi interessa (ad esempio 0.5 per la mediana)
    p_ref = np.quantile(econ_real[the_date-datetime.timedelta(days=30) :\
                                  the_date-datetime.timedelta(days=1)].values, 0.5)
    # calcolo un coefficiente che vari da 0.8 ad 1.2 in base al volume
    # residuo e linearmente. il coeff sarà più basso se il volume è vicino
    # a V_max (turbino di puù), e più altro se vicino a V_min
    coeff_volume = 0 + 2 * (vol_resid-vol_max)/(vol_min - vol_max)
    #coeff_volume = 0.5 + 1 * (vol_resid-vol_max)/(vol_min - vol_max)
    #coeff_volume = 1
    # quindi aggiusto la soglia del prezzo col coefficiente in funzione del
    # volume residuo, variadolo di un +- n% 
    p_ref = p_ref * coeff_volume
    # calcolo quanti valori sono sopra il prezzo di riferimento oggi
    n_ore = (price>p_ref).sum().values[0]
    Q_constr_turb = n_ore*q_max_turb/24
    print('the adjusted constraint is:', Q_constr_turb)
    return Q_constr_turb

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
p_m = prbabilità di mutazione polinomiale
problem = oggetto di Platypus con le sue definizioni"""
def alogorithm_creation(string, pop, p_c, p_m, problem):
    
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
        algorithm = SMPSO(problem, swarm_size=1000, leader_size=1000,
                            mutation_probability = 0.25,
                            mutation_perturbation = 0.5
                            )    

    return algorithm



"""Main code. Qui quasi tutti i parametri sono definiti. la stringa permette
di scegliere quale algoritmo testare"""
def main():
    # seleziona qui l'algoritmo che vuoi usare
    string = 'SMPSO'
    t = time.time()
    #parametri per l'algoritmo
    pop = 200
    n_gen = 100000
    p_c = 0.9
    p_m = 0.25
    n_var = 24          # numero di variabili. 24 come le 24 ore del giorno
    n_obj = 1           # numero funzioni obiettivo
    n_constr = 2        # numero constraints imposti 
    # =========================================================================
    """problem variables refer to:"""
    #     0 = idro const e economia real price
    # =========================================================================
    problem = 0
    serbatoio = 'Vernago'
    if serbatoio =='Vernago':
        # impianto
        salto_mandata = 1070
        L_mandata = 0 #così annullo le perdite di carico e i due sotto non servono
        ks_mandata = 80
        D = 2
        # parametri sistema fisico
        Q_min = 0
        Q_max = 13.7
        h_min = 1637.65
        h_max = 1689.5
        # Curva di volume: ht = (a + b*v_0 + c*v_0*v_0 + d*v_0*v_0*v_0)
        a = 1642
        b = 1.945919*1e-6  #1/A
        c = -3.692142*1e-14
        d = 4.109*1e-22
        e = 0
        f = 0
        v_0 = 11000000  # viene modificato nel ciclo (prima era 40000000)
        v_max = 42400000

    elif serbatoio =='Monguelfo':
        # impianto
        salto_mandata = 185
        L_mandata = 0 #così annullo le perdite di carico e i due sotto non servono
        ks_mandata = 80
        D = 2
        # parametri sistema fisico
        Q_min = 0
        Q_max = 22
        h_min = 1026
        h_max = 1055
        # Curva di volume: ht = a + b*v_0 + c*v_0*v_0 + d*v_0*v_0*v_0 + e*v_0*v_0*v_0*v_0 + f*v_0*v_0*v_0*v_0*v_0 
        a = 1027.2
        b = 1.80993464*1e-5  #1/A
        c = -8.69451817*1e-12
        d = 2.30915180*1e-18
        e = -2.78430073*1e-25
        f = +1.21936815*1e-32
        v_0 = 5300000  # viene modificato nel ciclo
        v_max = 5700000

    # parametri temporali che definizcono la simulazione
    start_date = '02_10_21 0'
    date = pd.to_datetime(start_date, format="%d_%m_%y %H")
    start_date = pd.to_datetime(start_date, format="%d_%m_%y %H")
    n_day = 364
    fail_count = 0
    collector = Output_collect()    # inizializzo l'oggetto collect
    
    i = 0
    while i < n_day:   
        print('Hydropotimisation launched with '+string+'\nPlease wait... \n')
        print('Actual date: ', date )
        # genero la classe funzioni
        functions = Optimisation_functions(problem, date, serbatoio)
        # parsing dei dati
        idro, Q_out_constr, idro_real = functions.parsing_idro()
        print('the original constraint is:', Q_out_constr)
        econ = functions.parsing_economics()
        econ = pd.merge(econ,idro, left_index=True,
                        right_index=True).drop(columns=['Q_in'])
        
        # Qui modifico il Q_out_constr completamente. Inserisco la nuova logica
        # in cui il constraint è legato al prezzo medio. Commentare se si 
        # vuole tornare alla logica del volume fissato da storico
        Q_out_constr = price_constr(Q_constr_turb = Q_out_constr,
                                    the_date = date,
                                    vol_resid = v_0,
                                    vol_max = v_max,
                                    vol_min = 0, #v_max*0.8
                                    price = econ,
                                    q_max_turb = Q_max)
      
        # verifico che il serbatoio non sia vuoto e in caso modifico il constr
        Q_out_constr = regularizer2(Q_constr_turb = Q_out_constr,
                                    v_0 = v_0, 
                                    Q_in = idro['Q_in'])
        # se il serbatoio è pieno posso turbinare di più e modifico il constr
        Q_out_constr = regularizer3(Q_constr_turb = Q_out_constr,
                                    v_0 = v_0, 
                                    Q_in = idro['Q_in'],
                                    v_max = v_max,
                                    Q_max = Q_max)
        # inizializzo l'algoritmo
        print(Q_out_constr)
        algorithm = alogorithm_creation(string, pop, p_c, p_m, Hydro_optimization
                                        (n_var, n_obj, n_constr, Q_min, Q_max,
                                         h_min, h_max, idro['Q_in'],
                                         econ['values'].values, salto_mandata,
                                         L_mandata, ks_mandata, D, a, b, c, d,
                                         e, f, v_0, v_max, Q_out_constr))
        algorithm.run(n_gen)
        print('Elapsed time for simulation: %s ' % (time.time() - t))       
        # genero il file Solution.txt che contiene variabili e f_obj
        var_saver(algorithm)
        Soluzioni = pd.read_csv('Solution.txt', engine='python')
        # selezione delle soluzioni richiamando il metodo
        Q_out = Soluzioni[Soluzioni.columns[:23]]
        cond = regularizer(Q_constr_turb = algorithm.problem.Q_out_constr,
                           Q_out = Q_out)
        # se la simulazione ha rispettato il constraint salva e vai avanti.
        # dunque aggiorna anche la data per il ciclo for
        if cond == True:
            # va aggiornato anche il volume ad ogni ciclo!
            v_0 = functions.solution_selector(Soluzioni, algorithm)
            output = functions.output_generator(algorithm, n_var)
            collector.fill(output)
            date = date + datetime.timedelta(days=1)
            i = i+1
        # se la simulazione non ha rispettato il constraint ritenta
        elif cond == False:
            fail_count = fail_count+1
            print('Failed to converge. Fail number: %s \n' % fail_count)
    #salva tutto
    collector.saver(problem, start_date)
    #genero gli output definitivi
    final_output = collector.list_return()
    print('Optimisation ended with fails:: %s \n' % fail_count)
    return algorithm, final_output, collector
# ===================================================================
"""Main launcher"""
# ===================================================================
if __name__ == "__main__":
    for i in range(1):
        algorithm, final_output, collector = main()    
#    Soluzioni = pd.read_csv('Solution.txt', engine='python')
#    
    Output = pd.read_csv('output/econ_real/' + collector.name +'.txt',sep=';', engine='python')
    Output.index = pd.to_datetime(Output['Unnamed: 0'], format="%Y-%m-%d %H:%M:%S" )
    Output.drop(columns=Output.columns[[0]], inplace=True) 
#    
    Output_collect().complete_plotter(n_days=364, output=Output)



