### run a training overall
<!-- python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/ml/training/run_process.py -p /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/ -r /home/daniele/documents/github/ftt01/phd/metadata/basins/B001.json
#### on seasons
python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/ml/training/run_process.py -p /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/ -r /home/daniele/documents/github/ftt01/phd/metadata/basins/B001.json -s winter
python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/ml/training/run_process.py -p /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/ -r /home/daniele/documents/github/ftt01/phd/metadata/basins/B001.json -s spring
python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/ml/training/run_process.py -p /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/ -r /home/daniele/documents/github/ftt01/phd/metadata/basins/B001.json -s summer -->

### to run the grid search
1. setup the JSON into the script [TODO]: export the JSON outside
2. specify the subbasins in the roi_config
3. run the script as follow:
    <code>python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/ml/training/run_process.py --gridsearch -p /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/resources/ml/training/ -r /home/daniele/documents/github/ftt01/phd/metadata/basins/phd/B003.json</code>

### to run the training using the grid search results
1. simply run the script with the specification of the JSON conf to use for train the models:
    <code>python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/ml/training/run_process.py --no-gridsearch -p /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/resources/ml/training/ -n 20231214152330</code>