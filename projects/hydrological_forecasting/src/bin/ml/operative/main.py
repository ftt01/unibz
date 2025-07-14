#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser
from sys import path as syspath

try:
    parser = ArgumentParser()
    parser.add_argument('repo_path', type=str)
    parser.add_argument('--configuration_file', dest='conf_file', type=str, required=True)
    parser.add_argument('--roi_config', dest='roi_config', type=str, required=True)
    parser.add_argument('--subbasin', dest='subbasin', type=str, required=True)
    parser.add_argument('--start_date', dest='start_date', type=str, required=False)
    parser.add_argument('--end_date', dest='end_date', type=str, required=False)
    args = parser.parse_args()
except:
    class local_args():

        def __init__(self) -> None:
            pass

        def add_repo_path(self,  repo_path):
            self.repo_path = repo_path

        def add_conf_file(self,  conf_file):
            self.conf_file = conf_file
        
        def add_subbasin(self,  subbasin):
            self.subbasin = subbasin

        def add_start_date(self,  start_date):
            self.start_date = start_date
        
        def add_end_date(self,  end_date):
            self.end_date = end_date
        
        def add_roi_config(self,  roi_config):
            self.roi_config = roi_config
       
    args = local_args()
    args.add_repo_path("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/")
    args.add_conf_file("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/ml/operative/vernago.json")
    args.add_subbasin("SB003")
    args.add_start_date("20211215")
    args.add_end_date("20211230")
    args.add_roi_config("/media/windows/projects/hydro_forecasting/vernago/training/output/metadata/20231214152330.json")

lib_dir = args.repo_path + "resources/"
syspath.insert( 0, lib_dir )
from local_lib import *

###############################################################################

cmd_preprocess = "python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/ml/operative/preprocess.py --configuration_file {preprocess_json} --subbasin {subbasin} --roi_config {roi_config}".format(
    preprocess_json = args.conf_file,
    subbasin = args.subbasin,
    roi_config = args.roi_config
)
if args.start_date != None:
    cmd_preprocess = cmd_preprocess + " --start_date " + args.start_date
    if args.end_date != None:
        cmd_preprocess = cmd_preprocess + " --end_date " + args.end_date

preprocess = subprocess.Popen( cmd_preprocess, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = preprocess.communicate()

###############################################################################

if preprocess.returncode != 0:
    send_email(
        subject="hydro_forecast | ML PreProcess FAILED",
        body="Error: " + str(stderr.decode('utf-8'))
    )
else:
    cmd = "python3 /home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/src/bin/ml/operative/process.py {repo_path} {conf_file} --subbasin {subbasin}".format(
        repo_path = args.repo_path,
        conf_file = args.conf_file,
        subbasin = args.subbasin)

    if args.start_date != None:
        cmd = cmd + " --start_date " + args.start_date
        if args.end_date != None:
            cmd = cmd + " --end_date " + args.end_date

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        
        send_email(
            subject="hydro_forecast | ML Process FAILED",
            body="Error: " + str(stderr.decode('utf-8'))
        )