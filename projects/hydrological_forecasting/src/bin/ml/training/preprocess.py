import sys

locallib_dir = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/lib"
sys.path.insert( 0, locallib_dir )

from locallib import *

wdir = "/media/windows/projects/hydro_forecasting/machine_learning/input/"

start_datetime_str = "2010-10-01T00:00:00"
end_datetime_str = "2019-09-30T23:59:00"

start_sim_datetime_str = "2017-10-01T00:00:00"
end_sim_datetime_str = "2019-09-30T23:59:00"

lag_hours = 168
lead_hours = 48
prediction_interval = 24

roi_conf = "/home/daniele/documents/github/ftt01/phd/metadata/basins/phd/B002.json"

ens_size = 12

mode = "operative"

variables = [
    {
        "name": "precipitation",
        "params": {
            "type": "raw",
            "ffill": True,
            "default": 0,
            "provider" : "era5land"
        }
    },
    {
        "name": "temperature",
        "params": {
            "type": "raw",
            "ffill": True,
            "default": 20,
            "provider" : "era5land"
        }
    },
    {
        "name": "streamflow",
        "params": {
            "type": "raw",
            "ffill": True,
            "default": 0,
            "provider" : "PAB"
        }
    }
]

#######

output_path = f"{wdir}data/"

logging, run_datetime = get_logging(output_path, logging_level=logging.DEBUG)
sim_name = run_datetime.strftime("%Y%m%dT%H%M%S")

output_path = f"{output_path}{sim_name}/"

start_data_datetime = dt.datetime.strptime( start_datetime_str, '%Y-%m-%dT%H:%M:%S' )
end_data_datetime = dt.datetime.strptime( end_datetime_str, '%Y-%m-%dT%H:%M:%S' )

start_sim_datetime = dt.datetime.strptime( start_sim_datetime_str, '%Y-%m-%dT%H:%M:%S' )
end_sim_datetime = dt.datetime.strptime( end_sim_datetime_str, '%Y-%m-%dT%H:%M:%S' )

sim_dates = date_range( start=start_sim_datetime, end=end_sim_datetime, freq=f"{prediction_interval}H" )

#######

meta = Metadata(roi_conf)

for basin in meta.basins:
    for var in variables:
        ##
        var_name = var["name"]
        
        c_var, c_df = basin.get_data(
            start_data_datetime, end_data_datetime, var_name, var["params"], neighbors=ens_size
        )

        if mode == "training":

            c_out_filename = f"{output_path}{var_name}/{basin.key}.csv"
            create_dir(c_out_filename)

            ## mean all the points
            c_df_mean = c_df.mean(axis=1).to_frame()
            c_df_mean.rename(columns={c_df_mean.columns[0]:"values"}, inplace=True)
            c_df_mean.to_csv(c_out_filename)

        else:
            c_out_filepath_ens = f"{output_path}{var_name}/ensemble/"
            create_dir(c_out_filepath_ens)

            c_out_filepath_mean = f"{output_path}{var_name}/mean/"
            create_dir(c_out_filepath_mean)

            for date in sim_dates:
                ## batch data
                cc_df = batch_data(c_df, date, lag_hours, lead_hours)
                cc_df = DataFrame(cc_df.values, index=c_df.index, columns=[str(i+1).zfill(3) for i in range(c_df.shape[1])])

