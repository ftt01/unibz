import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Step 1: Load the DataFrames
df1 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_hour/p_orig_mae.csv')  # Replace with your file names
df2 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_hour/p_MBCn_mae.csv')
df3 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_hour/p_DTR_mae.csv')

# Step 2: Extract relevant columns
# Assuming the first column is 'ID', the fourth is 'Elevation', and the fifth is 'MAE'
# Column indices start from 0, so we use 0 for the first column, 3 for the fourth, and 4 for the fifth

elevation1 = df1.iloc[:, 3]
mae1 = df1.iloc[:, 4]

elevation2 = df2.iloc[:, 3]
mae2 = df2.iloc[:, 4]

elevation3 = df3.iloc[:, 3]
mae3 = df3.iloc[:, 4]

# Step 3: Plot the data
plt.figure(figsize=(10, 6))

plt.scatter(mae1, elevation1, label='Original', marker='o')
plt.scatter(mae2, elevation2, label='MBCn', marker='s')
plt.scatter(mae3, elevation3, label='DTR', marker='^')

# Adding labels and legend
plt.xlabel('MAE')
plt.ylabel('Elevation')
plt.title('Elevation vs MAE - hourly precipitation')
plt.legend()

# Show plot
plt.grid(True)

plt.savefig('/media/windows/projects/bias_correction/comparison/30years/Fig/precipitation_elevation_vs_mae_hour.png')  
# plt.show()



# Step 1: Load the DataFrames
df1 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_hour/t_orig_mae.csv')  # Replace with your file names
df2 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_hour/t_MBCp_mae.csv')
df3 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_hour/t_XGB_mae.csv')

# Step 2: Extract relevant columns
# Assuming the first column is 'ID', the fourth is 'Elevation', and the fifth is 'MAE'
# Column indices start from 0, so we use 0 for the first column, 3 for the fourth, and 4 for the fifth

elevation1 = df1.iloc[:, 3]
mae1 = df1.iloc[:, 4]

elevation2 = df2.iloc[:, 3]
mae2 = df2.iloc[:, 4]

elevation3 = df3.iloc[:, 3]
mae3 = df3.iloc[:, 4]

# Step 3: Plot the data
plt.figure(figsize=(10, 6))

plt.scatter(mae1, elevation1, label='Original', marker='o')
plt.scatter(mae2, elevation2, label='MBCp', marker='s')
plt.scatter(mae3, elevation3, label='XGB', marker='^')

# Adding labels and legend
plt.xlabel('MAE')
plt.ylabel('Elevation')
plt.xticks([i for i in np.arange(13)])
plt.title('Elevation vs MAE - hourly temperature')
plt.legend()

# Show plot
plt.grid(True)

plt.savefig('/media/windows/projects/bias_correction/comparison/30years/Fig/temperature_elevation_vs_mae_hour.png')  
# plt.show()

#################################

# Step 1: Load the DataFrames
df1 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_day/p_orig_mae.csv')  # Replace with your file names
df2 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_day/p_MBCn_mae.csv')
df3 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_day/p_DTR_mae.csv')

# Step 2: Extract relevant columns
# Assuming the first column is 'ID', the fourth is 'Elevation', and the fifth is 'MAE'
# Column indices start from 0, so we use 0 for the first column, 3 for the fourth, and 4 for the fifth

elevation1 = df1.iloc[:, 3]
mae1 = df1.iloc[:, 4]

elevation2 = df2.iloc[:, 3]
mae2 = df2.iloc[:, 4]

elevation3 = df3.iloc[:, 3]
mae3 = df3.iloc[:, 4]

# Step 3: Plot the data
plt.figure(figsize=(10, 6))

plt.scatter(mae1, elevation1, label='Original', marker='o')
plt.scatter(mae2, elevation2, label='MBCn', marker='s')
plt.scatter(mae3, elevation3, label='DTR', marker='^')

# Adding labels and legend
plt.xlabel('MAE')
plt.ylabel('Elevation')
plt.title('Elevation vs MAE - daily precipitation')
plt.legend()

# Show plot
plt.grid(True)

plt.savefig('/media/windows/projects/bias_correction/comparison/30years/Fig/precipitation_elevation_vs_mae_day.png')  
# plt.show()



