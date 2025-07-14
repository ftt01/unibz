#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )


# In[ ]:


from lib import *
from shutil import rmtree


# In[ ]:


wdir = '/media/windows/projects/icon-evaluation/'


# In[ ]:


# SETUP
in_basin = 'passirio'
variables = ['precipitation', 'temperature']

data_path = '/media/windows/projects/icon-evaluation/data/forecast/icon-d2-eps_45h/done/'
output_path = '/media/windows/projects/icon-evaluation/data/forecast/icon-d2-eps_45h/postprocessed_2/'

init_ref = '03'
lead_hours = 45
# lag_hours = 24*3

ensemble_number = 20
reorder_ensembles = False

# output_types = ['mean', 'median', 'first_quantile', 'third_quantile']
output_types = ['mean']

start_date_str = '20210615T00:00:00'
end_date_str = '20211017T00:00:00'
timezone_str = 'Europe/Rome'
timezone = ZoneInfo(timezone_str)

# station_id = 118 ## ID from extracted data GRIB2

# ## Passirio basin
out_basin = 'passirio'
# lat = ( 46.68, 46.945 )
# lon = ( 11.015, 11.38 )
# points = [255, 256,
#           234, 235, 236, 237, 238,
#           214, 215, 216, 217, 218, 219,
#           195, 196, 197, 198, 199, 200,
#           175, 176, 177, 178, 179, 180, 181,
#           156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168,
#           137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151,
#           116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132,
#           97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
#           77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
#           59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
#           41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52,
#           27, 28, 29, 30, 31, 32]

# ## Passirio station
# lat = ( , )
# lon = ( , )

# # # Plan basin
# out_basin = 'plan'
# # lat = (46.7145853, 46.8251415)
# # lon = (11.0198472, 11.117037)
# points = [137,
#           116, 117, 118, 119, 120,
#           97, 98, 99, 100, 101, 102,
#           77, 78, 79, 80, 81, 82,
#           59, 60, 61,
#           41]

# # Plan station
# lat = ( , )
# lon = ( , )


# In[ ]:


points_file = wdir + 'data/forecast/' + 'points3.csv'

points_df = pd.read_csv( points_file )


# In[ ]:


# basin = 'plan'
# variable = 'precipitation'
# output_type = 'mean'
# datetime_str = '20210816'

# output_file = output_path + basin + '/' + variable + \
#                         '/' + output_type + '/' + datetime_str + '.csv'

# extracted = pd.read_csv( output_file, parse_dates=['datetime'], sep=';' )
# extracted.set_index('datetime', inplace=True)

# extracted['2021-08-16 10:00:00':'2021-08-18 00:00:00'].plot()


# In[ ]:


# obs_file = "/media/windows/projects/hydrological_forecasting/machine_learning/data/observed/plan/precipitation/daily/obs/mean/" + datetime_str + ".csv"
# print(obs_file)

# obs = pd.read_csv( obs_file, parse_dates=['datetime'], sep=';' )
# obs.set_index( 'datetime', inplace=True )

# obs['2021-08-15 10:00:00':'2021-08-18 00:00:00'].plot()


# In[ ]:


# output_file = "/media/windows/projects/hydrological_forecasting/machine_learning/data/observed/plan/precipitation/daily/filled/mean/" + datetime_str + '.csv'

# filled = pd.read_csv( output_file, parse_dates=['datetime'], sep=';' )
# filled.set_index('datetime', inplace=True)

# filled['2021-08-15 10:00:00':'2021-08-18 00:00:00'].plot()


# In[ ]:


start_date = dt.datetime.strptime(start_date_str, '%Y%m%dT%H:%M:%S').replace(tzinfo=ZoneInfo(timezone_str))
end_date = dt.datetime.strptime(end_date_str, '%Y%m%dT%H:%M:%S').replace(tzinfo=ZoneInfo(timezone_str))

dates = [start_date + dt.timedelta(days=x)
         for x in range(0, (end_date-start_date).days + 1)]


