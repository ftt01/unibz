#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )


# In[ ]:


from lib import *


# In[ ]:


def write_stations(list_temperature, list_precipitation, list_streamflow, pathout):
    mkNestedDir(pathout)

    line_1 = "{num_temperature}                 ! number of T stations"
    line_2 = "{num_precipitation}               ! number of P stations"
    line_3 = "{num_streamflow}                  ! number of Q stations"
    line_T = "! T stations ID"
    line_P = "! P stations ID"
    line_Q = "! Q stations ID"

    line_1 = line_1.format(num_temperature=str(len(list_temperature)))
    line_2 = line_2.format(num_precipitation=str(len(list_precipitation)))
    line_3 = line_3.format(num_streamflow=str(len(list_streamflow)))

    file = open(pathout+"stations.txt","w+")
    file.writelines(line_1 + "\n")
    file.writelines(line_2 + "\n")
    file.writelines(line_3 + "\n")

    file.writelines(line_T + "\n")
    for t in list_temperature:
        file.writelines(str(t) + "\n")

    file.writelines(line_P + "\n")
    for p in list_precipitation:
        file.writelines(str(p) + "\n")

    file.writelines(line_Q + "\n")
    for q in list_streamflow:
        file.writelines(str(q) + "\n")


# In[ ]:


def write_configuration_file(run_mode, start_wu_date, end_wu_date, start_forecast_date, end_forecast_date,
                             parameters_file, basin, meteo_src, outlet_point, da_flag, wdir, pathout, kernel=True):
    mkNestedDir(pathout)

    if kernel != True:
        wwdir = wdir
        wdir = '../'
    else:
        wwdir = wdir

    line_1 = "{run_mode}                                ! run mode: 10 -> forecasting; 6 -> forward".format(
        run_mode=run_mode)
    line_2 = "1                                         ! ID run"
    line_3 = "0 				 		                ! ID previous run (useless)"
    line_4 = "100 			 		                    ! ID run meteorological fields (useless)"
    line_5 = "0  	 			 		                ! T forecasts correction: 1 -> yes; 0 -> no (useless)"
    line_6 = "0 				 		                ! T forecasts correction: 1 -> yes; 0 -> no (useless)"

    # warmup period
    line_9 = "{start_wu_date} 		                    ! start warm - up".format(
        start_wu_date=dt.datetime.strftime(start_wu_date, format='%Y-%m-%d_%H:%M'))
    line_10 = "{end_wu_date} 		                    ! begin D.A. (end warm-up)".format(
        end_wu_date=dt.datetime.strftime(end_wu_date, format='%Y-%m-%d_%H:%M'))

    # DA starts one hour later than line_10 and it ends at line_7

    # forecast period
    line_7 = "{start_forecast_date}                     ! end D.A. (start forecast/forward)".format(
        start_forecast_date=dt.datetime.strftime(start_forecast_date, format='%Y-%m-%d_%H:%M'))
    line_8 = "{end_forecast_date} 	                    ! end forecast/forward".format(
        end_forecast_date=dt.datetime.strftime(end_forecast_date, format='%Y-%m-%d_%H:%M'))

    # parameters to run the model
    line_11 = "\"{parameters_file}\" 	                    ! parameter file name".format(
        parameters_file=parameters_file)

    line_12 = "\"subcatchments.asc\"                     ! subcatchment raster file name"
    line_13 = "\"{wdir}{basin}/INPUT/\" 	                ! path of required input data".format(
        wdir=wdir, basin=basin)
    
    line_14 = "\"{wdir}{basin}/OUTPUT/{date}/\" 	         ! general folder of output data"
    if run_mode == '10':
        line_14 = line_14.format(wdir=wdir, basin=basin, date=dt.datetime.strftime(start_forecast_date, format='%Y%m%d'))
        out_path = "{wdir}{basin}/OUTPUT/{date}/".format(wdir=wwdir, basin=basin, date=dt.datetime.strftime(start_forecast_date, format='%Y%m%d'))
    else:
        line_14 = line_14.format(wdir=wdir, basin=basin, date='')
        out_path = "{wdir}{basin}/OUTPUT/".format(wdir=wwdir, basin=basin)

    mkNestedDir(out_path)

    line_15 = "\"{wdir}{basin}/meteo/\"                     ! path of required meteorological data (obs. and for.)".format(
        wdir=wdir, basin=basin)
    line_16 = "\"{meteo_src}\"			                ! observed meteo source".format(
        meteo_src=meteo_src)
    line_17 = "30.0					                    ! cellsize of subcatchment map"
    line_18 = "5.0						                ! mm SWE for SCA threshold"
    line_19 = "46.7 					                    ! mean latitude"
    line_20 = "2.0						                ! minimum number of meteorological station to perform interpolation"
    line_21 = "\"NASH\" 					                ! objective function for model calibration"
    line_22 = "1 						                ! number of calibration points"
    line_23 = "{outlet_point} 					        ! ID calibration point".format(
        outlet_point=outlet_point)
    line_24 = "{outlet_point} 					        ! ID outlet section".format(
        outlet_point=outlet_point)
    line_25 = "1 						                ! model type for base"
    line_26 = "{da_flag} 						        ! flag Data Assimilation: 1 -> active; 0 -> open-loop".format(
        da_flag=da_flag)

    file = open(pathout+"configuration_file.txt", "w+")
    [file.writelines(l + "\n") for l in [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11,
                                         line_12, line_13, line_14, line_15, line_16, line_17, line_18, line_19, line_20, line_21,
                                         line_22, line_23, line_24, line_25, line_26]]


