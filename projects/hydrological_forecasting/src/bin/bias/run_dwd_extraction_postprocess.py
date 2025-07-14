import sys
import subprocess
import json
import glob

from multiprocessing import Pool
from multiprocessing import cpu_count

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )

from lib import send_email

def process(conf_file):
    cmd = "cd /home/daniele/documents/github/ftt01/phd/data/meteo/providers/dwd/src/bin/extract/ && python3 extract_data.py -c {conf_file}"
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

# conf_files = glob.glob("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/bias/pp/postprocess/input_DWD_*.json")
conf_files = glob.glob("/home/daniele/documents/github/ftt01/phd/projects/hydrological_forecasting/etc/conf/bias/alto_adige/icon/postprocess/input_DWD_*.json")

if __name__ == "__main__":
    pool = Pool(cpu_count())
    results = pool.map(process, conf_files)
    pool.close()  # 'TERM'
    pool.join()   # 'KILL'