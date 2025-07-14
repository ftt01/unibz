import os
import pandas as pd
import datetime  as dt
import glob

# Step 1: Save all directories in a list
input_dir = "/media/windows/projects/hydro_forecasting/vernago/testing/output/"  # Replace with your actual directory path
output_dir = "/media/windows/projects/hydro_forecasting/vernago/testing/output/"  # Replace with your desired output directory path

basin       = "B003"
subbasin    = "SB003"
release     = "R006"
model       = "M001"

type        = "ensemble"

base_dir = f"{input_dir}{basin}/{subbasin}/{release}/{model}/{type}/"
dirs = glob.glob(f"{base_dir}*")

# Step 2: Current date as the name of the directory + 1
computed_dates = [dt.datetime.strptime(dir[-8:],"%Y%m%d") for dir in dirs]

# Step 3, 4, and 5: Read forecast.csv, select data for the current date, and save in a unique dataframe
all_data = []

for computed_date in computed_dates:
    directory_path = os.path.join(base_dir, computed_date.strftime("%Y%m%d")) + "/"
    if type == "ensemble":
        csv_path = os.path.join(directory_path, "ens_forecast.csv")
    else:
        csv_path = os.path.join(directory_path, "forecast.csv")

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, parse_dates=True, index_col=0)
        
        # Step 3: Select data for the current date
        current_date_data = df[df.index.date == (computed_date + dt.timedelta(days=1)).date()]

        # Step 4: Save all information in a unique dataframe as a continuous time series
        all_data.append(current_date_data)

# Combine all dataframes into one
combined_dataframe = pd.concat(all_data)

# Step 5: Save the dataframe in the output directory
output_path = f"{output_dir}{basin}/{subbasin}/{release}/{model}/{type}/"
combined_dataframe.to_csv(f"{output_path}all_data.csv")