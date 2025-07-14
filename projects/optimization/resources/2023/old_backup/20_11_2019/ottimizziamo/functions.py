# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 09:28:58 2019

@author: arie9
"""
#import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime


class Optimisation_functions():
    
    def __init__(self, problem, idro_string, date, eco_string):
        self.problem = problem
        self.idro_case = idro_string
        self.eco_case = eco_string
        self.generate_string_idro(idro_string, date)
        self.generate_string_econ(eco_string)
        self.date = date
        self.output_string_gen()

        
    """Funzione per fare il parsing dei dati idrologici col 15"""
    def generate_string_idro(self, string, date):
        s0 = 'input/hydro'
        s1 = 'R1'
        s2 = '/'
        s3 = string
        s4 = 'forecast_'
        s5 = date
        s6 = 'out_ENSEMBLE_mean_flow.txt'
        self.idro_string = s0+s2+s1+s2+s3+s2+s4+s5+s2+s6
        
    """Funzione per fare il parsing dei dati economici"""
    def generate_string_econ(self, string):
        s0 = 'input/eco'
        s1 = '2019_'
        s2 = '/'
        s3 = string
        s6 = '.txt'
        self.eco_string = s0+s2+s1+s3+s6
        
    def output_string_gen(self):
        s1 = 'output/'
        s2 = 'R1'
        s3 = self.idro_case
        s4 = self.eco_case
        s5 = '_'
        s6 = '/'
        s7 = self.date + '.txt'
        self.output_path = s1+s2+s6+s3+s5+s4+s6
        self.output_string = s1+s2+s6+s3+s5+s4+s6+s7
        
    """Funzione per fare il parsing dei dati idrologici col 15"""
    def parsing_idro(self, n_hour):
        if self.problem == 0:
            idro = pd.read_csv(self.idro_string,skiprows=1,
                               header=None, engine='python')
            idro.index = pd.to_datetime(idro[0], format="%Y-%m-%d %H:%M")
            idro = idro[15]
            idro = idro.to_frame()
        elif self.problem == 1:
            idro = pd.read_csv('Dati/idro_const.txt',skiprows=1,
                               header=None, engine='python')
            idro.index = pd.to_datetime(idro[0], format="%Y-%m-%d %H:%M")
            idro.drop(columns=idro.columns[[-1]], inplace=True) 
        elif self.problem==2:
            idro = pd.read_csv('Dati/out_ENSEMBLE_mean_flow.txt',skiprows=1,
                               header=None, engine='python')
            idro.index = pd.to_datetime(idro[0], format="%Y-%m-%d %H:%M")
            idro.drop(columns=idro.columns[[-1]], inplace=True) 
        elif self.problem==3:
            idro = pd.read_csv('input/hydro/R1/H0/H0.txt',skiprows=1,
                               header=None, engine='python')
            idro.index = pd.to_datetime(idro[0], format="%Y-%m-%d %H:%M")
            idro.drop(columns=idro.columns[[0]], inplace=True)
        if self.problem == 3:
            date1 = pd.to_datetime(self.date, format="%d_%m_%y")
            date2 = date1 + datetime.timedelta(days=1)
            cond = (idro.index.date == date1) | (idro.index.date == date2)
            idro = idro[cond]        
            # considerando che dobbiamo andare dalle 8 alle 8:
            for i in range(8):
                idro = idro.drop(idro.index[[0]]) 
            for i in range(16):
                idro = idro.drop(idro.index[[-1]])   
            idro = idro.rename(columns = {idro.columns[0]: "Q_in"})
        else:
            for i in range (idro.shape[1]-1):
                idro.drop(columns=idro.columns[[-2]], inplace=True) 
            idro = idro.rename(columns = {idro.columns[0]: "Q_in"})
            for i in range (n_hour):
                idro = idro.drop(idro.index[[-1]])  
        return idro
    
    """Funzione per fare il parsing dei prezzi"""
    def parsing_economics(self):
        if self.problem == 0 or self.problem == 3:
            econ = pd.read_csv(self.eco_string, sep=',')
        elif self.problem == 1:
            econ = pd.read_csv('Dati/prices_example.txt', sep='\t')
        elif self.problem==2:
            econ = pd.read_csv('Dati/price_const.txt', sep='\t')
        econ.index = pd.to_datetime(econ['Date'], format="%Y-%m-%d %H:%M")
        econ.drop(columns=econ.columns[[-2]], inplace=True) 
        return econ
    
    """Funzione per fare il plot delle manovre 'migliori' ma è complesso in
    quanto è difficile trovare la miglior soluzione"""
    def plotter(self, Soluzioni, algorithm, n_hour):    
        solution = list()
        self.max_f1,self. max_f2, best = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        self.max_f1 = Soluzioni[Soluzioni[Soluzioni.columns[-2]] == 
                           Soluzioni[Soluzioni.columns[-2]].max()]
        self.max_f2 = Soluzioni[Soluzioni[Soluzioni.columns[-1]] == 
                           Soluzioni[Soluzioni.columns[-1]].max()]
        # zero solo è il dataframe in cui la massa è conservata
        self.zero_sol = Soluzioni[Soluzioni.index == [Soluzioni[Soluzioni.columns[-1]].
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
        print('BEST F1: f1 ed f2', self.max_f1[self.max_f1.columns[[-2,-1]]].values)
        print('BEST F2: f1 ed f2', self.max_f2[self.max_f2.columns[[-2,-1]]].values)
        print('BEST   : f1 ed f2', best[best.columns[[-2,-1]]].values)
        print('ZERO   : f1 ed f2', self.zero_sol[self.zero_sol.columns[[-2,-1]]].values)
        #drop delle f obiettivo, rimangono solo le manovre
        self.max_f1.drop(columns=self.max_f1.columns[[-1,-2]], inplace=True)
        self.max_f2.drop(columns=self.max_f2.columns[[-1,-2]], inplace=True)
        best.drop(columns=best.columns[[-1,-2]], inplace=True)
        self.zero_sol.drop(columns=self.zero_sol.columns[[-1,-2]], inplace=True)
        solution.append(self.max_f1)
        solution.append(self.max_f2)
        solution.append(self.zero_sol)
        #plot
        plt.figure(figsize=(18, 8)) 
        plt.plot(self.max_f1.transpose())  
        plt.plot(self.max_f2.transpose()) 
        #plt.plot(best.transpose()) 
        plt.plot(self.zero_sol.transpose()) 
        plt.gca().legend(('Massimo guadagno','Massimo risparmio acqua','Bilancio'))
        plt.xlabel('orario')
        plt.ylabel('Qout (m^3/s)')
        plt.savefig('Qout.png', dpi=300)
        plt.show()
        
        # ora la parte dei plot del livello del serbatoio
        V_0 = 100000
        #A = 57600
        self.ht = pd.DataFrame(columns=[0,1,2])
        idro = self.parsing_idro(n_hour)
        Q_in = idro['Q_in']
        econ = self.parsing_economics()
        econ = pd.merge(econ,idro, left_index=True,
                        right_index=True).drop(columns=['Q_in'])
        for j in range(3):
            h = list()
            v_i = list()
            for i in range(Soluzioni.shape[1]-2):
                v_i.append((Q_in[i] - solution[j].values.transpose()[i])*60*60)
                V = np.sum(v_i)+V_0 
                h.append(algorithm.problem.a + algorithm.problem.b*V +
                         algorithm.problem.c*np.power(V,2) +
                         algorithm.problem.d*np.power(V,3))
            self.ht[j] = h
        # plot del livello        
        plt.figure(figsize=(18, 8)) 
        plt.plot(self.ht[0])
        plt.plot(self.ht[1])
        plt.plot(self.ht[2])
        plt.gca().legend(('Massimo guadagno','Massimo risparmio acqua','Bilancio'))
        plt.xlabel('orario', fontsize=14)
        plt.ylabel('h(m)', fontsize=14)
        plt.xticks(range(n_hour))
        plt.show()
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(18, 12))
        ax1.plot(self.ht[0])
        ax1.plot(self.ht[1])
        ax1.plot(self.ht[2])
        ax1.set_xticks(range(n_hour))
        ax1.set_ylabel('ht(m)', fontsize=14)
        ax1.legend(['Massimo guadagno','Massimo risparmio acqua','Bilancio'])
        ax2.plot(idro['Q_in'].values)
        ax2.set_xticks(range(n_hour))
        ax2.set_ylabel('Qin(m^3/s)', fontsize=14)
        ax2.legend(['Q in'])
        ax3.plot(econ['Prices'].values)
        ax3.set_xticks(range(n_hour))
        ax3.set_ylabel('Price(eur/Mwh)', fontsize=14)
        ax3.legend(['Prices'])
        plt.savefig('3.png', dpi=300)
        
    """Generare un output nella quale si vedono in ordine:
        Date - Qin - Qout - h(t) - Energy - Prezzi - Ricavo$$"""    
    def output_generator(self, algorithm, n_hour):
        idro = self.parsing_idro(n_hour)
        Q_out = self.zero_sol
        econ = self.parsing_economics()
        econ = pd.merge(econ,idro, left_index=True,
                        right_index=True).drop(columns=['Q_in'])
        Ricavo = algorithm.problem.obj_function(self.zero_sol)
        Energy = Ricavo/econ['Prices'].values
        df_output = idro.copy()
        df_output['Q_in'] = df_output['Q_in'].round(2)
        df_output['Q out(m^3/s)'] = Q_out.transpose().values.round(2)
        df_output['ht(m)'] = self.ht[2].values.round(2)
        df_output['prezzo (eur/MWh)'] = econ['Prices'].values.round(2)
        df_output['energy (MWh)'] = Energy.transpose().values.round(2)
        df_output['ricavo (eur)'] = Ricavo.transpose().values.round(2)
        # save output
        df_output.to_csv(self.output_string, sep=';', encoding='utf-8')
        
        
        
        
        
        
        