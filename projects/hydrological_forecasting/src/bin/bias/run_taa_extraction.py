import sys
import subprocess
import json

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )

from lib import send_email

conf_file = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/bias/input_taa.json"

cmd = "cd /home/daniele/documents/github/ftt01/phd/data/meteo/providers/dwd/src/bin/extract/ && python3 extract_data.py {conf_file}"
process = subprocess.Popen(cmd.format(conf_file=conf_file), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if process.returncode != 0:
    send_email(
        subject="ERROR: DWD for hydro_forecasting NOT extracted",
        body="Error: " + str(stderr.decode('utf-8')[:100])
    )
else:
    with open(conf_file) as config_file:
        configuration = json.load(config_file)
        
        send_email(
            subject="DWD for hydro_forecasting data EXTRACTED!",
            body="Successfully updated following the below config file.\n" + json.dumps(configuration, indent=2, default=str)
        )
        config_file.close()