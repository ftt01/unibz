## ICON-D2 evaluation

### STEP 1: creation of the data sets

#### kriging data set
1. `preprocess.ipynb`
   a. input: merged data from the stations, updated metadata file, output directory
   b. output: stations data in files with id_internal.csv name and directory standard organization
   c. creation of the grid.json for each variable, to use it as future metadata [to add in the JSON configuration file for `run_kriging.ipynb`]

1. `run_kriging.ipynb`
   a. input: ***internal_id.csv*** for each station, JSON configuration file [containing the grid of points for KR(or stations for CV) to run over, the configuration parameters file path, the kriging setup, ..]
   b. output: a CSV file of the computed kriging value for each point + statistics if CV mode is used and the configuration file enable it

2. `analyze_data.ipynb`
   a. read the output of kriging model given by `run_kriging.ipynb`
<!-- 3.2 read the output of observation data given by `preprocess.ipynb` -->
   b. read the same input of observation data read by `preprocess.ipynb`
   c. read the forecasting data from the `extract_forecast.ipynb` output and save again in the hydrological model format input
   d. ... # TODO

### forecasting data set
1. `extract_forecast.ipynb`
   a. input: configuration of forecast (lead time, init_ref, ...); start date and end date, the ***output.csv*** files from the forecasting postprocessing
   b. output: for each point in the grid metadata *point.csv* a file containing the forecasting data as mean, median, quantiles [as selected at the configuration part 1.1]
   
### data analysis
1. `analyze_data.ipynb`
   a. extract the kriging data to a dataframe: create for each variable a dataframe with datetime as index and all the points in the grid metadata as columns
   b. extract the forecasting data to a dataframe: create for each variable a dataframe with initialization dates as index and all the points in the grid metadata as columns

### ICHYMOD model
1. `preprocess.ipynb` 