from lib import *

### simulation selection #############################################################################

current_phase = "calibration_best_plan"
current_basin = "passirio"
current_type = "kriging"
current_node = "plan"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, \
        sca_passirio, swe1, swe2, swe3 = retrieveSimulated( configPath, \
        current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
swe1_monthly_mean = swe1.resample('MS').mean()