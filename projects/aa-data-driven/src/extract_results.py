import os
import pandas as pd
import numpy as np
import glob
from sklearn.metrics import r2_score, mean_absolute_error


release = 6
basin = "B004"
subbasins = [
    ("SB001","/media/windows/projects/aa-data-driven/paper/03_icon/training/input/data/streamflow/03750PG.csv"),
    ("SB012","/media/windows/projects/aa-data-driven/paper/03_icon/training/input/data/streamflow/59450PG.csv")
]

for meta in subbasins:

    main_directory = '/media/windows/projects/aa-data-driven/paper/03_icon/testing/output/{basin}/{subbasin}/{release}/1/mean/'

    output_directory = '/media/windows/projects/aa-data-driven/paper/03_icon/testing/output/{basin}/{subbasin}/{release}/merged/'

    output_directory = output_directory.format(
        basin = basin,
        subbasin = meta[0],
        release = "R"+str(release).zfill(3)
    )
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Read the reference CSV file into a DataFrame with datetime as the index
    reference_df = pd.read_csv(meta[1], index_col=0)
    reference_df.index = pd.to_datetime(reference_df.index, utc=True).tz_localize(None)

    main_directory = main_directory.format(
        basin = basin,
        subbasin = meta[0],
        release = "R"+str(release).zfill(3)
    )

    # Get a list of all directories in the main directory
    directories = [d for d in os.listdir(main_directory) if os.path.isdir(os.path.join(main_directory, d))]

    # Loop through each directory
    for directory in directories:
        # Construct the path to the csv file in each directory
        csv_path = glob.glob(os.path.join(main_directory, directory, 'forecast*.csv'))[0]
        
        # Check if the file exists
        if os.path.isfile(csv_path):
            # Read the csv file into a pandas DataFrame with datetime as the index
            df = pd.read_csv(csv_path, index_col=0)
            df.index = pd.to_datetime(df.index, utc=True).tz_localize(None)

            # Extract data within the datetime range of the specific directory
            start_date = df.index.min()
            end_date = df.index.max()

            # Extract data from the reference DataFrame within the datetime range
            reference_subset = reference_df.loc[start_date:end_date]

            # Combine the extracted data with the reference data
            combined_df = pd.concat([reference_subset, df], axis=1)
            combined_df.index.name = 'datetime'

            # Save the combined DataFrame as a CSV with the start date as the name
            output_csv_name = os.path.join(output_directory, f"{start_date.strftime('%Y%m%d')}.csv")
            combined_df.to_csv(output_csv_name)

            # # Display or perform operations on the combined data
            # print(f"Directory: {directory}")
            # print(combined_df.head())  # Display the first few rows of the combined DataFrame
            # # Add any further processing or analysis based on your requirements
            # print("\n" + "="*40 + "\n")

        del df
    
    del reference_df

    # Define the path to the directory containing CSV files
    directory_path = '/media/windows/projects/aa-data-driven/paper/03_icon/testing/output/{basin}/{subbasin}/{release}/merged/'

    directory_path = directory_path.format(
        basin = basin,
        subbasin = meta[0],
        release = "R"+str(release).zfill(3)
    )

    # Get a list of all files in the directory
    files = os.listdir(directory_path)

    # Initialize lists to store evaluation metrics for each file
    csv_names = []
    r_squared_list = []
    mae_list = []
    mape_list = []
    dataset_lengths = []

    # Loop through each file in the directory
    for file in files:
        # Construct the path to the CSV file
        csv_path = os.path.join(directory_path, file)

        # Check if the file is a CSV file
        if file.lower().endswith('.csv'):

            try:
                # Read the CSV file into a pandas DataFrame
                df = pd.read_csv(csv_path, index_col=0, parse_dates=True)

            
                # Extract 'values' and 'predicted' columns
                values = df['values']
                predicted = df['predicted']

            
                # Calculate R-squared
                r_squared = r2_score(values, predicted)
                r_squared_list.append(r_squared)

                # Calculate Mean Absolute Error (MAE)
                mae = mean_absolute_error(values, predicted)
                mae_list.append(mae)

                # Calculate Mean Absolute Percentage Error (MAPE)
                mape = np.mean(np.abs((values - predicted) / values)) * 100
                mape_list.append(mape)
            except:
                continue

            # Store CSV name for indexing in the results DataFrame
            csv_names.append(file[:8])

    # Calculate overall MAE and MAPE
    csv_names.insert(0,'OVERALL')
    mae_list.insert(0,np.mean(mae_list))
    mape_list.insert(0,np.mean(mape_list))

    # Create a DataFrame with the results
    results_df = pd.DataFrame({
        # 'R-squared': r_squared_list,
        'MAE': mae_list,
        'MAPE': mape_list
    }, index=csv_names)

    # Save the results to a CSV file
    results_csv_path = os.path.join(output_directory, 'metrics.csv')
    results_df.to_csv(results_csv_path)