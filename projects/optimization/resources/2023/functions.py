# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 09:28:58 2019

@author: arie9
"""
#import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time


class Optimisation_functions():
    
    def __init__(self, problem, date, serbatoio):
        self.problem = problem        
        self.date = date
        self.serbatoio = serbatoio
        

    """Funzione per fare il parsing dei dati idrologici """
    def parsing_idro(self):
        if self.serbatoio == 'Vernago':
            stringa = '/Vernago/'
        elif self.serbatoio == 'Monguelfo': 
            stringa = '/Monguelfo/'
        try :
            idro = pd.read_csv('input/hydro' + stringa + 'forecast_alternati_scalati.csv', sep=',',
                               engine='python')
            idro.index = pd.to_datetime(idro['datetime'], format="%Y-%m-%d %H:%M:%S")
        except KeyError:
            idro = pd.read_csv('input/hydro' + stringa + 'forecast_alternati_scalati.csv', sep=',',
                               engine='python')
            idro.index = pd.to_datetime(idro['dates'], format="%Y/%m/%d %H:%M:%S")
        idro.drop(columns=idro.columns[[0]], inplace=True)
        start_date = self.date
        Q_in_val = idro['values'][idro.index.date == start_date].values
        idro_in = pd.DataFrame(index=pd.date_range(start_date, periods=24, freq='H'),
                                columns=['Q_in'])
        idro_in['Q_in']= idro
        # constraint su Q OUT
        try :
            idro_out = pd.read_csv('input/hydro' + stringa + 'dati_reali_scalati.csv', sep=',',
                                   engine='python')
            idro_out.index = pd.to_datetime(idro_out['datetime'], format="%Y-%m-%d %H:%M:%S")
        except KeyError:
            idro_out = pd.read_csv('input/hydro' + stringa + 'dati_reali_scalati.csv', sep=',',
                                   engine='python')
            idro_out.index = pd.to_datetime(idro_out['dates'], format="%Y/%m/%d %H:%M:%S")
        idro_out.drop(columns=idro_out.columns[[0]], inplace=True)
        Q_in_val = idro['values'][idro.index.date == start_date].values
        idro_out2 = pd.DataFrame(index=pd.date_range(start_date, periods=24, freq='H'),
                                columns=['Q_in_real'])
        idro_out2['Q_in_real']= idro_out
        # contraint sul forecast
        Q_out_val = idro_in['Q_in'].mean() 
        return idro_in, Q_out_val, idro_out2
    
    """Funzione per fare il parsing dei prezzi"""
    def parsing_economics(self):
        if self.problem == 0:
            econ = pd.read_csv('input/eco/prezzi_energia.csv', sep=',',
                               engine='python')
        elif self.problem == 1:
            econ = pd.read_csv('input/eco/armapq.csv', sep=',',
                               engine='python')
        elif self.problem == 2:
            econ = pd.read_csv('input/eco/ens_mea5eqw.csv', sep=',',
                               engine='python')
        elif self.problem == 3:
            econ = pd.read_csv('input/eco/ex5.csv', sep=',',
                               engine='python')
        econ.index = pd.to_datetime(econ['datetime'], format="%Y-%m-%d %H:%M:%S")
        econ.drop(columns=econ.columns[[0]], inplace=True) 
        return econ

    """Mi serve una funzione che mi estragga le migliori dal fronte, sia
    le Q_out, ma anche i tiranti. Nella prima parte faccio una selezione delle
    soluzioni della frontiera di pareto. Nella seconda parte ricavo i tiranti
    orari corrispondenti alle soluzioni estratte nella prima parte. L'output
    di questa funzione sarà V_out, ovvero il volume iniziale per la simulazione
    successiva"""
    def solution_selector(self, Soluzioni, algorithm):
        solution = list()
        self.max_f1, self.best = pd.DataFrame(), pd.DataFrame()
        self.max_f1 = Soluzioni[Soluzioni[Soluzioni.columns[-1]] == 
                           Soluzioni[Soluzioni.columns[-1]].max()]
        # per evitare di avere più soluzioni analoghe
        self.max_f1 = self.max_f1[self.max_f1.index==self.max_f1.index[0]]
        # La migliore è quella che soddifa il costraint alla perfezione
        constr = algorithm.problem.Q_out_constr*24
        sum_Q = Soluzioni[Soluzioni.columns[:23]].T.sum()
        difference= abs(sum_Q-constr)
        cond = (difference).min()
        self.best = Soluzioni[Soluzioni.index == difference.index[difference == cond][0]]
        #drop delle f obiettivo, rimangono solo le manovre
        self.max_f1.drop(columns=self.max_f1.columns[[-1]], inplace=True)
        self.best.drop(columns=self.best.columns[[-1]], inplace=True)
        solution.append(self.max_f1)
        solution.append(self.best)
        
        # ora la parte dei plot del livello del serbatoio
        V_0 = algorithm.problem.v_0
        self.ht = pd.DataFrame(columns=[0,1])
        idro, Qout_constr, idro_real = self.parsing_idro()
# =============================================================================
#       # La portate entrante reale però non è quella forecast! Il volume lo 
#       # aggiorno sulle turbinate ottimizzate e le portate entranti reali  
# =============================================================================
        Q_in = idro['Q_in']
        #Q_in = idro_real['Q_in_real']
        econ = self.parsing_economics()
        econ = pd.merge(econ,idro, left_index=True,
                        right_index=True).drop(columns=['Q_in'])
        for j in range(2):
            h = list()
            v_i = list()
            V_out = list()
            for i in range(Soluzioni.shape[1]-1):
                v_i.append((Q_in[i] - solution[j].values.transpose()[i])*60*60)
                V = np.sum(v_i)+V_0 
                # sto sfiorando? il volume cumulato supera il massimo?
                if V > algorithm.problem.v_max:
                    V = algorithm.problem.v_max 
                tirante = algorithm.problem.a + algorithm.problem.b*V \
                + algorithm.problem.c*V*V \
                + algorithm.problem.d*V*V*V \
                + algorithm.problem.e*V*V*V*V \
                + algorithm.problem.f*V*V*V*V*V
                # se sto sfiorando
                if tirante>algorithm.problem.h_max:
                    tirante = algorithm.problem.h_max
                    # devo ricalcolare il volume
                h.append(tirante)
                
            V_out.append(V)
            self.ht[j] = h
        return V_out[0]
    
        
    """Generare un output nella quale si vedono in ordine:
        Date - Qin - Qout - h(t) - Energy - Prezzi - Ricavo$$.
        Scegliere la soluzione nella prima variabile"""    
    def output_generator(self, algorithm, n_hour):
        solution_selected = self.best
        idro, Q_out_constr, idro_real = self.parsing_idro()
        Q_out = solution_selected
        econ = self.parsing_economics()
        econ = pd.merge(econ,idro, left_index=True,
                        right_index=True).drop(columns=['Q_in'])
        Ricavo = algorithm.problem.obj_function(solution_selected)
        Energy = Ricavo/econ['values'].values
        # fill dataframe
        df_output = idro.copy()
        df_output['Q_in'] = df_output['Q_in']
        df_output['Q_out_constr'] = algorithm.problem.Q_out_constr
        df_output['Q out(m^3/s)'] = Q_out.transpose().values
        df_output['ht(m)'] = self.ht[0].values
        df_output['prezzo (eur/MWh)'] = econ['values'].values.round(2)
        df_output['energy (MWh)'] = Energy.transpose().values.round(2)
        df_output['ricavo (eur)'] = Ricavo.transpose().values.round(2)
        # aggiungo la colonna con la Qout media giornaliera
        daily_mean_Qout = df_output['Q out(m^3/s)'].resample('D').mean()
        df_output['Q_in_real'] = idro_real['Q_in_real'] 
        # save output
        return df_output
        

"""Una classe semplice che genera una lista, appende i dati e li ritorna.
Aggiunto anche il metodo per plottare i risultati se richiesto"""    
class Output_collect():
    
    def __init__(self): 
        self.output_list = list()
        
    def fill(self, df_output):
        self.output_list.append(df_output)
        
    def list_return(self):
        return self.output_list        
        
    def saver(self, problem, date):
        if problem==0:
            self.problem_string = 'econ_real/'
        elif problem==1:
            self.problem_string = 'armapq/'
        elif problem==2:
            self.problem_string = 'ens_mea5eqw/'
        elif problem==3:
            self.problem_string = 'ex5/'
        self.df = pd.concat(self.output_list)
        self.string = date.strftime("%d_%m_%y")
        self.name = time.strftime("%Y%m%d-%H%M%S") + self.string
        self.df.to_csv('output/'+ self.problem_string + self.name +'.txt',
                       sep=';', encoding='utf-8')
        
    """funzione per fare il plot di piu giorni consecutivi"""    
    def complete_plotter(self, n_days, output=None):
        if isinstance(output, type(None)) == True:
            df = self.df
        else:
            df=output
        start_date = df.index[0]
        end_date = df.index[n_days*24-1]
        #
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, figsize=(18, 12))
        ax1.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        #ax1.xaxis.set_minor_locator(mdates.HourLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) 
        ax1.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax1.plot(df['ht(m)'][start_date:end_date])
        ax1.set_ylabel('ht(m)', fontsize=14)
        ax1.legend()
        ax1.grid(True)
        #
        ax2.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        #ax2.xaxis.set_minor_locator(mdates.HourLocator())
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) 
        ax2.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax2.plot(df['Q out(m^3/s)'][start_date:end_date])
        ax2.set_ylabel('Q out(m^3/s)', fontsize=14)
        ax2.legend()
        ax2.grid(True)
        #
        ax3.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        #ax3.xaxis.set_minor_locator(mdates.HourLocator())
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) 
        ax3.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax3.plot(df['prezzo (eur/MWh)'][start_date:end_date])
        ax3.set_ylabel('prezzo (eur/MWh)', fontsize=14)
        ax3.legend()
        ax3.grid(True)
        #
        ax4.xaxis.set_major_locator(mdates.HourLocator(interval=6))
        #ax4.xaxis.set_minor_locator(mdates.HourLocator())
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M')) 
        ax4.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax4.plot(df['Q_in'][start_date:end_date])
        # ax4.plot(df['Q_out_constr'][start_date:end_date])
        ax4.plot(df['Q_in_real'][start_date:end_date], 'b-o')
        ax4.set_ylabel('Q_in(m^3/s)', fontsize=14)
        ax4.legend(['Qin forecast', 'Qin real'])
        ax4.grid(True)
        fig.autofmt_xdate()
        plt.savefig('4.png', dpi=300)
        plt.show()
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
           
         
           
           
        
        
        
        
        