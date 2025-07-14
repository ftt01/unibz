import subprocess

subprocess.call("passirio_precipitation_lapse_rate_kriging1x1.py", shell=True)
subprocess.call("passirio_precipitation_lapse_rate_kriging11x8.py", shell=True)
subprocess.call("passirio_precipitation_lapse_rate_reanalysis11x8.py", shell=True)

subprocess.call("AA_precipitation_lapse_rate_kriging1x1.py", shell=True)
subprocess.call("AA_precipitation_lapse_rate_kriging11x8.py", shell=True)
subprocess.call("AA_precipitation_lapse_rate_reanalysis11x8.py", shell=True)