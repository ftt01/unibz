import sys
import subprocess
import json
import pandas as pd

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )

from lib import *

conf_file = "/home/daniele/documents/github/ftt01/phd/metadata/basins/alto_adige.json"

with open(conf_file, 'r') as config_file:
    configuration = json.load(config_file)
    config_file.close()

def create_winter(filein, output_filepath):
    c_df = pd.read_csv(filein)
    c_df = c_df.loc[(c_df.index.month >= 11) and (c_df.index.month <= 2)]

    ###### TO DO

basins = configuration['basins']
for b in basins:
    prec_path = b['training']['precipitation']['path']
    temp_path = b['training']['temperature']['path']
    flow_path = b['training']['streamflow']['path']

    prec_basepath = parent_directory(prec_path)
    temp_basepath = parent_directory(temp_path)
    flow_basepath = parent_directory(flow_path)

    new_prec_path = prec_basepath + 'winter' + extract_filename(prec_path)
    new_temp_path = temp_basepath + 'winter' + extract_filename(temp_path)
    new_flow_path = flow_basepath + 'winter' + extract_filename(flow_path)