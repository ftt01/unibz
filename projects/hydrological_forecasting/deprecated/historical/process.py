import subprocess
from argparse import ArgumentParser
from sys import path as syspath
import json

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
syspath.insert( 0, lib_dir )

from lib import send_email

subbasins = ['SB001']
# subbasins = ['SB001','SB002','SB003','SB004','SB005','SB006','SB007','SB008']
releases = [3]
# releases = [0,3,6,9,12,15,18,21]

errors = []
for s in subbasins:

    for r in releases:

        rel = 'R' + str(r).zfill(3)

        try:
            parser = ArgumentParser()
            parser.add_argument('basepath', type=str)
            parser.add_argument('release', type=str)
            parser.add_argument('basin', type=str)
            parser.add_argument('subbasin', type=str)
            parser.add_argument('parameters', type=str)
            parser.add_argument('input', type=str)
            parser.add_argument('output', type=str)

            args = parser.parse_args()
            basepath = args.basepath
            c_release = args.release
            basin = args.basin
            subbasin = args.subbasin
            json_parameters_pathname = args.parameters
            c_input = args.input
            c_output = args.output
        except:
            basepath = '/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/bias/historical/'
            c_release = rel
            basin = 'B001'
            subbasin = s
            json_parameters_pathname = '/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/bias/historical/parameters.json'
            c_input = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/data/bias/inputs/"
            c_output = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/data/bias/outputs/"

        ## bias correction module
        cmd = "Rscript {basepath}bias_module_historical.R \
                -w {basepath} -r {release} \
                    -b {basin} -s {subbasin} -p {params} \
                        -i {input} -o {output}".format(
                    basepath=basepath,
                    release=c_release,
                    basin=basin,
                    subbasin=subbasin,
                    params=json_parameters_pathname,
                    input=c_input,
                    output=c_output
            )
        print(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            errors.append( ((s,r),str(stderr.decode('utf-8'))) )

if len(errors) > 0:
    send_email(
        subject="hydrological_forecasting | ERROR: bias module not completed",
        body="Errors: " + [ '''On {subbasin} at {release} got error {err}'''.format(
            subbasin=e[0][1],
            release=e[0][2],
            err=e[1]
        ) for e in errors ]
    )
else:
    send_email(
        subject="hydrological_forecasting | BIAS EXECUTED!",
        body="Execution of the bias correction completed following the below configuration.".format(subbasin=s) +
            "\nConfiguation file: " + json.dumps(json_parameters_pathname, indent=2, default=str)
    )