# In[ ]:


dirs = glob.glob(data_path + '*/')
dirs


# In[ ]:


ensembles = range(1, ensemble_number + 1)


# In[ ]:


# for dir in dirs:

#     # for basin in in_basins:

#     for variable in variables:

#         print('Variable: ' + variable)

#         if variable == 'temperature':
#             var = 't_2m'
#         elif variable == 'precipitation':
#             var = 'tot_prec'

#         datetime_str = os.path.dirname(dir)[-8:]
#         print(datetime_str)

#         current_date = dt.datetime.strptime(datetime_str, '%Y%m%d')
#         current_date = current_date.astimezone(timezone)

#         if current_date in dates:

#             print('Date: ' + str(current_date) )

#             for output_type in output_types:

#                 print('Type: ' + output_type)

#                 current_dates = []
#                 values = []
#                 ensemble_index = [ str(e).zfill(3) for e in range(1,ensemble_number+1) ]
#                 fct_df = pd.DataFrame( index=ensemble_index )
#                 # fct_df_new = pd.DataFrame( index=ensemble_index )

#                 for n in range(1, lead_hours+1):

#                     current_dates.append(
#                             current_date + dt.timedelta(hours=(int(init_ref) + n)))

#                     n = str(n).zfill(3)

#                     # print( 'Lead time: ' + n )

#                     current_value = []
#                     ensemble_value = []
#                     for ensemble in ensembles:

#                         ensemble_str = str(ensemble).zfill(3)
#                         # print( "Ens. " + ensemble_str )
                        
#                         current_file = pd.read_csv(
#                             dir + n + '/' + in_basin + '/' + var + '/' + ensemble_str + '/' + 'output.csv', index_col=0)

#                         # current_file = current_file[current_file['lat'] <= lat[1]]
#                         # current_file = current_file[current_file['lat'] >= lat[0]]
#                         # current_file = current_file[current_file['lon'] <= lon[1]]
#                         # current_file = current_file[current_file['lon'] >= lon[0]]

#                         # evaluate the spatial mean of selected points
#                         # current_value = current_file.mean()
#                         if len(current_file) != 0:
#                             current_value = current_file[current_file['ID'] == station_id]['values'].values[0]
#                             # print( "Ens. " + ensemble_str + " : " + str(current_value) )
#                         else:
#                             print( "Ens. " + ensemble_str + " MISSING " )
#                             break

#                         if variable == 'temperature':
#                             ensemble_value.append(
#                                 current_value - 273.15)
#                         elif variable == 'precipitation':
#                             ensemble_value.append(
#                                 abs(current_value))
#                         else:
#                             print("ERROR: not a valid variable!")
                    
#                     fct_df[ n ] = ensemble_value
#                     # if variable == 'precipitation':
#                     #     # print( ensemble_value )
#                     #     ensemble_value = [round(ensemble_value[0], 2)] + [round(
#                     #         ensemble_value[i] - ensemble_value[i-1], 2) for i in range(1, len(ensemble_value))]

#                 if variable == 'precipitation':
#                     ### to solve cumulative problem
#                     for n in range(1, lead_hours+1):
                        
#                         lead_hour_str = str(n).zfill(3)
#                         if n-1 > 0:
#                             lead_hour_str_last = str(n-1).zfill(3)

#                             fct_df.sort_values(by=lead_hour_str_last, inplace=True)
#                             to_sort = fct_df[lead_hour_str]
#                             fct_df.drop(columns=lead_hour_str, inplace=True)
#                             fct_df[lead_hour_str] = to_sort.sort_values().values
                
#                     fct_df = fct_df.T
            
#                     for ens in ensembles:

#                         ens = str(ens).zfill(3)

#                         ens_value = fct_df[ens].values

#                         # print(ens_value)

#                         val = []
#                         val.append( ens_value[0] )
#                         for i in range(1, len(ens_value)):
#                             val.append( ens_value[i] - ens_value[i-1] )

#                         # print(tmp)

