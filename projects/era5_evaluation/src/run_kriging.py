#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )
from lib import *


# In[2]:


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


# In[3]:


def write_geometry(number_of_cells, spatial_resolution, pathout):
    mkNestedDir(pathout)

    header = "{number_of_cells} {spatial_resolution}"
    header = header.format(number_of_cells=number_of_cells, spatial_resolution=spatial_resolution)

    file = open(pathout+"geometry.in","w+")
    [file.writelines(el + "\n") for el in [header]]


# In[4]:


def write_input(basin, grid_cells, pathout):
    mkNestedDir(pathout)

    line_1 = "{basin}"
    line_2 = "{grid_cells}"
    line_1 = line_1.format(basin=basin)
    line_2 = line_2.format(grid_cells=grid_cells)

    file = open(pathout+"input.txt","w+")
    [file.writelines(el + "\n") for el in [line_1, line_2]]


# In[5]:


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


# In[6]:

### using the data from Nicola - it takes all files and generate kriging input
def generate_kriging_input( 
    simulation_type, secs_timestep, steps, 
    weather_data_path, start_datetime_str, 
    end_datetime_str, dates):

    dataset = pd.DataFrame(index=dates)
    metadata = pd.DataFrame(index=range(0, 3))
    big_frame = pd.DataFrame()

    # percentage of no data allowed - range (0,1]
    perc_filter = 1

    # Get list of files available
    files = os.listdir(weather_data_path)
    # print(files)

    # Loop over weather stations
    for filename in files:

        try:

            # Get station ID
            IDstation = filename.split('.')[0]

            # Reading data
            data = pd.read_csv(weather_data_path + filename, index_col=0,
                                parse_dates=True, names=['labels', 'values'])

            # Extract time series in the required time window
            ts = data.loc[start_datetime_str:end_datetime_str]

            # Count no data
            n_no_data = len(ts[ts['values'] == -999])

            if n_no_data > perc_filter*len(ts):
                continue
            elif len(ts) == 0:
                print( "MISSING: " + str(IDstation) )
                continue
            else:
                # Extract metadata
                metadata[IDstation] = data.iloc[1:4].values
                # Populate the overall matrix of data
                dataset[IDstation] = np.round(ts.values,1)

                big_frame = pd.concat([metadata, dataset])
        
        except:
            continue

    if simulation_type == "KR":

        station_number = len(big_frame.columns)
        buckets = [0] * (station_number - 3)
        buckets.insert(0, secs_timestep)
        buckets.insert(0, station_number)
        buckets.insert(0, steps)

        big_frame_meta = pd.DataFrame(
            data=[buckets], columns=big_frame.columns.values)
        big_frame_id = pd.DataFrame(
            data=[big_frame.columns.values], columns=big_frame.columns.values)
        kriging_input = pd.concat(
            [pd.concat([big_frame_meta, big_frame_id]), big_frame])

        return kriging_input
    
    else:
        return big_frame


# In[7]:


### using the data from Pranav - it takes all files and generate kriging input bigframe
def generate_kriging_input2( 
    simulation_type, secs_timestep, steps,
    weather_data_path, weather_metadata_path,
    start_datetime_str, end_datetime_str ):

    # weather_data_path = "/media/windows/projects/bias_correction/applications/era5/kriging/python_version/data/TAA_data/QC_prec_sameer_final.csv"
    # weather_metadata_path = "/media/windows/projects/bias_correction/applications/era5/kriging/python_version/data/TAA_data/Prec_metadata_bias.csv"

    c_data = pd.read_csv( weather_data_path, index_col=0 )
    c_data = c_data.replace( np.NaN, -999.0 )
    c_data = c_data.loc[start_datetime_str:end_datetime_str]
    c_data.reset_index(inplace=True)

    c_mdata = pd.read_csv( weather_metadata_path, sep=',' )
    c_mdata = c_mdata[['ID new','Easting','Northing','Elevation']]
    c_mdata.set_index('ID new', inplace=True)
    c_mdata = c_mdata.T

    bigframe = pd.DataFrame( index=[-1,0,1,2] + c_data['datetime'].to_list() )

    for id in c_mdata.columns.values:

        buckets = c_data[id].to_list()
        buckets.insert(0, c_mdata[id]['Elevation'])
        buckets.insert(0, c_mdata[id]['Northing'])
        buckets.insert(0, c_mdata[id]['Easting'])
        buckets.insert(0, id)
        
        bigframe[id] = buckets
    
    bigframe = bigframe.drop([-1])

    if simulation_type == "KR":

        station_number = len(bigframe.columns)
        buckets = [0] * (station_number - 3)
        buckets.insert(0, secs_timestep)
        buckets.insert(0, station_number)
        buckets.insert(0, steps)

        big_frame_meta = pd.DataFrame(
            data=[buckets], columns=bigframe.columns.values)
        big_frame_id = pd.DataFrame(
            data=[bigframe.columns.values], columns=bigframe.columns.values)
        kriging_input = pd.concat(
            [pd.concat([big_frame_meta, big_frame_id]), bigframe])

        return kriging_input
    
    else:
        return bigframe


