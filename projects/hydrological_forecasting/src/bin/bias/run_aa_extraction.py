import sys
import subprocess
import json

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )

from lib import send_email

conf_file = "/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/bias/pp/input_AA_data.json"

cmd = "cd /home/daniele/documents/github/ftt01/phd/data/meteo/providers/meteoaltoadige/src/bin/ && python3 extraction_data.py {conf_file} start_day"
process = subprocess.Popen(cmd.format(conf_file=conf_file), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

if process.returncode != 0:
    with open(conf_file) as config_file:
        configuration = json.load(config_file)

        send_email(
            subject="hydrological_forecasting | ERROR: Meteo AltoAdige for bias module NOT extracted",
            body="Error: " + str(stderr.decode('utf-8')) + \
                "\nConfiguation file: " + json.dumps(configuration, indent=2, default=str)
        )

        config_file.close()