#                         fct_df[ens] = val
                
#                 else:
#                     fct_df = fct_df.T

#                 # define the type of output
#                 if output_type == 'mean':
#                     values = fct_df.mean(axis=1).values
#                 elif output_type == 'median':
#                     values = fct_df.median(axis=1).values
#                 elif output_type == 'first_quantile':
#                     values = fct_df.quantile(0.15,axis=1).values
#                 elif output_type == 'third_quantile':
#                     values = fct_df.quantile(0.85,axis=1).values
#                 else:
#                     print("ERROR: not a valid output_type!")

#                 data = pd.DataFrame(values, index=current_dates, columns=['values'])
#                 data.index.name = 'datetime'
#                 data.index = [ dt.datetime.strftime(i, format='%Y-%m-%d %H:%M:%S') for i in data.index ]

#                 # if variable == 'precipitation':
#                 #     data['values'] = [round(data.iloc[0]['values'], 2)] + [round(
#                 #         data.iloc[i]['values'] - data.iloc[i-1]['values'], 2) for i in range(1, len(data))]
            
#                 output_file = output_path + out_basin + '/' + variable + '/deterministic/' + output_type + '/' + datetime_str + '.csv'
#                 mkNestedDir(os.path.dirname(output_file))
#                 data.to_csv(output_file, sep=';')


# In[ ]:


# for dir in dirs:

#     print(dir)

#     # for basin in in_basins:

#     for variable in variables:

#         if variable == 'temperature':
#             var = 't_2m'
#         elif variable == 'precipitation':
#             var = 'tot_prec'

#         datetime_str = os.path.dirname(dir)[-8:]
#         print(datetime_str)

#         current_date = dt.datetime.strptime(datetime_str, '%Y%m%d')

#         if current_date in dates:

#             print('Variable: ' + variable)

#             # print( n )
#             plots = []
#             for output_type in output_types:

#                 print(output_type)

#                 # current_data = None

#                 output_file = output_path + out_basin + '/' + variable + \
#                     '/' + output_type + '/' + datetime_str + '.csv'
#                 current_data = pd.read_csv(
#                     output_file, parse_dates=True, index_col=0, sep=';')

#                 plt_conf = {}

#                 if output_type == 'mean':
#                     # plt_conf["color"] = '#5e3c99'
#                     continue
#                 elif output_type == 'median':
#                     plt_conf["color"] = '#e66101'
#                 elif output_type == 'first_quantile':
#                     plt_conf["color"] = '#fdb863'
#                 elif output_type == 'third_quantile':
#                     plt_conf["color"] = '#8078bc'
#                 else:
#                     print("ERROR: not a valid output_type!")

#                 plt_conf["label"] = output_type
#                 plots.append((current_data, plt_conf))

#             output_image = output_path + "img/deterministic/" + out_basin + "/" + variable + \
#                 '/' + datetime_str + "." + output_format
#             createPlot(plots,  "X $[m^3/day]$", "Y", output_image,
#                         output_format=output_format, my_dpi=50)

#             output_image_hd = output_path + "img_HD/deterministic/" + out_basin + "/" + \
#                 variable + '/' + datetime_str + "." + output_format
#             createPlot(plots,  "X $[m^3/day]$", "Y", output_image_hd,
#                         output_format=output_format, my_dpi=600)


# In[ ]:


### extract data for each point in the out_basin

# for each directory -> for each day of forecast
#   for each variable
#       if the current date is in the range of dates
#           for each point in the grid [from metadata]
#               for each lead hour
#                   for each ensemble
#                        read the output.csv and save to a dataframe fct_df
#                   if precipitation
#                       correct BUG
#                       evaluate cumulative
#               export forecast data as ensemble mean, median and 1st/3rd quantile for each point
#
## OUTPUT: csv file for each point, containing a timeseries of forecasting data
#