# In[8]:


def generate_output_grid( meta_file='data/grids/era5/epsg32632.csv', output_file='data/grids/era5/json_epsg32632.csv' ):

    md = pd.read_csv( meta_file )

    c_list = []
    for i in md.index:

        c_dict = {}

        c_dict['station_id'] = str(int(md.loc[i]['id']))
        try:
            c_dict['station_name'] = md.loc[i]['name']
        except:
            c_dict['station_name'] = str(int(md.loc[i]['id']))
        c_dict['east'] = md.loc[i]['east']
        c_dict['north'] = md.loc[i]['north']
        try:
            c_dict['elevation'] = md.loc[i]['elevation']
        except:
            c_dict['elevation'] = np.NaN

        c_list.append(c_dict)
        del c_dict
    
    with open(output_file, 'w') as json_grid_file:
        json.dump(c_list, json_grid_file, indent=2)
        json_grid_file.close()


# In[9]:


def merge_files( files_to_merge, dates, output_file_merged=None ):

    bigframe = pd.DataFrame(index=dates)

    for ff in files_to_merge:

        c_ff = pd.read_csv(ff)
        c_id = c_ff.columns[0]
        bigframe[c_id] = c_ff[c_id].values

    bigframe.index.name = 'datetime'
    
    if output_file_merged == None:
        from pathlib import Path
        c_path = Path(files_to_merge[0])
        c_output_file = c_path.parent.absolute() + "000_merged.csv"
    else:
        c_output_file = output_file_merged
    
    print("Merging in: " + c_output_file)
    bigframe.to_csv( c_output_file )


# In[10]:


#### SETUP ####
wdir = "/media/windows/projects/era5_bias/kriging/new_version/"
config_path = wdir + "etc/config/alberto/"
input_path = wdir + "input/16_alberto/"

# KRIGING MODEL SETUP
exe_path = wdir
# exe_name = "2020_06_kriging_PT.exe"
exe_name = "kriging_v3"


# In[11]:


## !! to run if the csv of the grid must be updated
# generate_output_grid( wdir + 'data/grids/AA/era5land/epsg32632_wElev_AA.csv', wdir + 'data/grids/AA/era5land/epsg32632.json' )


# In[ ]:


inputs = glob.glob( input_path + "*.json" )


# In[ ]:


inputs


