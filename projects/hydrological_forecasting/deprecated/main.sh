#!/bin/bash

cd /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/bin

python3 extract_observed.py
# python3 delete_useless.py
# python3 extract_forecast.py
python3 comparison_biased.py
python3 fullfill_forecast_obs.py
python3 apply_temperature_bias.py
python3 apply_precipitation_bias.py
python3 extract_to_obs.py
python3 comparison_unbiased.py
python3 extract_to_ML.py