for dir in dirs:

    # for basin in in_basins:

    for variable in variables:

        print('Variable: ' + variable)

        if variable == 'temperature':
            var = 't_2m'
        elif variable == 'precipitation':
            var = 'tot_prec'

        datetime_str = os.path.dirname(dir)[-8:]
        print(datetime_str)

        current_date = dt.datetime.strptime(datetime_str, '%Y%m%d')
        current_date = current_date.astimezone(timezone)

        if current_date in dates:

            print('Date: ' + str(current_date) )

            for point in points_df['ID']:

                # print('Type: ' + output_type)

                current_dates = []
                values = []
                ensemble_index = [ str(e).zfill(3) for e in range(1,ensemble_number+1) ]
                fct_df = pd.DataFrame( index=ensemble_index )
                # fct_df_new = pd.DataFrame( index=ensemble_index )

                for n in range(1, lead_hours+1):

                    current_dates.append(
                            current_date + dt.timedelta(hours=(int(init_ref) + n)))

                    n = str(n).zfill(3)

                    # print( 'Lead time: ' + n )

                    current_value = []
                    ensemble_value = []
                    for ensemble in ensembles:

                        ensemble_str = str(ensemble).zfill(3)
                        # print( "Ens. " + ensemble_str )
                        
                        current_file = pd.read_csv(
                            dir + n + '/' + in_basin + '/' + var + '/' + ensemble_str + '/' + 'output.csv', index_col=0)

                        # current_file = current_file[current_file['lat'] <= lat[1]]
                        # current_file = current_file[current_file['lat'] >= lat[0]]
                        # current_file = current_file[current_file['lon'] <= lon[1]]
                        # current_file = current_file[current_file['lon'] >= lon[0]]

                        # evaluate the spatial mean of selected points
                        # current_value = current_file.mean()

                        current_value = current_file[current_file['ID'] == int(point)]['values'].values[0]
                        # print( "Ens. " + ensemble_str + " : " + str(current_value) )

                        if variable == 'temperature':
                            ensemble_value.append( round(
                                current_value - 273.15, 2) )
                        elif variable == 'precipitation':
                            ensemble_value.append( round(
                                abs(current_value), 2) )
                        else:
                            print("ERROR: not a valid variable!")
                    
                    fct_df[ n ] = ensemble_value

                if variable == 'precipitation':

                    ## to solve cumulative problem
                    # for n in range(1, lead_hours+1):
                        
                    #     lead_hour_str = str(n).zfill(3)
                    #     if n-1 > 0:
                    #         lead_hour_str_last = str(n-1).zfill(3)

                    #         fct_df.sort_values(by=lead_hour_str_last, inplace=True)
                    #         to_sort = fct_df[lead_hour_str]
                    #         fct_df.drop(columns=lead_hour_str, inplace=True)
                    #         fct_df[lead_hour_str] = to_sort.sort_values().values

                    ## to reorder the last based on the next to last
                    bug_hour = 16
                    lead_time_bug = str(bug_hour).zfill(3)
                    before_bug = str(bug_hour-1).zfill(3)
                    after_bug = str(bug_hour+1).zfill(3)
                    fct_df.drop(columns=lead_time_bug, inplace=True)
                    fct_df[lead_time_bug] = (fct_df[after_bug].values + fct_df[before_bug].values)/2

                    # bug_hour = 44
                    # next_to_bug = str(bug_hour-1).zfill(3)
                    # bug_lead_time = str(bug_hour).zfill(3)
                    # fct_df.sort_values(by=next_to_bug, inplace=True)
                    # to_sort = fct_df[bug_lead_time]
                    # fct_df.drop(columns=bug_lead_time, inplace=True)
                    # fct_df[bug_lead_time] = to_sort.sort_values().values

                    ## to reorder the last based on the next to last
                    next_to_last = str(lead_hours-1).zfill(3)
                    last_lead_time = str(lead_hours).zfill(3)
                    fct_df.sort_values(by=next_to_last, inplace=True)
                    to_sort = fct_df[last_lead_time]
                    fct_df.drop(columns=last_lead_time, inplace=True)
                    fct_df[last_lead_time] = to_sort.sort_values().values

                    fct_final = pd.DataFrame( index=ensemble_index )
                    for en in range(1,lead_hours+1):
                        fct_final[str(en).zfill(3)] = fct_df[str(en).zfill(3)]

                    fct_df = fct_final.T
            
                    for ens in ensembles:

                        ens = str(ens).zfill(3)

                        ens_value = fct_df[ens].values

                        # print(ens_value)

                        val = []
                        val.append( ens_value[0] )
                        for i in range(1, len(ens_value)):
                            val.append( ens_value[i] - ens_value[i-1] )

                        fct_df[ens] = [round(v, 2) for v in val]
                else:
                    fct_df = fct_df.T

                for output_type in output_types: # define the type of output
                    if output_type == 'mean':
                        fct_df_tmp = pd.DataFrame(fct_df.mean(axis=1).values, index=current_dates, columns=['values'])
                    elif output_type == 'median':
                        fct_df_tmp = pd.DataFrame(fct_df.median(axis=1).values, index=current_dates, columns=['values'])
                    elif output_type == 'first_quantile':
                        fct_df_tmp = pd.DataFrame(fct_df.quantile(0.15,axis=1).values, index=current_dates, columns=['values'])
                    elif output_type == 'third_quantile':
                        fct_df_tmp = pd.DataFrame(fct_df.quantile(0.85,axis=1).values, index=current_dates, columns=['values'])
                    else:
                        print("ERROR: not a valid output_type!")  

                    fct_df_tmp.index = current_dates
                    fct_df_tmp.index = [ dt.datetime.strftime(i, format='%Y-%m-%d %H:%M:%S') for i in fct_df_tmp.index ]
                    fct_df_tmp.index.name = "datetime"
                
                    output_file = output_path + out_basin + '/' + variable + '/deterministic/' + output_type + '/' + datetime_str + '/' + str(point) + '.csv'
                    mkNestedDir(os.path.dirname(output_file))
                    fct_df_tmp.to_csv(output_file, sep=';')