# In[ ]:


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

    params = json.load(config_file)

    simulation_type = setup_sim["simulation_type"]

    basin = setup_sim["basin"]
    secs_timestep = setup_sim["secs_timestep"]
    number_of_stations = setup_sim["number_of_stations"]
    kriging_type = setup_sim["kriging_type"]
    kriging_model = params["kriging_model"]
    kriging_correction = setup_sim["kriging_correction"]
    grid_cells = setup_sim["grid_cells"]

    ## read cells json
    cells_json_path = wdir + setup_sim["cells_json_path"]
    cells_json_file = open(cells_json_path)
    cells_grid = json.load(cells_json_file)

    number_of_cells = len(cells_grid)
    print("Number of points: " + str(number_of_cells))

    start_datetime_str = setup_sim["start_datetime"]
    start_datetime = dt.datetime.strptime(
        start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_datetime_str = setup_sim["end_datetime"]
    end_datetime = dt.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
    dates = pd.date_range(start_datetime, end_datetime, freq='h')
    steps = len(dates)

    weather_data_path = wdir + setup_sim["weather_data_path"]
    weather_metadata_path = wdir + setup_sim["weather_metadata_path"]

    path_kriging_inputs = wdir + basin + "/input/"
    mkNestedDir(path_kriging_inputs)
    path_kriging_outputs = wdir + basin + "/output/"
    mkNestedDir(path_kriging_outputs)

    # AA version
    kriging_input = generate_kriging_input(
        simulation_type, secs_timestep, steps, 
        weather_data_path, start_datetime_str, 
        end_datetime_str, dates)
    
    # ## TAA version
    # kriging_input = generate_kriging_input2(
    #     simulation_type, secs_timestep, steps,
    #     weather_data_path, weather_metadata_path,
    #     start_datetime_str, end_datetime_str )

    if variable == "temperature":
        kriging_input.to_csv(
            path_kriging_inputs + "TMEAN_" + basin + ".in", index=False, header=False)
    elif variable == "precipitation":
        kriging_input.to_csv(path_kriging_inputs + "P_" +
                                basin + ".in", index=False, header=False)

    files_to_merge = []
    # OUTPUT DIRECTORY
    output_dir = wdir + setup_sim['output_path'] + \
        grid_cells + "/" + \
            variable + "/" + \
                simulation_type + "/" + \
                    kriging_type + "/" + \
                        kriging_correction + "/" + \
                            number_of_stations + "/"

    mkNestedDir(output_dir)

    # init stats
    sum_hourly_bias = 0.0
    sum_daily_bias = 0.0
    sum_monthly_bias = 0.0

    sum_hourly_rmse = 0.0
    sum_daily_rmse = 0.0
    sum_monthly_rmse = 0.0

    sum_hourly_mae = 0.0
    sum_daily_mae = 0.0
    sum_monthly_mae = 0.0

    sum_hourly_r2 = 0.0
    sum_daily_r2 = 0.0
    sum_monthly_r2 = 0.0

    n_computed_elements=0
    start_sim_email=True
    start_sim_datetime = dt.datetime.now()

    for i in range(number_of_cells):

        if (start_sim_email==True) and (n_computed_elements==1):
            simulation_step_time = end_sim_datetime.second - start_sim_datetime.second
            send_email(subject=simulation_type + " | computation started", body="Started " + str(input) +
                "\nNumber of points: " + str(number_of_cells) +
                "\nEstimated finish: " + str(dt.datetime.now() + dt.timedelta(seconds=simulation_step_time*number_of_cells)) +
                "\n\n" + str(json.dumps(setup_sim, indent=4)))
            start_sim_email = False

        station_name = cells_grid[i]["station_name"]
        station_id = cells_grid[i]["station_id"]
        east = cells_grid[i]["east"]
        north = cells_grid[i]["north"]
        elevation = cells_grid[i]["elevation"]

        print(station_id)

        ###########################################################

        # print(int(IDstation))
        if simulation_type == "CV":
            try:
                kriging_input_tmp = kriging_input.drop(columns=str(station_id))
                print("Excluded:" + str(station_id))

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

        output_file = output_dir + output_name + ".csv"
        print("Moving output to: " + output_file)
        try:
            os.rename(exe_output_name, output_file)
        except FileExistsError:
            os.remove(output_file)
            os.rename(exe_output_name, output_file)
        
        ## add to list for merging
        files_to_merge.append(output_file)

        # POST-PROCESSING STATS
        if bool(setup_sim['generate_stats']) == True and simulation_type == "CV":

            model_output = pd.DataFrame( pd.read_csv(output_file, parse_dates=True)[str(station_id)].values, columns=["model"])
            model_output.index = dates
            model_output = model_output[start_datetime:end_datetime]

            # print(model_output)

            if variable == "temperature":
                model_output_hourly = model_output.resample('h').agg(lambda x: np.nan if np.isnan(x).any() else np.nanmean(x))
                model_output_daily = model_output.resample("d").agg(lambda x: np.nan if np.isnan(x).any() else np.nanmean(x))
                model_output_monthly = model_output.resample("MS").agg(lambda x: np.nan if np.isnan(x).any() else np.nanmean(x))
            if variable == "precipitation":
                model_output_hourly = model_output.resample("h").agg(lambda x: np.nan if np.isnan(x).any() else np.nansum(x))
                model_output_daily = model_output.resample("d").agg(lambda x: np.nan if np.isnan(x).any() else np.nansum(x))
                model_output_monthly = model_output.resample("MS").agg(lambda x: np.nan if np.isnan(x).any() else np.nansum(x))

            model_output_hourly = model_output_hourly.iloc[:, 0]
            model_output_daily = model_output_daily.iloc[:, 0]
            model_output_monthly = model_output_monthly.iloc[:, 0]

            data_length = len(model_output)

            # read observed data
            obs_data_name = weather_data_path + str(station_id) + ".txt"
            print("Opening: " + obs_data_name)

            obs_data = pd.read_csv( obs_data_name, index_col=0, parse_dates=True, skiprows=4, names=['obs'] )

            # print(obs_data)

            obs_data = obs_data[start_datetime:end_datetime]
            obs_data[obs_data == -999] = None
            if variable == "temperature":
                obs_data_hourly = obs_data.resample('h').agg(lambda x: np.nan if np.isnan(x).any() else np.nanmean(x))
                obs_data_daily = obs_data.resample("d").agg(lambda x: np.nan if np.isnan(x).any() else np.nanmean(x))
                obs_data_monthly = obs_data.resample("MS").agg(lambda x: np.nan if np.isnan(x).any() else np.nanmean(x))
            if variable == "precipitation":
                obs_data_hourly = obs_data.resample("h").agg(lambda x: np.nan if np.isnan(x).any() else np.nansum(x))
                obs_data_daily = obs_data.resample("d").agg(lambda x: np.nan if np.isnan(x).any() else np.nansum(x))
                obs_data_monthly = obs_data.resample("MS").agg(lambda x: np.nan if np.isnan(x).any() else np.nansum(x))

            print("Evaluating stats:")

            output_path_stats = output_dir + "stats/"
            mkNestedDir(output_path_stats)

            # print(obs_data_hourly)
            
            # evaluate stats
            try:
                df_all_hourly = pd.concat( [obs_data_hourly, model_output_hourly], axis=1 )
                df_all_hourly.dropna(inplace=True)
                
                bias_hourly = np.mean(df_all_hourly["obs"] - df_all_hourly["model"])
                rmse_hourly = mean_squared_error( df_all_hourly["obs"], df_all_hourly["model"], squared=False)
                mae_hourly = mean_absolute_error( df_all_hourly["obs"], df_all_hourly["model"] )
                r2_hourly = r2_score( df_all_hourly["obs"], df_all_hourly["model"] )
                
                df_all_daily = pd.concat( [obs_data_daily, model_output_daily], axis=1 )
                df_all_daily.dropna(inplace=True)

                bias_daily = np.mean(df_all_daily["obs"] - df_all_daily["model"])
                rmse_daily = mean_squared_error( df_all_daily["obs"], df_all_daily["model"], squared=False)
                mae_daily = mean_absolute_error( df_all_daily["obs"], df_all_daily["model"] )
                r2_daily = r2_score( df_all_daily["obs"], df_all_daily["model"] )
                
                df_all_monthly = pd.concat( [obs_data_monthly, model_output_monthly], axis=1 )
                df_all_monthly.dropna(inplace=True)

                bias_monthly = np.mean(df_all_monthly["obs"] - df_all_monthly["model"])
                rmse_monthly = mean_squared_error( df_all_monthly["obs"], df_all_monthly["model"], squared=False)
                mae_monthly = mean_absolute_error( df_all_monthly["obs"], df_all_monthly["model"] )
                r2_monthly = r2_score( df_all_monthly["obs"], df_all_monthly["model"] )
                
                stats_df = pd.DataFrame(columns=['BIAS', 'RMSE', 'R2', 'MAE'])
                stats_df['timestep'] = ["hourly", "daily", "monthly"]
                stats_df['BIAS'] = [bias_hourly, bias_daily, bias_monthly]
                stats_df['RMSE'] = [rmse_hourly, rmse_daily, rmse_monthly]
                stats_df['R2'] = [r2_hourly, r2_daily, r2_monthly]
                stats_df['MAE'] = [mae_hourly, mae_daily, mae_monthly]

                stats_df.set_index('timestep', inplace=True)

                output_file_stats = output_path_stats + output_name + ".txt"
                print("Exporting to: " + output_file_stats)
                stats_df.to_csv(output_file_stats)

                ### prepare to mean stats
                out_stats = pd.read_csv(output_file_stats, index_col=0)
                sum_hourly_bias = sum_hourly_bias + float(out_stats.loc["hourly"]["BIAS"])
                sum_daily_bias = sum_daily_bias + float(out_stats.loc["daily"]["BIAS"])
                sum_monthly_bias = sum_monthly_bias + float(out_stats.loc["monthly"]["BIAS"])

                sum_hourly_rmse = sum_hourly_rmse + float(out_stats.loc["hourly"]["RMSE"])
                sum_daily_rmse = sum_daily_rmse + float(out_stats.loc["daily"]["RMSE"])
                sum_monthly_rmse = sum_monthly_rmse + float(out_stats.loc["monthly"]["RMSE"])

                sum_hourly_r2 = sum_hourly_r2 + float(out_stats.loc["hourly"]["R2"])
                sum_daily_r2 = sum_daily_r2 + float(out_stats.loc["daily"]["R2"])
                sum_monthly_r2 = sum_monthly_r2 + float(out_stats.loc["monthly"]["R2"])

                sum_hourly_mae = sum_hourly_mae + float(out_stats.loc["hourly"]["MAE"])
                sum_daily_mae = sum_daily_mae + float(out_stats.loc["daily"]["MAE"])
                sum_monthly_mae = sum_monthly_mae + float(out_stats.loc["monthly"]["MAE"])

                n_computed_elements=n_computed_elements+1

            except:
                continue

            try:
                df_all_jan = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==1], 
                    model_output_daily.loc[model_output_daily.index.month==1]], axis=1 )
                df_all_jan.dropna(inplace=True)
                df_all_feb = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==2], 
                    model_output_daily.loc[model_output_daily.index.month==2]], axis=1 )
                df_all_feb.dropna(inplace=True)
                df_all_mar = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==3], 
                    model_output_daily.loc[model_output_daily.index.month==3]], axis=1 )
                df_all_mar.dropna(inplace=True)
                df_all_apr = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==4], 
                    model_output_daily.loc[model_output_daily.index.month==4]], axis=1 )
                df_all_apr.dropna(inplace=True)
                df_all_may = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==5], 
                    model_output_daily.loc[model_output_daily.index.month==5]], axis=1 )
                df_all_may.dropna(inplace=True)
                df_all_jun = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==6], 
                    model_output_daily.loc[model_output_daily.index.month==6]], axis=1 )
                df_all_jun.dropna(inplace=True)
                df_all_jul = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==7], 
                    model_output_daily.loc[model_output_daily.index.month==7]], axis=1 )
                df_all_jul.dropna(inplace=True)
                df_all_aug = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==8], 
                    model_output_daily.loc[model_output_daily.index.month==8]], axis=1 )
                df_all_aug.dropna(inplace=True)
                df_all_sep = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==9], 
                    model_output_daily.loc[model_output_daily.index.month==9]], axis=1 )
                df_all_sep.dropna(inplace=True)
                df_all_oct = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==10], 
                    model_output_daily.loc[model_output_daily.index.month==10]], axis=1 )
                df_all_oct.dropna(inplace=True)
                df_all_nov = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==11], 
                    model_output_daily.loc[model_output_daily.index.month==11]], axis=1 )
                df_all_nov.dropna(inplace=True)
                df_all_dec = pd.concat( [
                    obs_data_daily.loc[obs_data_daily.index.month==12], 
                    model_output_daily.loc[model_output_daily.index.month==12]], axis=1 )
                df_all_dec.dropna(inplace=True)

                bias_jan_mean = df_all_jan["obs"] - df_all_jan["model"]
                rmse_jan_mean = mean_squared_error( df_all_jan["obs"], df_all_jan["model"], squared=False)
                mae_jan_mean = mean_absolute_error( df_all_jan["obs"], df_all_jan["model"] )
                r2_jan_mean = r2_score( df_all_jan["obs"], df_all_jan["model"] )
                bias_jan_mean = np.mean(df_all_jan["obs"] - df_all_jan["model"])

                rmse_feb_mean = mean_squared_error( df_all_feb["obs"], df_all_feb["model"], squared=False)
                mae_feb_mean = mean_absolute_error( df_all_feb["obs"], df_all_feb["model"] )
                r2_feb_mean = r2_score( df_all_feb["obs"], df_all_feb["model"] )
                bias_feb_mean = np.mean(df_all_feb["obs"] - df_all_feb["model"])

                rmse_mar_mean = mean_squared_error( df_all_mar["obs"], df_all_mar["model"], squared=False)
                mae_mar_mean = mean_absolute_error( df_all_mar["obs"], df_all_mar["model"] )
                r2_mar_mean = r2_score( df_all_mar["obs"], df_all_mar["model"] )
                bias_mar_mean = np.mean(df_all_mar["obs"] - df_all_mar["model"])

                rmse_apr_mean = mean_squared_error( df_all_apr["obs"], df_all_apr["model"], squared=False)
                mae_apr_mean = mean_absolute_error( df_all_apr["obs"], df_all_apr["model"] )
                r2_apr_mean = r2_score( df_all_apr["obs"], df_all_apr["model"] )
                bias_apr_mean = np.mean(df_all_apr["obs"] - df_all_apr["model"])

                rmse_may_mean = mean_squared_error( df_all_may["obs"], df_all_may["model"], squared=False)
                mae_may_mean = mean_absolute_error( df_all_may["obs"], df_all_may["model"] )
                r2_may_mean = r2_score( df_all_may["obs"], df_all_may["model"] )
                bias_may_mean = np.mean(df_all_may["obs"] - df_all_may["model"])

                rmse_jun_mean = mean_squared_error( df_all_jun["obs"], df_all_jun["model"], squared=False)
                mae_jun_mean = mean_absolute_error( df_all_jun["obs"], df_all_jun["model"] )
                r2_jun_mean = r2_score( df_all_jun["obs"], df_all_jun["model"] )
                bias_jun_mean = np.mean(df_all_jun["obs"] - df_all_jun["model"])
                
                rmse_jul_mean = mean_squared_error( df_all_jul["obs"], df_all_jul["model"], squared=False)
                mae_jul_mean = mean_absolute_error( df_all_jul["obs"], df_all_jul["model"] )
                r2_jul_mean = r2_score( df_all_jul["obs"], df_all_jul["model"] )
                bias_jul_mean = np.mean(df_all_jul["obs"] - df_all_jul["model"])

                rmse_aug_mean = mean_squared_error( df_all_aug["obs"], df_all_aug["model"], squared=False)
                mae_aug_mean = mean_absolute_error( df_all_aug["obs"], df_all_aug["model"] )
                r2_aug_mean = r2_score( df_all_aug["obs"], df_all_aug["model"] )
                bias_aug_mean = np.mean(df_all_aug["obs"] - df_all_aug["model"])

                rmse_sep_mean = mean_squared_error( df_all_sep["obs"], df_all_sep["model"], squared=False)
                mae_sep_mean = mean_absolute_error( df_all_sep["obs"], df_all_sep["model"] )
                r2_sep_mean = r2_score( df_all_sep["obs"], df_all_sep["model"] )
                bias_sep_mean = np.mean(df_all_sep["obs"] - df_all_sep["model"])

                rmse_oct_mean = mean_squared_error( df_all_oct["obs"], df_all_oct["model"], squared=False)
                mae_oct_mean = mean_absolute_error( df_all_oct["obs"], df_all_oct["model"] )
                r2_oct_mean = r2_score( df_all_oct["obs"], df_all_oct["model"] )
                bias_oct_mean = np.mean(df_all_oct["obs"] - df_all_oct["model"])

                rmse_nov_mean = mean_squared_error( df_all_nov["obs"], df_all_nov["model"], squared=False)
                mae_nov_mean = mean_absolute_error( df_all_nov["obs"], df_all_nov["model"] )
                r2_nov_mean = r2_score( df_all_nov["obs"], df_all_nov["model"] )
                bias_nov_mean = np.mean(df_all_nov["obs"] - df_all_nov["model"])

                rmse_dec_mean = mean_squared_error( df_all_dec["obs"], df_all_dec["model"], squared=False)
                mae_dec_mean = mean_absolute_error( df_all_dec["obs"], df_all_dec["model"] )
                r2_dec_mean = r2_score( df_all_dec["obs"], df_all_dec["model"] )
                bias_dec_mean = np.mean(df_all_dec["obs"] - df_all_dec["model"])

                m_stats_df = pd.DataFrame(columns=['RMSE', 'R2', 'MAE'])
                m_stats_df['timestep'] = [
                    "jan", "feb", "mar", \
                        "apr", "may", "jun", \
                            "jul", "aug", "sep", \
                                "oct", "nov", "dec" ]
                m_stats_df['BIAS'] = [bias_jan_mean,bias_feb_mean,bias_mar_mean,bias_apr_mean,bias_may_mean,bias_jun_mean,bias_jul_mean,bias_aug_mean,bias_sep_mean,bias_oct_mean,bias_nov_mean,bias_dec_mean]
                m_stats_df['RMSE'] = [rmse_jan_mean,rmse_feb_mean,rmse_mar_mean,rmse_apr_mean,rmse_may_mean,rmse_jun_mean,rmse_jul_mean,rmse_aug_mean,rmse_sep_mean,rmse_oct_mean,rmse_nov_mean,rmse_dec_mean]
                m_stats_df['R2'] = [r2_jan_mean,r2_feb_mean,r2_mar_mean,r2_apr_mean,r2_may_mean,r2_jun_mean,r2_jul_mean,r2_aug_mean,r2_sep_mean,r2_oct_mean,r2_nov_mean,r2_dec_mean]
                m_stats_df['MAE'] = [mae_jan_mean,mae_feb_mean,mae_mar_mean,mae_apr_mean,mae_may_mean,mae_jun_mean,mae_jul_mean,mae_aug_mean,mae_sep_mean,mae_oct_mean,mae_nov_mean,mae_dec_mean]

                m_stats_df.set_index('timestep', inplace=True)

                output_file_stats = output_path_stats + output_name + "_monthly_mean.txt"
                print("Exporting to: " + output_file_stats)
                m_stats_df.to_csv(output_file_stats)
            
            except:
                print("Every month must have at least one value not NaN to evaluate this stats!")

        end_sim_datetime = dt.datetime.now()
    
    merge_files( files_to_merge, dates, output_file_merged=output_dir+"000_merged_{sd}_{ed}.csv".format(
        sd=start_datetime.strftime(format='%Y%m%d'),
        ed=end_datetime.strftime(format='%Y%m%d')))
    
    if bool(setup_sim['generate_stats']) == True and simulation_type == "CV":
        bias_hourly_mean = sum_hourly_bias / n_computed_elements
        bias_daily_mean = sum_daily_bias / n_computed_elements
        bias_monthly_mean = sum_monthly_bias / n_computed_elements

        rmse_hourly_mean = sum_hourly_rmse / n_computed_elements
        rmse_daily_mean = sum_daily_rmse / n_computed_elements
        rmse_monthly_mean = sum_monthly_rmse / n_computed_elements

        r2_hourly_mean = sum_hourly_r2 / n_computed_elements
        r2_daily_mean = sum_daily_r2 / n_computed_elements
        r2_monthly_mean = sum_monthly_r2 / n_computed_elements

        mae_hourly_mean = sum_hourly_mae / n_computed_elements
        mae_daily_mean = sum_daily_mae / n_computed_elements
        mae_monthly_mean = sum_monthly_mae / n_computed_elements

    data = [["hourly", bias_hourly_mean, rmse_hourly_mean, r2_hourly_mean, mae_hourly_mean ],
            ["daily", bias_daily_mean, rmse_daily_mean,r2_daily_mean, mae_daily_mean ],
            ["monthly", bias_monthly_mean, rmse_monthly_mean, r2_monthly_mean, mae_monthly_mean ]]

    output_stats = pd.DataFrame(data, columns=["timestep", "BIAS", "RMSE", "R2", "MAE"])
    output_stats.set_index("timestep", inplace=True)

    output_stats.to_csv( output_path_stats + "00_statistics_mean.txt" )
    
    sim_datetime_end = dt.datetime.now()

    send_email(
        subject=simulation_type + " | computation done", 
        body="Started at " + str(start_sim_datetime) + \
            "\nEnded in " + str(sim_datetime_end.second - start_sim_datetime.second) + " seconds."
            "\nNumber of points computed: " + str(n_computed_elements) + \
            "\n\n" + str(json.dumps(setup_sim, indent=4))
    )
    

