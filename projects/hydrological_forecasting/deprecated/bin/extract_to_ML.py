#!/usr/bin/env python
# coding: utf-8

# In[ ]:


wdir = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/"


# In[ ]:


# IMPORTs
import sys
import os

# to link the lib in py scripts as well
os.chdir(wdir)
sys.path.insert(0, os.path.join(os.path.abspath(os.getcwd()), 'lib'))
from lib import *


# In[ ]:


import glob
from dateutil import tz


# In[ ]:


def append_data(current_data, additional_data, col_name):

    current_data = current_data.reset_index()
    additional_data = additional_data.reset_index()

    current_data = current_data.rename(columns={'values' : '{col_name}'.format(col_name=col_name)})
    current_data = pd.concat([current_data[current_data['datetime'].isin(
        additional_data['datetime']) == False], additional_data], ignore_index=True)

    # current_data = current_data.drop(columns=['values'])

    current_data = current_data.set_index('datetime')
    current_data = current_data[current_data.index.notnull()]

    return current_data


# In[ ]:


# SETUP
# basins = ['passirio', 'plan']
basins = ['plan']
variables = ['temperature', 'precipitation']

init_forecasting_hour = 10
lead_hours = 38
lag_hours = 24*7

ensemble_cardinality = 20

start_date_str = '20210615T00:00:00'
end_date_str = '20211016T00:00:00'
timezone_str = 'Europe/Rome'
timezone = ZoneInfo(timezone_str)


# In[ ]:


start_date = dt.datetime.strptime(start_date_str, '%Y%m%dT%H:%M:%S').replace(tzinfo=ZoneInfo(timezone_str))
end_date = dt.datetime.strptime(end_date_str, '%Y%m%dT%H:%M:%S').replace(tzinfo=ZoneInfo(timezone_str))

dates = [start_date + dt.timedelta(days=x)
         for x in range(0, (end_date-start_date).days)]


# In[ ]:


# To create the input for the machine learning models - to read Andrea files
# for each day we create here a timeseries with the 7 days lag before the init_hour [9AM] and the forecasting for the following 38 hours

for variable in variables:

    print(variable)

    for basin in basins:

        print(basin)

        obs_data_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/observed/{basin}/{variable}/daily/obs/mean/"
        # fct_data_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/forecast/icon-d2-eps_45h/postprocess_test/{basin}/{variable}/ensemble/"
        fct_data_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/forecast/icon-d2-eps_45h/postprocessed/{basin}/{variable}/unbias/ensemble/"
        output_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/output/{basin}/{variable}/ensemble/"

        obs_data_path = obs_data_path.format(
            basin=basin, variable=variable)
        fct_data_path = fct_data_path.format(
            basin=basin, variable=variable)
        output_path = output_path.format(
            basin=basin, variable=variable)
        mkNestedDir(output_path)

        stations = glob.glob(obs_data_path + '*.csv')
        forecasts = glob.glob(fct_data_path + '*.csv')
        forecast_dates = [os.path.basename(d)[:-4] for d in forecasts]

        for date in dates:
            # print(date)

            date_as_str = dt.datetime.strftime(date, '%Y%m%d')
            station_data_path = obs_data_path + date_as_str + ".csv"

            station_data = pd.read_csv(station_data_path, parse_dates=[0], header=0, sep=';')
            station_data.set_index('datetime', inplace=True)

            infer_dst = np.array([False] * station_data.shape[0])
            station_data = station_data.tz_localize(timezone_str, ambiguous=infer_dst)

            if variable == 'precipitation':
                station_data = station_data.resample("H").sum()
            elif variable == 'temperature':
                station_data = station_data.resample("H").mean()
            elif variable == 'streamflow':
                station_data = station_data.resample("H").mean()
            else:
                print('WRONG variable')

            start_datetime = date + dt.timedelta(hours=int(init_forecasting_hour))
            start_datetime_wlag = start_datetime - dt.timedelta(hours=lag_hours)
            end_datetime = start_datetime + dt.timedelta(hours=lead_hours)

            if date_as_str in forecast_dates:

                current_fct_data = fct_data_path + date_as_str + ".csv"

                fct_data = pd.read_csv(
                    current_fct_data, parse_dates=[0], header=0, index_col=0)
                fct_data.index.name = "datetime"

                infer_dst = np.array([False] * fct_data.shape[0])
                fct_data = fct_data.tz_localize(timezone_str, ambiguous=infer_dst)

                fct_data = fct_data[start_datetime:end_datetime]

                fct_tmp = pd.DataFrame( index=fct_data.index )
                for en in range(1,ensemble_cardinality+1):
                    try:
                        fct_tmp[str(en).zfill(3)] = fct_data[str(en)]
                    except:
                        fct_tmp[str(en).zfill(3)] = fct_data[str(en).zfill(3)]
                fct_data = fct_tmp

                # fct_data = apply_bias_correction( variable, fct_data, fct_data_path, obs_data_path, dates, date )
                
                ensemble_current_data = pd.DataFrame( index=station_data.index, columns=[str(i).zfill(3) for i in range(1,ensemble_cardinality+1)] )

                for i in range(1,ensemble_cardinality+1):
                    ens_str = str(i).zfill(3)
                    
                    tmp = append_data(station_data, fct_data[ens_str], ens_str)
                    ensemble_current_data[ens_str] = [round(d[0],2) for d in tmp.values]
            else:
                ### fulfill with observed
                ensemble_current_data = pd.DataFrame( index=station_data.index, columns=[str(i).zfill(3) for i in range(1,ensemble_cardinality+1)] )

                for i in range(1,ensemble_cardinality+1):
                    ens_str = str(i).zfill(3) 
                    ensemble_current_data[ens_str] = [round(d[0],2) for d in station_data.values]

            ensemble_current_data.index = [ dt.datetime.strftime(i, format='%Y-%m-%d %H:%M:%S') for i in ensemble_current_data.index ]
            ensemble_current_data.index.name = "datetime"
            
            ensemble_current_data.to_csv( output_path + date_as_str + '.csv', sep=';')


