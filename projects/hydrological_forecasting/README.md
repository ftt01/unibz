## To run the extraction in python
1. go to the *bin* directory
2. run the command with 3 arguments:
    - path [-p] where to find the specific directory to run
    - initial lead time [-l] from which to start the extraction
    - variable [-var] tot_prec or t_2m

    example: python3 extract_icon-d2-eps.py -p /mnt/e/projects/hydrological_forecasting/machine_learning/data/forecast/icon-d2-eps_45h/custom/running/tmp/20210823/ -l 15 -var tot_prec

## To run the ML
### time to execute
run_dwd_module 140s/day/basin

### steps
1. download the data from the AA API
**description**: check all available stations data, download and append to the local copy
**cmd**: python3 /home/daniele/documents/github/ftt01/phd/data/meteo/providers/meteoaltoadige/src/bin/run_download.py
**timing**: 10min/all stations
**comments**: run on all the stations every day at 9AM

2. extract the DWD data
**description**: cut to a ROI, extract on subbasins using a spatial mean or ensemble
**cmd**: python3 /home/daniele/documents/github/ftt01/phd/data/meteo/providers/dwd/src/bin/run_dwd_extraction.py
**timing**: ??
**comments**: after the first time just run on the today data!

3. extract the data to run the bias script + run the bias script
**description**: extract the data of the last days, run the operative code for bias. This starts from the .Rdata and add the last run that add the information to the RData and it apply bias correction to the date indicated in starter.json 
**cmd**: python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/full_chain/run_bias_module.py
**timing**: ??
**comments**: to run the ML model trained is necessary to use just the last lagged data and the today forecasting. 

4. preprocess the data for ML module
**description**: extract the streamflow data as temperature/precipitation format, save these data to the same directory. Then the preprocessing of the data starts and the combination of historical data (based on lag) and the forecasting data is joined in a timeseries for each day.
**cmd**: python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/full_chain/run_ML_preprocess.py
**timing**: ??
**comments**: Is necessary to have all the historical data covering the lag.

5. run the ML module to produce the results
**description**: 
**cmd**: python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/full_chain/run_ML_module.py
**timing**: ??
**comments**: 