# In[ ]:


# for input in inputs:
#     print(input[:-5])

#     setup_file = open(input)
#     setup_sim = json.load(setup_file)
#     variable = setup_sim["variable"]

#     # coordinates = coordinates.format(
#     #     east=east, north=north, elevation=elevation)
#     # config_file = open(config_path + "temperature.json")
#     # file = open(pathout+"subcells.in", "w+")
#     # [file.writelines(el + "\n") for el in [header, cell_metadata, coordinates]]

#     if variable == "temperature":
#         config_file = open(config_path + "temperature.json")
#     elif variable == "precipitation":
#         config_file = open(config_path + "precipitation.json")

#     params = json.load(config_file)

#     simulation_type = setup_sim["simulation_type"]

#     basin = setup_sim["basin"]
#     secs_timestep = setup_sim["secs_timestep"]
#     number_of_stations = setup_sim["number_of_stations"]
#     kriging_type = setup_sim["kriging_type"]
#     kriging_model = params["kriging_model"]
#     kriging_correction = setup_sim["kriging_correction"]

#     number_of_cells = len(cells_grid)
#     print("Number of points: " + str(number_of_cells))

#     start_datetime_str = setup_sim["start_datetime"]
#     start_datetime = dt.datetime.strptime(
#         start_datetime_str, '%Y-%m-%d %H:%M:%S')
#     end_datetime_str = setup_sim["end_datetime"]
#     end_datetime = dt.datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')
#     dates = pd.date_range(start_datetime, end_datetime, freq='h')
#     steps = len(dates)