# In[ ]:


# # To create the input for the machine learning models
# # for each day we create here a timeseries with the 7 days lag before the init_hour [9AM] and the forecasting for the following 38 hours

# for variable in variables:

#     print(variable)

#     for basin in basins:

#         print(basin)

#         obs_data_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/observed/{basin}/{variable}/daily/obs/mean/"
#         # fct_data_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/forecast/icon-d2-eps_45h/postprocess_test/{basin}/{variable}/ensemble/"
#         fct_data_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/forecast/icon-d2-eps_45h/postprocess_2022/{basin}/{variable}/unbias/ensemble/"
#         output_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/output2/{basin}/{variable}/ensemble/"

#         obs_data_path = obs_data_path.format(
#             basin=basin, variable=variable)
#         fct_data_path = fct_data_path.format(
#             basin=basin, variable=variable)
#         output_path = output_path.format(
#             basin=basin, variable=variable)
#         mkNestedDir(output_path)

#         stations = glob.glob(obs_data_path + '*.csv')
#         forecasts = glob.glob(fct_data_path + '*/')

#         for forecast in forecasts:

#             forecast_dirs = glob.glob( forecast + '*.csv' )
#             points = [d.split('/')[-2] for d in forecast_dirs]
#             forecast_dates = [os.path.basename(d)[:-4] for d in forecast_dirs]

#             for point in points:
#                 for date in dates:

#                     # print(date)

#                     date_as_str = dt.datetime.strftime(date, '%Y%m%d')
#                     # print(date_as_str)

#                     station_data_path = obs_data_path + date_as_str + ".csv"

#                     station_data = pd.read_csv(station_data_path, parse_dates=[0], header=0, sep=';')
#                     station_data.set_index('datetime', inplace=True)

#                     infer_dst = np.array([False] * station_data.shape[0])
#                     station_data = station_data.tz_localize(timezone_str, ambiguous=infer_dst)

#                     if variable == 'precipitation':
#                         station_data = station_data.resample("H").sum()
#                     elif variable == 'temperature':
#                         station_data = station_data.resample("H").mean()
#                     elif variable == 'streamflow':
#                         station_data = station_data.resample("H").mean()
#                     else:
#                         print('WRONG variable')
                    
#                     # print(station_data)