# In[ ]:


# fct_df


# In[ ]:


# for dir in dirs:

#     datetime_str = os.path.dirname(dir)[-8:]
#     print(datetime_str)

#     for variable in variables:

#         print('Variable: ' + variable)

#         point_matrix = pd.DataFrame()

#         for output_type in output_types: # define the type of output
#             for point in points:

#                 point_id = str(point).zfill(3)

#                 file_to_read = output_path + out_basin + '/' + variable + '/deterministic/' + output_type + '/' + point_id + '/' + datetime_str + '.csv'
#                 # print(file_to_read)
#                 current_file = pd.read_csv( file_to_read, parse_dates=[0], index_col=0, sep=';' )

#                 if len(point_matrix.index) == 0:
#                     point_matrix.index = current_file.index
#                 point_matrix[point_id] = [ round(v[0],2) for v in current_file.values ]

#             mean_matrix = pd.DataFrame(point_matrix.mean(axis=1).round(2), columns=['values'])

#             mean_matrix.index = [ dt.datetime.strftime(i, format='%Y-%m-%d %H:%M:%S') for i in mean_matrix.index ]
#             mean_matrix.index.name = 'datetime'
#             mean_matrix.columns = [str(m).zfill(3) for m in mean_matrix.columns]

#             output_file = output_path + out_basin + '/' + variable + '/deterministic/' + output_type + '/' + 'spatial_mean/' + datetime_str + '.csv'
#             mkNestedDir(os.path.dirname(output_file))
#             mean_matrix.to_csv(output_file, sep=';')


# In[ ]:


# for dir in dirs:

#     datetime_str = os.path.dirname(dir)[-8:]
#     print(datetime_str)

#     for variable in variables:

#         print('Variable: ' + variable)

#         point_matrix = pd.DataFrame()

#         for point in points:

#             point_id = str(point).zfill(3)