#     weather_data_path = wdir + setup_sim["weather_data_path"]

#     path_kriging_inputs = wdir + basin + "/input/"
#     path_kriging_outputs = wdir + basin + "/output/"

#     # OUTPUT DIRECTORY
#     output_dir = wdir + setup_sim['output_path'] + variable + "/" + simulation_type + \
#         "/" + kriging_type + "/" + kriging_correction + "/"
#     mkNestedDir(output_dir)

#     elevation_array = []
#     error_array = []

#     for i in range(number_of_cells):

#         station_name = cells_grid[i]["station_name"]
#         station_id = cells_grid[i]["station_id"]
#         east = cells_grid[i]["east"]
#         north = cells_grid[i]["north"]
#         elevation = cells_grid[i]["elevation"]

#         ###########################################################

#         elevation_array.append(elevation)

#         output_path_stats = output_dir + "stats/"
#         output_name = simulation_type + "_" + str(station_id) + "_" + station_name + "_" + kriging_type + "_" + \
#             start_datetime.strftime(format='%Y%m%d') + \
#             "_" + end_datetime.strftime(format='%Y%m%d')
        
#         tmp_stats = pd.read_csv(output_path_stats + output_name + ".txt", index_col=0)
#         error_array.append( tmp_stats.loc['hourly']['MAE'] )

#     fig, axs = instantiatePlot( "MAE", "Elevation $[m]$" )

#     axs.scatter( error_array, elevation_array, s=10 )

#     output_file = output_dir + "plots/" + os.path.basename(input[:-5]) + "_MAE_over_elevation." + output_format
#     mkNestedDir(getPathFromFilepath(output_file))
#     fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=50 )

#     output_file_hd = output_dir + "plots/" + os.path.basename(input[:-5]) + "_MAE_over_elevation_HD." + output_format
#     mkNestedDir(getPathFromFilepath(output_file_hd))
#     fig.savefig( output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=600 ) 

