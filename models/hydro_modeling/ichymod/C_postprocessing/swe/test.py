from lib import *

### simulation selection #############################################################################

current_phase = "best_merano_swe"
current_basin = "passirio"
current_type = "kriging_11"
current_node = "merano"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, \
        sca_passirio, swe1, swe2, swe3, swe4, swe5 = retrieveSimulated( configPath, \
        current_phase, current_basin, current_type, current_node)