# Step 1: Load the DataFrames
df1 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_day/t_orig_mae.csv')  # Replace with your file names
df2 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_day/t_MBCp_mae.csv')
df3 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_day/t_XGB_mae.csv')

# Step 2: Extract relevant columns
# Assuming the first column is 'ID', the fourth is 'Elevation', and the fifth is 'MAE'
# Column indices start from 0, so we use 0 for the first column, 3 for the fourth, and 4 for the fifth

elevation1 = df1.iloc[:, 3]
mae1 = df1.iloc[:, 4]

elevation2 = df2.iloc[:, 3]
mae2 = df2.iloc[:, 4]

elevation3 = df3.iloc[:, 3]
mae3 = df3.iloc[:, 4]

# Step 3: Plot the data
plt.figure(figsize=(10, 6))

plt.scatter(mae1, elevation1, label='Original', marker='o')
plt.scatter(mae2, elevation2, label='MBCp', marker='s')
plt.scatter(mae3, elevation3, label='XGB', marker='^')

# Adding labels and legend
plt.xlabel('MAE')
plt.ylabel('Elevation')
plt.xticks([i for i in np.arange(13)])
plt.title('Elevation vs MAE - daily temperature')
plt.legend()

# Show plot
plt.grid(True)

plt.savefig('/media/windows/projects/bias_correction/comparison/30years/Fig/temperature_elevation_vs_mae_day.png')  
# plt.show()

##################

# Step 1: Load the DataFrames
df1 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_month/p_orig_mae.csv')  # Replace with your file names
df2 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_month/p_MBCp_mae.csv')
df3 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_month/p_DTR_mae.csv')

# Step 2: Extract relevant columns
# Assuming the first column is 'ID', the fourth is 'Elevation', and the fifth is 'MAE'
# Column indices start from 0, so we use 0 for the first column, 3 for the fourth, and 4 for the fifth

elevation1 = df1.iloc[:, 3]
mae1 = df1.iloc[:, 4]

elevation2 = df2.iloc[:, 3]
mae2 = df2.iloc[:, 4]

elevation3 = df3.iloc[:, 3]
mae3 = df3.iloc[:, 4]

# Step 3: Plot the data
plt.figure(figsize=(10, 6))

plt.scatter(mae1, elevation1, label='Original', marker='o')
plt.scatter(mae2, elevation2, label='MBCp', marker='s')
plt.scatter(mae3, elevation3, label='DTR', marker='^')

# Adding labels and legend
plt.xlabel('MAE')
plt.ylabel('Elevation')
plt.title('Elevation vs MAE - monthly precipitation')
plt.legend()

# Show plot
plt.grid(True)

plt.savefig('/media/windows/projects/bias_correction/comparison/30years/Fig/precipitation_elevation_vs_mae_month.png')  
# plt.show()



# Step 1: Load the DataFrames
df1 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_month/t_orig_mae.csv')  # Replace with your file names
df2 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_month/t_MBCr_mae.csv')
df3 = pd.read_csv('/media/windows/projects/bias_correction/comparison/30years/Fig/fig3_month/t_XGB_mae.csv')

# Step 2: Extract relevant columns
# Assuming the first column is 'ID', the fourth is 'Elevation', and the fifth is 'MAE'
# Column indices start from 0, so we use 0 for the first column, 3 for the fourth, and 4 for the fifth

elevation1 = df1.iloc[:, 3]
mae1 = df1.iloc[:, 4]

elevation2 = df2.iloc[:, 3]
mae2 = df2.iloc[:, 4]

elevation3 = df3.iloc[:, 3]
mae3 = df3.iloc[:, 4]

# Step 3: Plot the data
plt.figure(figsize=(10, 6))

plt.scatter(mae1, elevation1, label='Original', marker='o')
plt.scatter(mae2, elevation2, label='MBCr', marker='s')
plt.scatter(mae3, elevation3, label='XGB', marker='^')

# Adding labels and legend
plt.xlabel('MAE')
plt.ylabel('Elevation')
plt.xticks([i for i in np.arange(13)])
plt.title('Elevation vs MAE - monthly temperature')
plt.legend()

# Show plot
plt.grid(True)

plt.savefig('/media/windows/projects/bias_correction/comparison/30years/Fig/temperature_elevation_vs_mae_month.png')  
# plt.show()