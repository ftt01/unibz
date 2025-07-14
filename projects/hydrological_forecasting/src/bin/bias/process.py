import subprocess
from argparse import ArgumentParser
from sys import path as syspath
import json
import datetime as dt
import pandas as pd

### logging
logging_level = "DEBUG"

### dates
# running_dates = [dt.datetime.today()]
running_dates = pd.date_range(
    dt.datetime.strptime('20230819', '%Y%m%d'), dt.datetime.strptime('20230820', '%Y%m%d')
    ).tolist()

### releases
releases = [
    'R000',
    'R003',
    'R006',
    'R009',
    'R012',
    'R015',
    'R018',
    'R021'
    ]

### basins
basins = [
    'B001'
    ]

### subbasins
subbasins = [
    'SB010'
    ]

input_path = "/media/windows/projects/hydro_forecasting/bias_correction/input/"
output_path = "/media/windows/projects/hydro_forecasting/bias_correction/output/"

for b in basins:
    for sb in subbasins:

        for c_date in running_dates:

            ### process
            # basepath = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/"
            # json_setup = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/bias/operative/parameters.json"

            ## loop over releases
            for c_rls in releases:

                print( "date: " + str(c_date) )
                print( "release: " + c_rls )
                # print( "json_parameters: " + json_setup )

                cmd = "docker run --rm \
                    --name rbias_online \
                    -v {input_path}:/home/rstudio/data/input/ \
                    -v {output_path}:/home/rstudio/data/output/ \
                    aiaqua/rbias_online:3.0.0 \
                    -b /home/rstudio/src/ -d {c_date} -r {release} -b {basin} -s {subbasin} -p /home/rstudio/etc/conf/parameters.json -v {loglevel} -m /home/rstudio/data/input/icon/postprocessed/".format(
                        input_path=input_path,
                        output_path=output_path,
                        c_date=c_date.strftime("%Y%m%d"),
                        release=c_rls,
                        basin=b,
                        subbasin=sb,
                        loglevel=logging_level
                    )
                print(cmd)
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()