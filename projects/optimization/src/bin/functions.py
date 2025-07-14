# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 09:28:58 2019

@author: ariele zanfei
"""

from sys import path as syspath

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
syspath.insert( 0, lib_dir )

from lib import pd, np, plt, logging, os, dt, mdates

def create_directory_tree(directory_path):
    # Check if the directory already exists
    if not os.path.exists(directory_path):
        # Create the directory and its parents if they don't exist
        os.makedirs(directory_path)

class Optimisation_functions():
    
    def __init__(self, date, serbatoio, forecast_data_filename, real_data_filename, price_filename):
        # self.problem = problem        
        self.date = date
        self.serbatoio = serbatoio
        self.forecast_data_filename = forecast_data_filename
        self.real_data_filename = real_data_filename
        self.price_filename = price_filename
        # self.default_flow_const = default_flow_const

    """Funzione per fare il parsing dei dati idrologici """
    def parsing_idro(self):
        
        try :
            flow_in = pd.read_csv( self.forecast_data_filename, sep=',', engine='python' )
            flow_in.index = pd.to_datetime(flow_in['datetime'], format="%Y-%m-%d %H:%M:%S")
        except KeyError:
            raise

        flow_in.drop(columns=flow_in.columns[[0]], inplace=True)
        Q_in_val = flow_in['values'][flow_in.index.date == self.date.date()].values
        flow_in_df = pd.DataFrame(
            index=pd.date_range(self.date, periods=24, freq='H'), columns=['Q_in'])
        try:
            flow_in_df['Q_in']= Q_in_val
            constraint_Q = Q_in_val.mean()
        except ValueError as e:
            logging.error(f"No enough model data for today {self.date}: {e}")
            constraint_Q = np.nan

        # constraint su Q OUT
        try :
            flow_out = pd.read_csv( self.real_data_filename, sep=',', engine='python' )
            flow_out.index = pd.to_datetime(flow_out['datetime'], format="%Y-%m-%d %H:%M:%S")
        except KeyError:
            raise

        flow_out.drop(columns=flow_out.columns[[0]], inplace=True)
        Q_out_val = flow_out['values'][flow_out.index.date == self.date].values
        flow_out_df = pd.DataFrame(index=pd.date_range(self.date, periods=24, freq='H'),
                                columns=['Q_in_real'])
        try:
            flow_out_df['Q_in_real']= Q_out_val
        except ValueError as e:
            logging.error(f"No enough reference data for today {self.date}: {e}")       
            flow_out_df = None

        return flow_in_df, constraint_Q, flow_out_df
    
    """Funzione per fare il parsing dei prezzi"""
    def parsing_economics(self):
        try:
            econ = pd.read_csv(self.price_filename, sep=',', engine='python')
            econ.index = pd.to_datetime(econ['datetime'], format="%Y-%m-%d %H:%M:%S")
            econ.drop(columns=econ.columns[[0]], inplace=True) 
        except:
            raise
        return econ

    """Mi serve una funzione che mi estragga le migliori dal fronte, sia
    le Q_out, ma anche i tiranti. Nella prima parte faccio una selezione delle
    soluzioni della frontiera di pareto. Nella seconda parte ricavo i tiranti
    orari corrispondenti alle soluzioni estratte nella prima parte. L'output
    di questa funzione sarà V_out, ovvero il volume iniziale per la simulazione
    successiva"""
    def solution_selector(self, solutions, algorithm):
        solution = list()
        self.max_f1, self.best = pd.DataFrame(), pd.DataFrame()
        self.max_f1 = solutions[solutions[solutions.columns[-1]] == 
                           solutions[solutions.columns[-1]].max()]
        # per evitare di avere più soluzioni analoghe
        self.max_f1 = self.max_f1[self.max_f1.index==self.max_f1.index[0]]
        # La migliore è quella che soddifa il costraint alla perfezione
        constr = algorithm.problem.Q_out_constr*24
        sum_Q = solutions[solutions.columns[:23]].T.sum()
        difference= abs(sum_Q-constr)
        cond = (difference).min()
        self.best = solutions[solutions.index == difference.index[difference == cond][0]]
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
        # La portata entrante reale però non è quella forecast! Il volume lo 
        # aggiorno sulle turbinate ottimizzate e le portate entranti reali  
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
            for i in range(solutions.shape[1]-1):
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
    
    def __init__(self, simulation_name): 
        self.simulation_name = simulation_name
        self.output_list = list()
        
    def fill(self, df_output):
        self.output_list.append(df_output)
        
    def list_return(self):
        return self.output_list        
        
    def saver(self, date, output_path=None):
        
        self.df = pd.concat(self.output_list)
        self.string = date.strftime("%Y%m%d")
        if output_path is not None:
            self.output_filepath = f"{output_path}{self.simulation_name}_{self.string}.csv"
            create_directory_tree(output_path)
        else:
            self.output_filepath = self.name +'.csv'
        self.df.to_csv(self.output_filepath, sep=';', encoding='utf-8')
         
    """funzione per fare il plot di piu giorni consecutivi"""    
    def complete_plotter(self, n_days, output=None, output_path='./'):
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
        plt.savefig(output_path+'4.png', dpi=300)
        # plt.show()
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
           
         
           
           
        
        
        
        
        