#             file_to_read = output_path + out_basin + '/' + variable + '/ensemble/' + point_id + '/' + datetime_str + '.csv'

#             current_file = pd.read_csv( file_to_read, parse_dates=[0], index_col=0, sep=';' )
                
#             tmp = []
#             for hour in range( lead_hours ):
#                 tmp.append( current_file.iloc[hour].to_list() )
            
#             point_matrix[point_id] = tmp
#         break
#     break


# In[ ]:


# point_matrix


# In[ ]:


# for dir in dirs:

#     datetime_str = os.path.dirname(dir)[-8:]
#     print(datetime_str)

#     for variable in variables:

#         print('Variable: ' + variable)

#         point_matrix = pd.DataFrame()

#         for point in points:

#             point_id = str(point).zfill(3)
#             # print(point_id)

#         # datetime_str = os.path.dirname(dir)[-8:]
#         # print(datetime_str)

#         # current_date = dt.datetime.strptime(datetime_str, '%Y%m%d')

#         # if current_date in dates:

#             # print('Date: ' + str(current_date) )

#             file_to_read = output_path + out_basin + '/' + variable + '/ensemble/' + point_id + '/' + datetime_str + '.csv'
#             # files_to_read = glob.glob(file_to_read)

#             current_file = pd.read_csv( file_to_read, parse_dates=[0], index_col=0, sep=';' )
#             # print(files_to_read)
#             # for f in files_to_read:

#                 # datetime_str = os.path.dirname(f)[-8:]
#                 # print(datetime_str)

#                 # current_file = pd.read_csv( f, parse_dates=True, index_col=0, sep=';' )
                
#             tmp = []
#             for hour in range( lead_hours ):
#                 tmp.append( current_file.iloc[hour].to_list() )
            
#             point_matrix[point_id] = tmp

#         point_matrix.index = current_file.index

#         mean_matrix = pd.DataFrame(index=[l for l in range(1,ensemble_number+1)])

#         for i in range(lead_hours):
#             ensemble_spatial_mean = []
#             for k in range(ensemble_number):
#                 ensemble_array = []
#                 for j in points:
#                     point_id = str(j).zfill(3)
#                     ensemble_array.append( point_matrix.iloc[i][point_id][k] )
#                 ensemble_spatial_mean.append( round(np.mean(ensemble_array), 2) )
#             mean_matrix[point_matrix.index[i]] = ensemble_spatial_mean

#         mean_matrix = mean_matrix.T
#         mean_matrix.index.name = 'datetime'
#         mean_matrix.index = [ dt.datetime.strftime(i, format='%Y-%m-%d %H:%M:%S') for i in mean_matrix.index ]

#         output_file = output_path + out_basin + '/' + variable + '/ensemble/spatial_mean/' + datetime_str + '.csv'
#         mkNestedDir(os.path.dirname(output_file))
#         mean_matrix.to_csv(output_file, sep=';')


# In[ ]:


# ### for saving into the DB

# for variable in variables:

#     print('Variable: ' + variable)

#     point_matrix = pd.DataFrame()

#     for point in points:

#         point_id = str(point).zfill(3)

#     # datetime_str = os.path.dirname(dir)[-8:]
#     # print(datetime_str)

#     # current_date = dt.datetime.strptime(datetime_str, '%Y%m%d')

#     # if current_date in dates:

#         # print('Date: ' + str(current_date) )

#         file_to_read = output_path + out_basin + '/' + variable + '/' + point_id + '/' + '*.csv'
#         files_to_read = glob.glob(file_to_read)

#         # print(files_to_read)
#         for f in files_to_read:

#             datetime_str = os.path.dirname(dir)[-8:]
#             # print(datetime_str)

#             current_file = pd.read_csv( f, parse_dates=True, index_col=0, sep=';' )
            
#             tmp = []
#             for hour in range( lead_hours ):
#                 tmp.append( current_file.iloc[hour].to_list() )
            
#             point_matrix[point_id] = tmp

#     point_matrix.index = current_file.index
#     break