#                     start_datetime = date + dt.timedelta(hours=int(init_forecasting_hour))
#                     # print( start_datetime )
#                     start_datetime_wlag = start_datetime - dt.timedelta(hours=lag_hours)
#                     # print( start_datetime_wlag )
#                     end_datetime = start_datetime + dt.timedelta(hours=lead_hours)
#                     # print( end_datetime )

#                     # current_obs_data = station_data[start_datetime_wlag:end_datetime]

#                     # current_obs_data.plot()
                    
#                     # print(current_obs_data)
#                     # print(dt.datetime.strftime(start_datetime_wlag, format='%Y-%m-%d %H:%M:%s'))
#                     # print(dt.datetime.strftime(end_datetime, format='%Y-%m-%d %H:%M:%s'))

#                     if date_as_str in forecast_dates:

#                         # print("OK")

#                         current_fct_data = fct_data_path + point + '/' + date_as_str + ".csv"
#                         # print( current_fct_data )

#                         fct_data = pd.read_csv(
#                             current_fct_data, parse_dates=[0], header=0, sep=';', index_col=0)
#                         fct_data.index.name = "datetime"

#                         infer_dst = np.array([False] * fct_data.shape[0])
#                         fct_data = fct_data.tz_localize(timezone_str, ambiguous=infer_dst)

#                         fct_data = fct_data[start_datetime:end_datetime]

#                         # fct_data = apply_bias_correction( variable, fct_data, fct_data_path, obs_data_path, dates, date )
                        
#                         ensemble_current_data = pd.DataFrame( index=station_data.index, columns=[str(i).zfill(3) for i in range(1,ensemble_cardinality+1)] )

#                         for i in range(1,ensemble_cardinality+1):
#                             ens_str = str(i).zfill(3)
                          
#                             tmp = append_data(station_data, fct_data[ens_str], ens_str)
#                             ensemble_current_data[ens_str] = tmp.values
#                     else:
#                         ### fulfill with observed
#                         ensemble_current_data = pd.DataFrame( index=station_data.index, columns=[str(i).zfill(3) for i in range(1,ensemble_cardinality+1)] )

#                         for i in range(1,ensemble_cardinality+1):
#                             ens_str = str(i).zfill(3) 
#                             ensemble_current_data[ens_str] = station_data.values

#                 ensemble_current_data.index = [ dt.datetime.strftime(i, format='%Y-%m-%d %H:%M:%S') for i in ensemble_current_data.index ]
#                 ensemble_current_data.index.name = "datetime"
                
#                 current_outputpath = output_path + point + '/'
#                 mkNestedDir(current_outputpath)

#                 ensemble_current_data.to_csv( current_outputpath + dt.datetime.strftime(start_datetime, format='%Y%m%d') + '.csv', sep=';')


# In[ ]:


ensemble_number = 20
output_path = "/media/windows/projects/hydro_forecasting/machine_learning/data/output/{basin}/{variable}/ensemble/"


# In[ ]:


for basin in basins:
    for variable in variables:
        print(variable)
        for date in dates:
            date_as_str = dt.datetime.strftime(date, '%Y%m%d')
            print(date_as_str)

            output_path = output_path.format(
                basin=basin, variable=variable)
            mkNestedDir(output_path)

            fct_data = pd.read_csv(output_path + date_as_str + '.csv', sep=';')

            plots = []
            for k in range(1, ensemble_number+1):

                k = str(k).zfill(3)

                plt_conf = {}
                # plt_conf["label"] = k
                plots.append((fct_data[k], plt_conf))

            import matplotlib.dates as mdates
            x_major_formatter = mdates.DateFormatter('%dT%H')

            outfile = output_path + 'plots/' + date_as_str + "." + output_format
            mkNestedDir(os.path.dirname(outfile))
            createPlot(plots, "Time $[hour]$", 'Prec. [$mm/hour$]', outfile,
                       x_major_formatter=x_major_formatter, my_dpi=50, height=80)

            outfile_hd = output_path + 'plots/HD/' + date_as_str + "." + output_format
            mkNestedDir(os.path.dirname(outfile_hd))
            createPlot(plots, "Time $[hour]$", 'Prec. [$mm/hour$]', outfile_hd,
                       x_major_formatter=x_major_formatter, my_dpi=600, height=80)


# In[ ]:




