from sys import path as syspath
locallib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib/"
syspath.insert( 0, locallib_dir )
from lib import pd

### BASIN 25
temp_data = pd.read_csv("/media/windows/projects/aa-data-driven/lombardi/tesi/data/data_bacini/25/meteo_temp_c_KNN_c.csv")
temp_ids = temp_data.columns[1:-1].tolist()

prec_data = pd.read_csv("/media/windows/projects/aa-data-driven/lombardi/tesi/data/data_bacini/25/meteo_prec_c_KNN_c.csv")
prec_ids = prec_data.columns[1:-1].tolist()

flow_data = pd.read_csv("/media/windows/projects/aa-data-driven/lombardi/tesi/data/data_bacini/25/.csv")
flow_ids = flow_data.columns[1:-1].tolist()