# In[ ]:


def write_DA_settings(ensemble_size, pathout):
    mkNestedDir(pathout)

    line_1 = "{ensemble_size} 			! ensemble size".format(ensemble_size=ensemble_size)
    line_2 = "5 			            ! number of state variables"
    line_3 = "R C S G B 	            ! labels of state variables"
    line_4 = "0.00		                ! percentage error of observed Q "
    line_5 = "0.01			            ! percentage error for further perturbing observed streamflow"
    line_6 = "0.02		                ! threshold on precipitation perturbation"
    line_7 = "1.0			            ! shape gamma pdf for P perturbation (k or alpha)      --> USELESS"
    line_8 = "1.0			            ! scale gamma pdf for P perturbation (beta or 1/theta) --> USELESS"
    line_9 = "0. 			            ! dev. std. T perturbation"
    line_10 = "0			            ! additive inflation on soil water content (0: no; 1: yes)"
    line_11 = "0.00		                ! random noise for additive inflation"
    line_12 = "1	    	            ! time step between every analysis step"

    file = open( pathout + "DA_settings.txt", "w+")
    [file.writelines(l + "\n") for l in [line_1, line_2, line_3, line_4, line_5, line_6,
                                         line_7, line_8, line_9, line_10, line_11, line_12]]


# In[ ]:


wdir = "/media/windows/projects/icon-evaluation/"

variables = ['precipitation', 'temperature']
basin = "passirio"

timezone_str = 'Europe/Rome'

# kriging dates - NB: must be the same of the kriging simulation
start_kr_date_str = '2010-10-01 00:00:00'
end_kr_date_str = '2021-10-17 00:00:00'

start_kr_date = dt.datetime.strptime(
    start_kr_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo(timezone_str))
end_kr_date = dt.datetime.strptime(
    end_kr_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo(timezone_str))

dates = [start_kr_date + dt.timedelta(hours=x)
         for x in range(1, (end_kr_date-start_kr_date).days*24 + 1)]

# forecasting dates
start_fct_date_str = '2021-06-16 00:00:00'
end_fct_date_str = '2021-10-17 00:00:00'

start_fct_date = dt.datetime.strptime(
    start_fct_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo(timezone_str))
end_fct_date = dt.datetime.strptime(
    end_fct_date_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=ZoneInfo(timezone_str))

fct_dates = [start_fct_date + dt.timedelta(days=x)
             for x in range((end_fct_date-start_fct_date).days)]

output_dt_format = '%Y-%m-%d %H:%M:%S'

# setup simulations
run_mode = "10"

calibration_lag_hours = 1*300*24
wu_days = 360
da_days = 10
forecasting_lead_time = 24

da_flag = "1"
ensemble_size = 20

parameters_file = "hydro_parameters_GLUE_216.txt"
meteo_src = "GS"
outlet_points = ["118", "155"]

# ### ICHYMOD LINUX
# linux = True
# exe_path = "/home/daniele/documents/github/ftt01/phd/models/hydro_modeling/ichymod/core/release/"
# exe_name = "ichymod"

# ICHYMOD WINZOZ
linux = False
exe_path = "/home/daniele/documents/github/ftt01/phd/models/hydro_modeling/ichymod/core/VS_project/x64/Debug/"
exe_name = "ichymod.exe"


# In[ ]:


### stations metadata
## the grid is obtained in QGIS from the output.csv and the DTM elevation
metadata_data_path =  wdir + "data/GIS/grid.json"

grid_file = open(metadata_data_path)
grid_meta = json.load(grid_file)


# In[ ]:


list_temperature = []
list_precipitation = []

# for each element in the forecasting dates
#   - setup the dates to use the right windows of data
#   for each variable in variables
#       for each point of the grid
break_flag = False

for fct_date in fct_dates:

    current_start_fct_date = fct_date
    current_end_fct_date = current_start_fct_date +         dt.timedelta(hours=forecasting_lead_time)

    start_date = current_start_fct_date -         dt.timedelta(hours=calibration_lag_hours)
    end_date = current_end_fct_date

    start_date_str = dt.datetime.strftime( start_date, '%Y-%m-%d %H:%M:%S' )
    end_date_str = dt.datetime.strftime( end_date, '%Y-%m-%d %H:%M:%S' )

    start_wu_date = start_date - dt.timedelta(days=wu_days+da_days)
    end_wu_date = current_start_fct_date - dt.timedelta(days=da_days)

    if os.path.exists(wdir + "hydro_modeling/" +
                      basin + "/meteo/forecast/{date}/".format(
                          date=dt.datetime.strftime(fct_date, '%Y%m%d'))) == False:
        print("Forecast data missing: " + fct_weather_data_path)
        continue

    for variable in variables:

        print(variable)

        # input of forecasting data
        fct_weather_data_path = wdir + "hydro_modeling/" +             basin + "/meteo/forecast/{date}/{variable}/".format(
                variable=variable, date=dt.datetime.strftime(fct_date, '%Y%m%d'))
        output_weather_fct_path = wdir + "hydro_modeling/" +             basin + "/meteo/GS/forecasts/{variable}/".format(
                variable=variable)

        # simply copy the two directories from `extract_forecast.ipynb`
        copy_content(fct_weather_data_path, output_weather_fct_path)

        if variable == 'temperature':
            kr_corr = 'NO'
        elif variable == 'precipitation':
            kr_corr = 'DEUTSCH'

        st_list = []
        for g in grid_meta:

            output_weather_data_path = wdir + "hydro_modeling/" +                 basin + "/meteo/GS/observations/{variable}/"

            grid_weather_data_path = wdir +                 "kriging/output_passirio_stations_complete/{variable}/KR/{kr_type}/{kr_correction}/"

            internal_id = str(g['station_id'])
            east = str(g['east'])
            north = str(g['north'])
            elevation = str(g['elevation'])

            current_data_path = grid_weather_data_path.format(
                variable=variable, kr_type='OKED', kr_correction=kr_corr)
            # print(current_data_path)

            current_file = glob.glob(
                current_data_path + '*_{id}_*.csv'.format(id=internal_id))[0]
            current_data = pd.DataFrame(pd.read_csv(current_file, header=0)[
                                        internal_id].values, index=dates, columns=['values'])
            current_data.index.name = 'datetime'

            current_data = current_data[start_date:end_date]

            if variable == 'precipitation':
                current_data = current_data.resample('h').sum()
            elif variable == 'temperature':
                current_data = current_data.resample('h').mean()
            else:
                print('NOT A VALID VARIABLE!')
                continue

            current_data.index = [dt.datetime.strftime(
                i, format=output_dt_format) for i in current_data.index]
            df = current_data.to_csv(header=False).strip('\n').split('\n')
            data = '\r\n'.join(df)

            current_output_file = output_weather_data_path.format(
                variable=variable) + internal_id + ".txt"
            mkNestedDir(getPathFromFilepath(current_output_file))

            # ID,2.0
            # x,642993.5
            # y,5164882.0
            # z,630.0
            header = """ID,{id}\nx,{x}\ny,{y}\nz,{z}\n"""

            with open(current_output_file, 'w') as new:
                new.write(header.format(id=internal_id,
                                        x=east, y=north, z=elevation))
                new.write(data)

            # add station to station list
            if variable == 'precipitation':
                list_precipitation.append(internal_id)
            elif variable == 'temperature':
                list_temperature.append(internal_id)
            else:
                print('Not a valid variable!')
                continue

            ########################################################
            # FORECAST DATA - extraction on the forecasting period
            # output_weather_fct_path
            in_fct_file = output_weather_fct_path + '{id}.csv'.format(
                id=internal_id)
            out_fct_file = output_weather_fct_path + '{id}.txt'.format(
                id=internal_id)

            try:
                current_fct_data = read_timeseries_pd(pd.read_csv(in_fct_file, header=None, skiprows=4),
                                                      input_dt_format="%Y-%m-%d %H:%M:%S", datetime_col=0)
            except FileNotFoundError as err:
                print(err)
                continue
            except:
                raise

            current_fct_data.index.name = 'datetime'
            os.remove(in_fct_file)

            current_fct_data = current_fct_data[start_fct_date_str:end_fct_date_str]

            if variable == 'precipitation':
                current_fct_data = current_fct_data.resample('h').sum()
            elif variable == 'temperature':
                current_fct_data = current_fct_data.resample('h').mean()
            else:
                print('NOT A VALID VARIABLE!')
                continue

            current_fct_data.index = [dt.datetime.strftime(
                i, format=output_dt_format) for i in current_fct_data.index]
            df = current_fct_data.to_csv(header=False).strip('\n').split('\n')
            data = '\r\n'.join(df)

            # ID,2.0
            # x,642993.5
            # y,5164882.0
            # z,630.0
            header = """ID,{id}\nx,{x}\ny,{y}\nz,{z}\n"""

            with open(out_fct_file, 'w') as new:
                new.write(header.format(id=internal_id,
                                        x=east, y=north, z=elevation))
                new.write(data)

            # add station to station list
            if variable == 'precipitation':
                list_precipitation.append(internal_id)
            elif variable == 'temperature':
                list_temperature.append(internal_id)
            else:
                print('Not a valid variable!')
                continue

    streamflow_data_path = wdir + "kriging/data/" + basin + "/GS/streamflow/"
    output_streamflow_data_path = wdir +         "hydro_modeling/" + basin + "/meteo/streamflow/"

    streamflow_files = glob.glob(streamflow_data_path + '*.txt')

    for el in streamflow_files:
        id = str(os.path.basename(el[:-4]))
        if id in outlet_points:

            # collect matadata
            current_metadata = pd.read_csv(el, header=0)[0:4]
            x = current_metadata[id][0]
            y = current_metadata[id][1]
            z = current_metadata[id][2]
            area = current_metadata[id][3]

            # collect streamflow data
            current_data = pd.read_csv(el, skiprows=5, index_col=0, parse_dates=True, header=None,
                                       names=['datetime', 'values'])

            current_data = current_data[start_date:end_date]
            current_data['values'] = current_data['values'].replace(
                np.nan, -999.0)

            current_data.index = [dt.datetime.strftime(
                i, format=output_dt_format) for i in current_data.index]

            df = current_data.to_csv(header=False).strip('\n').split('\n')
            data = '\r\n'.join(df)

            # ID,2.0
            # x,642993.5
            # y,5164882.0
            # z,630.0
            # area,-999.0
            header = """ID,{id}\nx,{x}\ny,{y}\nz,{z}\narea,{area}\n"""

            mkNestedDir(output_streamflow_data_path)
            with open(output_streamflow_data_path + os.path.basename(el[:-4]) + '.txt', 'w') as new:
                new.write(header.format(id=id,
                                        x=x, y=y, z=z, area=area))
                new.write(data)

    write_stations(list_temperature, list_precipitation,
                   outlet_points, wdir + "hydro_modeling/" + basin + "/INPUT/")

    ##################################################################

    input_weather_data_path = wdir + "hydro_modeling/" +         basin + "/meteo/GS/observations/"
    output_weather_data_path = wdir + "hydro_modeling/" + basin + "/meteo/GS/forecasts/"

    # grid_weather_data_path = wdir + "kriging/output_passirio_stations_complete/{variable}/KR/{kr_type}/{kr_correction}/"

    # stations metadata
    # the grid is obtained in QGIS from the output.csv and the DTM elevation
    metadata_data_path = wdir + "data/GIS/grid.json"

    grid_file = open(metadata_data_path)
    grid_meta = json.load(grid_file)

    list_temperature = []
    list_precipitation = []

    for variable in variables:

        print(variable)

        st_list = []
        for g in grid_meta:

            internal_id = str(g['station_id'])
            east = str(g['east'])
            north = str(g['north'])
            elevation = str(g['elevation'])

            # current_data_path = grid_weather_data_path.format(variable=variable, kr_type='OKED', kr_correction=kr_corr)
            # # print(current_data_path)
            current_input_weather_data_path = input_weather_data_path + variable + "/"

            current_file = glob.glob(
                current_input_weather_data_path + '{id}.txt'.format(id=internal_id))[0]
            current_data = pd.read_csv(current_file, header=None, skiprows=4,
                                       parse_dates=True, index_col=0, names=['datetime', 'values'])
            try:
                current_data = current_data.tz_localize(
                    timezone_str, ambiguous='infer', nonexistent='NaT')
            except:
                current_data = current_data.tz_localize(
                    timezone_str, ambiguous=True, nonexistent='NaT')

            current_data = current_data[current_start_fct_date:current_end_fct_date]

            if variable == 'precipitation':
                current_data = current_data.resample('h').sum()
            elif variable == 'temperature':
                current_data = current_data.resample('h').mean()
            else:
                print('NOT A VALID VARIABLE!')
                continue

            current_data.index = [dt.datetime.strftime(
                i, format=output_dt_format) for i in current_data.index]
            df = current_data.to_csv(header=False).strip('\n').split('\n')
            data = '\r\n'.join(df)

            current_output_file = output_weather_data_path +                 variable + "/" + internal_id + ".txt"
            mkNestedDir(getPathFromFilepath(current_output_file))

            # ID,2.0
            # x,642993.5
            # y,5164882.0
            # z,630.0
            header = """ID,{id}\nx,{x}\ny,{y}\nz,{z}\n"""

            with open(current_output_file, 'w') as new:
                new.write(header.format(id=internal_id,
                                        x=east, y=north, z=elevation))
                new.write(data)

            # add station to station list
            if variable == 'precipitation':
                list_precipitation.append(internal_id)
            elif variable == 'temperature':
                list_temperature.append(internal_id)
            else:
                print('NOT A VALID VARIABLE!')
                continue

    ##################################################################

    write_configuration_file(run_mode, start_wu_date, end_wu_date, current_start_fct_date, current_end_fct_date,
                             parameters_file, basin, meteo_src, outlet_points[
                                 0], da_flag, wdir + "hydro_modeling/",
                             wdir + "hydro_modeling/" + basin + "/INPUT/", kernel=linux)

    write_DA_settings(ensemble_size, wdir +
                      "hydro_modeling/" + basin + "/INPUT/")

    # RUN THE MODEL
    os.chdir(wdir + "hydro_modeling/" + basin + "/")
    p = subprocess.Popen(exe_path + exe_name,
                         stdin=subprocess.PIPE, shell=True)
    p.communicate(input='\n'.encode())


# In[ ]:


# streamflow_data_path = wdir + "kriging/data/" + basin + "/GS/streamflow/"
# output_streamflow_data_path = wdir + "hydro_modeling/" + basin + "/meteo/streamflowDA/"

# list_streamflow = ['118','155']


# In[ ]:


# streamflow_files = glob.glob(streamflow_data_path + '*.txt')

# for el in streamflow_files:
#     id = str(os.path.basename(el[:-4]))
#     if id in list_streamflow:

#         ### collect matadata
#         current_metadata = pd.read_csv(el, header=0)[0:4]
#         x = current_metadata[id][0]
#         y = current_metadata[id][1]
#         z = current_metadata[id][2]
#         area = current_metadata[id][3]

#         ### collect streamflow data
#         current_data = pd.read_csv(el, skiprows=5, index_col=0, parse_dates=True, header=None,
#                                 names=['datetime', 'values'])

#         current_data = current_data[start_date:end_date]
#         current_data['values'] = current_data['values'].replace(np.nan, -999.0)

#         current_data.index = [dt.datetime.strftime(
#             i, format=output_dt_format) for i in current_data.index]
        
#         df = current_data.to_csv(header=False).strip('\n').split('\n')
#         data = '\r\n'.join(df)

#         # ID,2.0
#         # x,642993.5
#         # y,5164882.0
#         # z,630.0
#         # area,-999.0
#         header = """ID,{id}\nx,{x}\ny,{y}\nz,{z}\narea,{area}\n"""

#         mkNestedDir(output_streamflow_data_path)
#         with open(output_streamflow_data_path + os.path.basename(el[:-4]) + '.txt', 'w') as new:
#             new.write(header.format(id=id,
#                         x=x, y=y, z=z, area=area))
#             new.write(data)


# In[ ]:




