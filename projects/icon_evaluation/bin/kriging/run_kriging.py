#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )

from lib import *


# In[ ]:


def write_subcells(number_of_cells, cell_id, spatial_resolution, east, north, elevation, pathout):
    mkNestedDir(pathout)

    header = "{number_of_cells} {spatial_resolution} {spatial_resolution}"
    header = header.format(number_of_cells=number_of_cells, spatial_resolution=spatial_resolution)

    cell_metadata = "{id} 1"
    cell_metadata = cell_metadata.format(id=cell_id, spatial_resolution=spatial_resolution)

    coordinates = "{east} {north} {elevation} 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0 1.0"
    coordinates = coordinates.format(east=east, north=north, elevation=elevation)

    file = open(pathout+"subcells.in","w+")
    [file.writelines(el + "\n") for el in [header, cell_metadata, coordinates]]


# In[ ]:


def write_geometry(number_of_cells, spatial_resolution, pathout):
    mkNestedDir(pathout)

    header = "{number_of_cells} {spatial_resolution}"
    header = header.format(number_of_cells=number_of_cells, spatial_resolution=spatial_resolution)

    file = open(pathout+"geometry.in","w+")
    [file.writelines(el + "\n") for el in [header]]


# In[ ]:


def write_input(basin, grid_cells, pathout):
    mkNestedDir(pathout)

    line_1 = "{basin}"
    line_2 = "{grid_cells}"
    line_1 = line_1.format(basin=basin)
    line_2 = line_2.format(grid_cells=grid_cells)

    file = open(pathout+"input.txt","w+")
    [file.writelines(el + "\n") for el in [line_1, line_2]]


# In[ ]:


def write_params(variable, number_of_stations, kriging_type, kriging_model, kriging_correction, nugget, var, Ia, secs_timestep, starting_date, basin, pathout):
    mkNestedDir(pathout)

    line_1 = "{Ia}  0   0   {var}   {nug}               ! Parameters for kriging (I_a, I_e, m, var, var_nug) --> variogr. precip."
    line_2 = "{Ia}  0   0   {var}   {nug}               ! Parameters for kriging (I_a, I_e, m, var, var_nug) --> variogr. temper."
    line_3 = "-999  -999    -999    -999    -999        ! Parameters for kriging (I_a, I_e, m, var, var_nug) --> TMIN"
    line_4 = "-999  -999    -999    -999    -999        ! Parameters for kriging (I_a, I_e, m, var, var_nug) --> TMAX"
    line_5 = "{number_of_stations}                      ! nk: number of neighbour meteorological stations used in the kriging"
    line_6 = "{kriging_type}                            ! Type of Kriging OK, OKED"
    line_7 = "{kriging_model}                           ! Model equation EXP, DBLE_EXP --> modello di semivariogramma"
    line_8 = "{kriging_correction}				        ! Correction of negative weights NO, RESET, ADD, DEUTSCH --> pesi negativi ogni tanto, per avere sum(pesi)=1"
    line_9 = "{secs_timestep}                           ! Output time step [s]"
    line_10 = "{var}                                    ! P = Rainfall,  T = Temperature"
    line_11 = "{datetime}	                            ! Starting date (measurements) yyyy/mm/dd hh:mm"
    line_12 = "{basin}                                  ! Bacino"
    line_13 = "0					                    ! flag_varcond: 1--> evaluate conditional variance (0 --> otherwise)"

    if variable == "temperature":
        line_1 = line_1.format(Ia="-999", var="-999", nug="-999")
        line_2 = line_2.format(Ia=Ia, var=var, nug=nugget)
        line_10 = line_10.format(var="T")

    if variable == "precipitation":
        line_2 = line_2.format(Ia="-999", var="-999", nug="-999")
        line_1 = line_1.format(Ia=Ia, var=var, nug=nugget)
        line_10 = line_10.format(var="P")

    line_5 = line_5.format(number_of_stations=number_of_stations)
    line_6 = line_6.format(kriging_type=kriging_type)
    line_7 = line_7.format(kriging_model=kriging_model)
    line_8 = line_8.format(kriging_correction=kriging_correction)
    line_9 = line_9.format(secs_timestep=secs_timestep)
    line_11 = line_11.format(datetime=starting_date)
    line_12 = line_12.format(basin=basin)

    file = open(pathout+"kriging_params.in","w+")
    [file.writelines(el + "\n") for el in [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11, line_12, line_13]]


# In[ ]:


def generate_kriging_input(weather_data_path, weather_input_dt_format, start_datetime, end_datetime):
    dataset = pd.DataFrame(index=dates)
    metadata = pd.DataFrame(index=range(1, 4))
    big_frame = pd.DataFrame()

    # percentage of no data allowed - range (0,1]
    perc_filter = 1

    # Get list of files available
    files = os.listdir(weather_data_path)
    # print(files)

    # Loop over weather stations
    for filename in files:

        # Get station ID
        IDstation = filename.split('.')[0]
        print("Setup: " + IDstation)

        # Reading data
        # "/media/windows/projects/icon-evaluation/kriging/data/passirio/GS/precipitation/101.txt"
        # data = pd.read_csv(weather_data_path + filename, index_col=0, parse_dates=True, names=['datetime', 'values'], skiprows=4)
        print("Opening: " + weather_data_path + filename)
        data = pd.read_csv(weather_data_path + filename,
                           names=['datetime', 'values'])
        # print(weather_data_path + filename)

        # Extract time series in the required time window
        # ts = pd.DataFrame( data.iloc[5:] )
        # ts['datetime'] = [ dt.datetime.strptime(t, weather_input_dt_format) for t in ts['datetime'] ]
        # ts.set_index('datetime', inplace=True)
        ts = read_timeseries_pd(pd.read_csv(weather_data_path + filename, names=[
                                'datetime', 'values'], skiprows=4), input_dt_format=weather_input_dt_format)
        ts = ts[start_datetime:end_datetime]

        n_no_data = 0
        arr = []
        for date in dates:
            try:
                if np.isnan(ts.loc[date][0]):
                    # print('ERR: nan')
                    raise
                else:
                    arr.append(ts.loc[date][0])
                    # print('appending..')
            except:
                arr.append(np.nan)
                n_no_data = n_no_data + 1

        if n_no_data > perc_filter*len(arr):
            continue
        elif len(arr) == n_no_data:
            print("MISSING: " + str(IDstation))
            continue
        else:
            # Extract metadata
            metadata[IDstation] = data.iloc[1:4]['values']
            # Populate the overall matrix of data
            dataset[IDstation] = arr

            big_frame = pd.concat([metadata, dataset])

        print("End node: " + IDstation)

    # this imputation is just a workaround - TODO
    # nan_indexes = big_frame[big_frame.isna().all(axis=1)]

    # for j in [big_frame.index.get_loc(i) for i in nan_indexes.index]:
    #     big_frame.iloc[j] = big_frame.iloc[j-1].values
    
    big_frame = big_frame.fillna(axis=0, method='ffill')
    big_frame = big_frame.fillna(-999.0)

    return big_frame


# In[ ]:


#### SETUP ####
wdir = "/media/windows/projects/icon-evaluation/kriging/"
os.chdir(wdir)
# wdir = "/media/windows/projects/era5_bias/kriging/"
config_path = wdir + "etc/config/"
input_path = wdir + "input/"

### KRIGING MODEL SETUP
## LINUX
exe_path = wdir 
# exe_name = "2020_06_kriging_PT.exe"
exe_name = "kriging_v3"


# In[ ]:


inputs = glob.glob( input_path + "*.json" )


# In[ ]:


### for each input == configuration JSON file

for input in inputs:
    print(input)

    setup_file = open(input)
    setup_sim = json.load(setup_file)
    variable = setup_sim["variable"]

    # coordinates = coordinates.format(
    #     east=east, north=north, elevation=elevation)
    # config_file = open(config_path + "temperature.json")
    # file = open(pathout+"subcells.in", "w+")
    # [file.writelines(el + "\n") for el in [header, cell_metadata, coordinates]]

    if variable == "temperature":
        config_file = open(config_path + "temperature.json")
    elif variable == "precipitation":
        config_file = open(config_path + "precipitation.json")
    else:
        print( 'Not a valid variable: ' + variable )

    params = json.load(config_file)

    simulation_type = setup_sim["simulation_type"]

    basin = setup_sim["basin"]
    secs_timestep = setup_sim["secs_timestep"]
    number_of_stations = setup_sim["number_of_stations"]
    kriging_type = setup_sim["kriging_type"]
    kriging_model = params["kriging_model"]
    kriging_correction = setup_sim["kriging_correction"]
    grid_cells = setup_sim["grid_cells"]

    number_of_cells = len(setup_sim["cells"])
    print("Number of points: " + str(number_of_cells))

    timezone_str = setup_sim["timezone"]
    start_datetime_str = setup_sim["start_datetime"]
    start_datetime = dt.datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M:%S')
    end_datetime_str = setup_sim["end_datetime"]
    end_datetime = dt.datetime.strptime(end_datetime_str, '%Y-%m-%dT%H:%M:%S')
    dates = [ start_datetime + dt.timedelta(hours=x) for x in range(0, (end_datetime-start_datetime).days*24) ]
    steps = len(dates)

    weather_data_path = wdir + setup_sim["weather_data_path"]
    weather_input_dt_format = setup_sim["input_dt_format"]

    path_kriging_inputs = wdir + basin + "/input/"
    path_kriging_outputs = wdir + basin + "/output/"

    kriging_input = generate_kriging_input(
        weather_data_path, weather_input_dt_format, start_datetime, end_datetime)

    if simulation_type == "KR":

        station_number = len(kriging_input.columns)
        buckets = [0] * (station_number - 3)
        buckets.insert(0, secs_timestep)
        buckets.insert(0, station_number)
        buckets.insert(0, steps)

        big_frame_meta = pd.DataFrame(
            data=[buckets], columns=kriging_input.columns.values)
        big_frame_id = pd.DataFrame(
            data=[kriging_input.columns.values], columns=kriging_input.columns.values)
        kriging_input = pd.concat(
            [pd.concat([big_frame_meta, big_frame_id]), kriging_input])

        if variable == "temperature":
            kriging_input.to_csv(
                path_kriging_inputs + "TMEAN_" + basin + ".in", index=False, header=False)
        elif variable == "precipitation":
            kriging_input.to_csv(path_kriging_inputs + "P_" +
                                 basin + ".in", index=False, header=False)

    sent_email = False

    for i in range(number_of_cells):

        station_name = setup_sim["cells"][i]["station_name"]
        station_id = setup_sim["cells"][i]["station_id"]
        east = setup_sim["cells"][i]["east"]
        north = setup_sim["cells"][i]["north"]
        elevation = setup_sim["cells"][i]["elevation"]

        print(station_id)

        ###########################################################

        start_sim_datetime = dt.datetime.now()

        if simulation_type == "CV":
            try:
                kriging_input_tmp = kriging_input.drop(columns=str(station_id))
                print("Excluded: " + str(station_id))

                station_number = len(kriging_input_tmp.columns)
                buckets = [0] * (station_number - 3)
                buckets.insert(0, secs_timestep)
                buckets.insert(0, station_number)
                buckets.insert(0, steps)

                big_frame_meta = pd.DataFrame(
                    data=[buckets], columns=kriging_input_tmp.columns.values)
                big_frame_id = pd.DataFrame(
                    data=[kriging_input_tmp.columns.values], columns=kriging_input_tmp.columns.values)
                kriging_input_tmp = pd.concat(
                    [pd.concat([big_frame_meta, big_frame_id]), kriging_input_tmp])

                if variable == "temperature":
                    kriging_input_tmp.to_csv(path_kriging_inputs + "TMEAN_" +
                                            basin + ".in", index=False, header=False)
                elif variable == "precipitation":
                    kriging_input_tmp.to_csv(path_kriging_inputs + "P_" +
                                            basin + ".in", index=False, header=False)
            except:
                print("Not in the JSON file: " + str(station_id))
                continue

        write_params(variable, number_of_stations, kriging_type, kriging_model, kriging_correction, params["model_nugget"],
                     params["model_psill"], params["model_range"],
                     secs_timestep, start_datetime.strftime(format='%Y/%m/%d %H:%M'), basin, path_kriging_inputs)

        pathout_subcell = wdir + basin + "/input/" + grid_cells + "/"
        write_input(basin, grid_cells, wdir)
        write_subcells(1, station_id, 30, east, north,
                       elevation, pathout_subcell)
        write_geometry(1, 30, pathout_subcell)

        print("RUN the model..")

        # RUN THE MODEL
        path = exe_path
        os.chdir(path)
        # os.system(exe_name)
        p = subprocess.Popen(exe_path + exe_name,
                             stdin=subprocess.PIPE, shell=True)
        p.communicate(input='\n'.encode())

        if variable == "temperature":
            exe_output_name = path_kriging_outputs +                 str(start_datetime.year) + "_" +                 str(start_datetime.month) + "/TMEAN_" + basin + ".krig"
        elif variable == "precipitation":
            exe_output_name = path_kriging_outputs +                 str(start_datetime.year) + "_" +                 str(start_datetime.month) + "/P_" + basin + ".krig"

        output_name = simulation_type + "_" + str(station_id) + "_" + station_name + "_" + kriging_type + "_" +             start_datetime.strftime(format='%Y%m%d') +             "_" + end_datetime.strftime(format='%Y%m%d')

        # OUTPUT DIRECTORY
        output_dir = wdir + setup_sim['output_path'] + variable + "/" + simulation_type +             "/" + kriging_type + "/" + kriging_correction + "/"
        mkNestedDir(output_dir)

        output_file = output_dir + output_name + ".csv"
        print("Moving output to: " + output_file)
        try:
            os.rename(exe_output_name, output_file)
        except FileExistsError:
            os.remove(output_file)
            os.rename(exe_output_name, output_file)

        # POST-PROCESSING STATS
        if bool(setup_sim['generate_stats']) == True and simulation_type == "CV":

            model_output = pd.DataFrame( pd.read_csv(output_file, parse_dates=True)[str(station_id)].values, columns=["model"])
            model_output.index = dates
            model_output = model_output[start_datetime:end_datetime]

            model_output['model'] = pd.to_numeric(model_output['model'], errors='coerce')

            # print(model_output)

            if variable == "temperature":
                model_output_hourly = model_output.resample("h").mean()
                model_output_daily = model_output.resample("d").mean()
                model_output_monthly = model_output.resample("MS").mean()
            if variable == "precipitation":
                model_output_hourly = model_output.resample("h").sum()
                model_output_daily = model_output.resample("d").sum()
                model_output_monthly = model_output.resample("MS").sum()

                model_output_hourly = model_output_hourly.iloc[:, 0]
                model_output_daily = model_output_daily.iloc[:, 0]
                model_output_monthly = model_output_monthly.iloc[:, 0]

            data_length = len(model_output)

            # read observed data
            obs_data_name = weather_data_path + str(station_id) + ".txt"
            print("Opening: " + obs_data_name)

            # obs_data = read_timeseries_pd( pd.read_csv(obs_data_name, skiprows=4, names=['datetime', 'obs']), '%Y-%m-%dT%H:%M:%S.%f%z' )
            obs_data = read_timeseries_pd( pd.read_csv(obs_data_name, skiprows=4, names=['datetime', 'obs']), weather_input_dt_format )

            # print(obs_data)

            obs_data = obs_data[start_datetime:end_datetime]
            obs_data[obs_data == -999] = None
            if variable == "temperature":
                obs_data_hourly = obs_data.resample("h").mean()
                obs_data_daily = obs_data.resample("d").mean()
                obs_data_monthly = obs_data.resample("MS").mean()
            if variable == "precipitation":
                obs_data_hourly = obs_data.resample("h").sum()
                obs_data_daily = obs_data.resample("d").sum()
                obs_data_monthly = obs_data.resample("MS").sum()

            print("Evaluating stats:")

            output_path_stats = output_dir + "stats/"
            mkNestedDir(output_path_stats)

            # print(obs_data_hourly)
            
            # evaluate stats
            df_all_hourly = pd.concat( [obs_data_hourly, model_output_hourly], axis=1 )
            df_all_hourly.dropna(inplace=True)

            if not( df_all_hourly.empty ):

                rmse_hourly = mean_squared_error( df_all_hourly["obs"], df_all_hourly["model"], squared=False)
                mae_hourly = mean_absolute_error( df_all_hourly["obs"], df_all_hourly["model"] )
                r2_hourly = r2_score( df_all_hourly["obs"], df_all_hourly["model"] )
                
                df_all_daily = pd.concat( [obs_data_daily, model_output_daily], axis=1 )
                df_all_daily.dropna(inplace=True)

                rmse_daily = mean_squared_error( df_all_daily["obs"], df_all_daily["model"], squared=False)
                mae_daily = mean_absolute_error( df_all_daily["obs"], df_all_daily["model"] )
                r2_daily = r2_score( df_all_daily["obs"], df_all_daily["model"] )

                df_all_monthly = pd.concat( [obs_data_monthly, model_output_monthly], axis=1 )
                df_all_monthly.dropna(inplace=True)

                rmse_monthly = mean_squared_error( df_all_monthly["obs"], df_all_monthly["model"], squared=False)
                mae_monthly = mean_absolute_error( df_all_monthly["obs"], df_all_monthly["model"] )
                r2_monthly = r2_score( df_all_monthly["obs"], df_all_monthly["model"] )

                # rmse_monthly = np.sqrt(
                #     (1/data_length) * np.nansum((obs_data_monthly.T.values - model_output_monthly.values)**2))
                # cc_monthly = np.ma.corrcoef(np.ma.masked_invalid(
                #     model_output_monthly.values), np.ma.masked_invalid(obs_data_monthly.T.values))
                # mae_monthly = (np.nansum(
                #     np.abs(obs_data_monthly.T.values - model_output_monthly.values)))/data_length

                stats_df = pd.DataFrame(columns=['RMSE', 'R2', 'MAE'])
                stats_df['timestep'] = ["hourly", "daily", "monthly"]
                stats_df['RMSE'] = [rmse_hourly, rmse_daily, rmse_monthly]
                stats_df['R2'] = [r2_hourly, r2_daily, r2_monthly]
                stats_df['MAE'] = [mae_hourly, mae_daily, mae_monthly]

                stats_df.set_index('timestep', inplace=True)

                output_file_stats = output_path_stats + output_name + ".txt"
                print("Exporting to: " + output_file_stats)
                stats_df.to_csv(output_file_stats)

        end_sim_datetime = dt.datetime.now()

        if sent_email == False:

            simulation_step_time = end_sim_datetime.second - start_sim_datetime.second
            send_email(subject=simulation_type + " | computation started", body="Started " + str(input) +
                       "\nNumber of points: " + str(number_of_cells) +
                       "\nEstimated finish: " + str(dt.datetime.now() + dt.timedelta(seconds=simulation_step_time*number_of_cells)) +
                       "\n" + str(json.dumps(setup_sim, indent=4)))
            sent_email = True
    
    if bool(setup_sim['generate_stats']) == True and simulation_type == "CV":

        outputs = glob.glob(output_path_stats + "*.txt")

        # create stats
        sum_hourly_rmse = 0.0
        sum_daily_rmse = 0.0
        sum_monthly_rmse = 0.0

        sum_hourly_mae = 0.0
        sum_daily_mae = 0.0
        sum_monthly_mae = 0.0

        sum_hourly_r2 = 0.0
        sum_daily_r2 = 0.0
        sum_monthly_r2 = 0.0

        for out in outputs:

            # print(os.path.basename(out).split("_"))

            out_stats = pd.read_csv(out, index_col=0)
            sum_hourly_rmse = sum_hourly_rmse +                 float(out_stats.loc["hourly"]["RMSE"])
            sum_daily_rmse = sum_daily_rmse + float(out_stats.loc["daily"]["RMSE"])
            sum_monthly_rmse = sum_monthly_rmse +                 float(out_stats.loc["monthly"]["RMSE"])

            sum_hourly_mae = sum_hourly_mae + float(out_stats.loc["hourly"]["MAE"])
            sum_daily_mae = sum_daily_mae + float(out_stats.loc["daily"]["MAE"])
            sum_monthly_mae = sum_monthly_mae +                 float(out_stats.loc["monthly"]["MAE"])

            sum_hourly_r2 = sum_hourly_r2 + float(out_stats.loc["hourly"]["R2"])
            sum_daily_r2 = sum_daily_r2 + float(out_stats.loc["daily"]["R2"])
            sum_monthly_r2 = sum_monthly_r2 + float(out_stats.loc["monthly"]["R2"])

        rmse_hourly_mean = sum_hourly_rmse / len(outputs)
        rmse_daily_mean = sum_daily_rmse / len(outputs)
        rmse_monthly_mean = sum_monthly_rmse / len(outputs)

        mae_hourly_mean = sum_hourly_mae / len(outputs)
        mae_daily_mean = sum_daily_mae / len(outputs)
        mae_monthly_mean = sum_monthly_mae / len(outputs)

        r2_hourly_mean = sum_hourly_r2 / len(outputs)
        r2_daily_mean = sum_daily_r2 / len(outputs)
        r2_monthly_mean = sum_monthly_r2 / len(outputs)

        data = [["hourly", rmse_hourly_mean, mae_hourly_mean, r2_hourly_mean],
                ["daily", rmse_daily_mean, mae_daily_mean, r2_daily_mean],
                ["monthly", rmse_monthly_mean, mae_monthly_mean, r2_monthly_mean]]

        output_stats = pd.DataFrame(data, columns=["timestep", "RMSE", "MAE", "R2"])
        output_stats.set_index("timestep", inplace=True)

        output_stats.to_csv( output_path_stats + "00_statistics_mean.txt" )

    send_email(subject=simulation_type + " | computation done", body="Ended: " + str(input))

