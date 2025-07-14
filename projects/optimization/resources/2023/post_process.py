# -*- coding: utf-8 -*-
"""
Created on Sat Nov 23 17:12:38 2019

@author: ariele
"""

"""Code developed to make the post-process of the optimization problem"""

import numpy as np
import pandas as pd
import datetime
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import seaborn


"""Functions"""
def import_case(case, date):
    Output = pd.read_csv('output/' + case + '/' + date + '.txt',sep=';',
                         engine='python')
    Output.index = pd.to_datetime(Output['Unnamed: 0'],
                                  format="%Y-%m-%d %H:%M:%S")
    Output.drop(columns=Output.columns[[0]], inplace=True) 
    return Output

"""La domanda che mi pongo è, considerato l'ottimizzazione nel momento in cui
io vado a prendere anche solo l'andamento dei prezzi io sono a posto, perchè
poi l'ottimizzatore nel scegliere le porte da turbinare va a selezzionare i 
picchi indipendentemente dal loro modulo. Quindi a mio avviso questo va 
considerato e vanno contfrontati sia gli andamenti sia i forecast veri e propri
Quindi una prima comparison puo essere:
    - Guadagno reale vs best guadagno
    - Guadagno previsto vs guadagno best
cosi nel primo vedo gli andamenti e nel secondo anche come ho previsto
i prezzi"""
def first_comparison(df_real, df_model):
    
    real_income = df_model['energy (MWh)']*df_real['prezzo (eur/MWh)']
    real_tot = real_income.sum()
    supposed_tot = df_model['ricavo (eur)'].sum()
    best_tot = df_real['ricavo (eur)'].sum()
    print('best possible income:                    ', best_tot.round(2),
          '\nreal income with optimized Qout:         ', real_tot.round(2),
          '\nsupposed income during the optimization: ', supposed_tot.round(2),'\n')
    print('best possible income:                    ', best_tot.round(2)/best_tot.round(2),
          '\nreal income with optimized Qout:         ', real_tot.round(2)/best_tot.round(2),
          '\nsupposed income during the optimization: ', supposed_tot.round(2)/best_tot.round(2),'\n')


#-----------------------------------------------------------------------------#
"""Main"""
df_econ_real = import_case('econ_real', '01_01_17')

df_autoarimax = import_case('autoarimax', '01_01_17')

df_benchmark = import_case('benchmark', '01_01_17')


first_comparison(df_econ_real, df_autoarimax)

first_comparison(df_econ_real, df_benchmark)
#-----------------------------------------------------------------------------#

deltaQ_autoarimax = pd.DataFrame(abs(df_autoarimax['Q out(m^3/s)']-df_econ_real['Q out(m^3/s)']),
                                 index = df_autoarimax.index)
deltaQ_benchmark  = pd.DataFrame(abs(df_benchmark['Q out(m^3/s)']-df_econ_real['Q out(m^3/s)']),
                                 index = df_autoarimax.index)
deltaQ_modelled  = pd.DataFrame((df_benchmark['Q out(m^3/s)']-df_autoarimax['Q out(m^3/s)']),
                                 index = df_autoarimax.index)
df_prices = pd.DataFrame(df_econ_real['prezzo (eur/MWh)'],index=df_econ_real.index)

df_average_hourly_autoarimax = df_autoarimax.groupby(df_autoarimax.index.hour).mean()
df_average_hourly_benchmark  = df_benchmark.groupby(df_benchmark.index.hour).mean()
df_average_hourly_econ_real = df_econ_real.groupby(df_econ_real.index.hour).mean()

#%% plot
start_date = '10-06-17'
n_days = 1
start_date = datetime.datetime.strptime(start_date, '%d-%m-%y')
end_date = start_date + datetime.timedelta(days = n_days)
fig, ax = plt.subplots(figsize=(18, 6))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_minor_locator(mdates.DayLocator(interval=10))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d')) 
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
#ax.plot(deltaQ_autoarimax[start_date:end_date]) #autoarimax
#ax.plot(deltaQ_benchmark[start_date:end_date])  #benchmark
#ax.plot(deltaQ_modelled[start_date:end_date])  #deltaQmodel
ax.plot(df_prices[start_date:end_date])         #price
ax.plot(df_autoarimax['prezzo (eur/MWh)'][start_date:end_date])
ax.plot(df_benchmark['prezzo (eur/MWh)'][start_date:end_date])
ax.plot(df_autoarimax['Q out(m^3/s)'][start_date:end_date])
ax.plot(df_benchmark['Q out(m^3/s)'][start_date:end_date])
ax.set_xlabel('hour')
ax.set_ylabel('Delta Qout(l/s)')
ax.legend(('real', 'autoarimax', 'bench'))

ax.grid(True)       
fig.autofmt_xdate()
#plt.savefig('10-06-17.png', dpi=300, bbox_inches='tight')
plt.show()

#%% boxplot delta Q
dataset = deltaQ_benchmark
dataset1 = dataset['Q out(m^3/s)']
fig, ax = plt.subplots(figsize=(18,6))
seaborn.boxplot(dataset.index.hour, dataset1, ax=ax)
ax.plot(df_average_hourly_econ_real['prezzo (eur/MWh)'])
ax.set(xlabel='time', ylabel='delta_Q')
#plt.savefig('box.png', dpi=300)
plt.show() 

#%% boxplot Prices
dataset = deltaQ_autoarimax
dataset1 = dataset['Q out(m^3/s)']
fig, ax = plt.subplots(figsize=(18,6))
seaborn.boxplot(dataset.index.hour, dataset1, ax=ax)
ax.plot(df_average_hourly_econ_real['prezzo (eur/MWh)'])
ax.set(xlabel='time', ylabel='delta_Q')
#plt.savefig('box.png', dpi=300)
plt.show() 

#%% plot average hourly among year
fig, ax = plt.subplots(figsize=(18, 6))
#ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) 
#ax.format_xdata = mdates.DateFormatter('%H:%M')
ax.plot(df_average_hourly_autoarimax['Q out(m^3/s)']) #autoarimax
ax.plot(df_average_hourly_benchmark['Q out(m^3/s)'])  #benchmark
ax.plot(df_average_hourly_econ_real['Q out(m^3/s)'])  #deltaQmodel
ax.plot(df_average_hourly_econ_real['prezzo (eur/MWh)'])         #price
ax.set_xlabel('hour')
ax.set_ylabel('Delta Qout(l/s)')
ax.legend(('autoarimax', 'benchmark', 'Q_real', 'price'))
ax.grid(True)       
fig.autofmt_xdate()
plt.show()

#%% plot average price hourly among year
fig, ax = plt.subplots(figsize=(18, 6))
#ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M')) 
#ax.format_xdata = mdates.DateFormatter('%H:%M')
ax.plot(df_average_hourly_autoarimax['prezzo (eur/MWh)']) #autoarimax
ax.plot(df_average_hourly_benchmark['prezzo (eur/MWh)'])  #benchmark
ax.plot(df_average_hourly_econ_real['prezzo (eur/MWh)'])         #price real
ax.set_xlabel('hour')
ax.set_ylabel('Delta Qout(l/s)')
ax.legend(('autoarimax price', 'benchmark', 'price real'))
ax.grid(True)       
fig.autofmt_xdate()
plt.show()





















