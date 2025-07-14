#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )


# In[2]:


from lib import *


# In[3]:


wdir = "/media/windows/projects/icon-evaluation/hydro_modeling/"

basin = "passirio"

timezone_str = 'Europe/Rome'

gauge_station = '58' ### merano
gauge_measure = '118'


# In[4]:


start_date_str = '20210728T00:00:00'
end_date_str = '20211017T00:00:00'

start_date = dt.datetime.strptime(start_date_str, '%Y%m%dT%H:%M:%S')
end_date = dt.datetime.strptime(end_date_str, '%Y%m%dT%H:%M:%S')

dates = [ start_date + dt.timedelta(days=x) for x in range(0, (end_date-start_date).days) ]
fct_dates = [ start_date + dt.timedelta(hours=x) for x in range(0, (end_date-start_date).days*24) ]

output_dt_format = '%Y-%m-%d %H:%M:%S'


# In[5]:


calibration_lag_hours = 1*360*24
wu_days = 360
da_days = 10
forecasting_lead_time = 24


# In[6]:


bias_table = pd.DataFrame(columns=['fct', 'hydro'])

for date in dates:

    print(date)
    str_date = dt.datetime.strftime(date, format='%Y%m%d')

    current_start_date = dt.datetime.strftime(
        date - dt.timedelta(days=da_days*2), output_dt_format)
    current_end_date = dt.datetime.strftime(
        date + dt.timedelta(hours=forecasting_lead_time), output_dt_format)

    streamflow_df = pd.DataFrame()

    ### measured ###
    obs_flow = pd.read_csv(wdir + basin + "/meteo/streamflow/" + gauge_measure +
                            ".txt", skiprows=5, header=None, parse_dates=True, index_col=0)
    obs_flow.index.name = 'datetime'
    # obs_flow = obs_flow[current_start_date:current_end_date]

    streamflow_df['measured'] = obs_flow[obs_flow[1] > 0][1]

    ### forward ###
    obs_flow_filepath = wdir + basin + "/OUTPUT/FORWARD/output_1/"

    t = pd.read_csv(obs_flow_filepath + 'out_flow.txt')
    t.rename(columns={'date':'datetime'}, inplace=True)
    t = read_timeseries_pd( t, input_dt_format='%Y-%m-%d %H:%M' )

    # streamflow_df['forward'] = pd.to_numeric( t[current_start_date:current_end_date]['58'] )
    # streamflow_df['forward'] = t[current_start_date:current_end_date]['58']
    streamflow_df['forward'] = t['58']
    streamflow_df.reset_index(inplace=True)

    obs_flow_filepath = wdir + basin + "/OUTPUT_KR/" +         str_date + "/FORECASTING/Nens_20/output_1/"

    try:

        ### DA ###
        obs_flow = pd.read_csv(obs_flow_filepath + 'DA_out_ENSEMBLE_mean_flow.txt',
                            skiprows=1, header=None)
        obs_flow = obs_flow.rename(columns={0: 'datetime'})
        obs_flow = read_timeseries_pd(obs_flow, input_dt_format='%Y-%m-%d %H:%M')
        obs_flow = obs_flow[[int(gauge_station)]]
        obs_flow = obs_flow.rename(columns={int(gauge_station): 'DA'})

        # obs_flow = obs_flow[current_start_date:current_end_date]

        obs_flow.reset_index(inplace=True)
        streamflow_df = streamflow_df.merge(obs_flow, on='datetime', how='outer')
        del [obs_flow]

        # ### deterministic ###
        # obs_flow = pd.read_csv(obs_flow_filepath + 'out_flow.txt',
        #                     skiprows=1, header=None)
        # obs_flow = obs_flow.rename(columns={0: 'datetime'})
        # obs_flow = read_timeseries_pd(obs_flow, input_dt_format='%Y-%m-%d %H:%M')
        # obs_flow = obs_flow[[int(gauge_station)]]
        # obs_flow = obs_flow.rename(columns={int(gauge_station): 'deterministic'})

        # obs_flow = obs_flow[current_start_date:current_end_date]

        # obs_flow.reset_index(inplace=True)
        # streamflow_df = streamflow_df.merge(obs_flow, on='datetime', how='outer')
        # del [obs_flow]

        ### forecast ###
        obs_flow = pd.read_csv(obs_flow_filepath + 'out_ENSEMBLE_mean_flow.txt',
                            skiprows=1, header=None, parse_dates=True, index_col=0)
        obs_flow.index.name = 'datetime'
        obs_flow = obs_flow[[int(gauge_station)]]
        obs_flow = obs_flow.rename(columns={int(gauge_station): 'forecast'})

        # obs_flow = obs_flow[current_start_date:current_end_date]

        obs_flow.reset_index(inplace=True)
        streamflow_df = streamflow_df.merge(obs_flow, on='datetime', how='outer')
        del [obs_flow]

    except FileNotFoundError as e:
        print(e)
        continue
    except:
        raise
    
    streamflow_df.set_index('datetime', inplace=True)
    streamflow_df = streamflow_df[current_start_date:current_end_date]

    plots = []

    plt_conf = {}
    plt_conf["label"] = 'Observed'
    plt_conf["color"] = '#fdb863'
    plots.append( (streamflow_df['measured'], plt_conf) )

    plt_conf = {}
    plt_conf["label"] = 'DA'
    plt_conf["color"] = '#e66101'
    plots.append( (streamflow_df['DA'], plt_conf) )

    plt_conf = {}
    plt_conf["label"] = 'forward'
    plt_conf["color"] = '#8078bc'
    plots.append( (streamflow_df['forward'], plt_conf) )

    plt_conf = {}
    plt_conf["label"] = 'forecast'
    plt_conf["color"] = '#5e3c99'
    plots.append( (streamflow_df['forecast'], plt_conf) )

    import matplotlib.dates as mdates
    x_major_locator=mdates.YearLocator(month=10, day=1)
    x_major_formatter=mdates.DateFormatter('%m-%d')

    output_path_plots_HD = wdir + basin + "/OUTPUT_KR/plots_HD/"
    createPlot(plots,  "Time", "Streamflow $[m^3/s]$",
           output_path_plots_HD + str_date + "." + output_format, output_format=output_format,  x_major_formatter=x_major_formatter, my_dpi=600)

    output_path_plots = wdir + basin + "/OUTPUT_KR/plots/"
    createPlot(plots,  "Time", "Streamflow $[m^3/s]$",
           output_path_plots + str_date + "." + output_format, output_format=output_format,  x_major_formatter=x_major_formatter, my_dpi=50)

#     bias_table['fct'] = streamflow_df['ensemble'] - streamflow_df['measured']
#     ### hydrological model in deterministic run days
#     bias_table['hydro'] = streamflow_df['deterministic'] - streamflow_df['measured']

#     # if counter == 3:
#     #     break
#     # else:
#     #     counter = counter + 1

# createBoxPlot(fct_dataframe,  "Time $[hour]$", "Streamflow bias $[m^3/hour]$",
#               output_path_plots, period='H', output_format=output_format, my_dpi=600)


# In[ ]:


# streamflow_df.set_index('datetime', inplace=True)
streamflow_df.plot(figsize=(15,15))


# In[ ]:


# deterministic_data = bias_table['hydro'].dropna()


# In[ ]:


# bias_values = pd.DataFrame(index=[i for i in range(forecasting_lead_time)], columns=[
#                            i for i in range(int(len(deterministic_data)/forecasting_lead_time))])


# In[ ]:


# c = 0
# for t in deterministic_data.index:
#     try:
#         bias_values[c][t.hour] = deterministic_data[t]
#     except:
#         break
#     if t.hour+1 == bias_values.shape[0]:
#         c = c+1


# In[ ]:


# bias_mean_values = bias_values.mean(axis=1)


# In[ ]:


# fct_data = bias_table['fct'].dropna()


# In[ ]:


# c = 0
# for f in fct_data.index:
#     # print(deterministic_data.loc[f])
#     try:
#         fct_data.loc[f] = fct_data.loc[f] - bias_mean_values[f.hour]
#     except:
#         print('AAAAAAAAAAAAAAAH')
#         break

# streamflow_df['unbiased'] = fct_data


# In[ ]:


# deterministic_data = bias_table['hydro'].dropna()


# In[ ]:


# c = 0
# for f in deterministic_data.index:
#     # print(deterministic_data.loc[f])
#     try:
#         deterministic_data.loc[f] = deterministic_data.loc[f] - bias_mean_values[f.hour]
#     except:
#         print('AAAAAAAAAAAAAAAH')
#         break

# streamflow_df['unbiased_deterministic'] = deterministic_data


# In[ ]:


# streamflow_df.plot(figsize=(20,20))


# In[ ]:





# In[ ]:




