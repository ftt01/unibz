#!/usr/bin/env python
# coding: utf-8

# In[2]:
import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )


# In[3]:
from lib import *
from sklearn.linear_model import LinearRegression
from scipy.stats import skewnorm


# In[4]:
import logging

# In[7]:
wdir = "/home/daniele/documents/github/ftt01/phd/projects/era5_evaluation/"
output_path = "/media/windows/projects/era5_bias/01_preprocessing/"


# In[8]:
## SETUP
basin = 'AltoAdige'
output_path = output_path + "meteo/" + basin + "/fake/"
mkNestedDir(output_path)
output_log = '''{output_path}/temperature_lapse_rate_new.log'''

### create an array of values for precipitation along a linear regression curve
def generate_random_nonuniform(start, end, count):
    

    # Generate random samples from the skew-normal distribution
    random_nonuniform = skewnorm.rvs(a=10, loc=0, scale=0.5, size=count)
    random_nonuniform = abs(random_nonuniform)
    random_nonuniform = random_nonuniform / max(random_nonuniform)
    random_nonuniform = random_nonuniform * (end - start) + start
    # random_nonuniform = np.clip(random_nonuniform, start, end)
    return random_nonuniform.tolist()

# Example usage
start = 250  # Starting value
end = 3500  # Ending value
counts = np.arange(5,200,2)  # Number of random nonuniform numbers to generate

for count in counts:

    elevation = generate_random_nonuniform(start, end, count)

    epsilon = 0.1  # Epsilon value for random noise
    elevs = []
    temps = []
    for e in elevation:
        elevs.append(e)
        temps.append(
            np.random.uniform(-2,20) - (4 * (e-start)/1000) + np.random.uniform(-epsilon, epsilon)
        )

    # Example data
    x = np.array(temps)
    y = np.array(elevs)

    # Fit linear regression
    regression = LinearRegression()
    regression.fit(x.reshape(-1, 1), y)

    # Get slope and intercept
    slope = regression.coef_[0]
    intercept = regression.intercept_

    # Calculate residuals
    y_predicted = regression.predict(x.reshape(-1, 1))
    residuals = y - y_predicted

    # Calculate RMSE
    rmse = np.sqrt(np.mean(residuals ** 2))

    # Define range of RMSE
    rmse_range = 800

    # Generate random samples within the RMSE range
    random_nonuniform = skewnorm.rvs(a=10, loc=0, scale=0.5, size=len(x))
    random_nonuniform = abs(random_nonuniform)
    random_nonuniform = random_nonuniform / max(random_nonuniform)
    random_samples = random_nonuniform * rmse_range

    # # Add random samples to predicted y-values
    elevs = y_predicted + random_samples

    fig, axs = instantiatePlot( "Temperature $[Celsius]$","Elevation $[m]$", height=60, width=60, plot_legend=False )

    axs.scatter( temps, elevs, s=10 ) 

    z1 = np.polyfit( temps, elevs, 1 )
    p1 = np.poly1d( z1 )

    elevations = elevs
    temperatures = np.arange(min(temps)-epsilon,max(temps)+epsilon,5)
    axs.plot( temperatures, p1(temperatures), "r--" )

    axs.set_xlim([min(temperatures)-epsilon,max(temperatures)+epsilon])
    axs.set_ylim([min(elevations),max(elevations)])

    # axs.set_xticks([min(temperatures)-epsilon,np.mean(temperatures),max(temperatures)+epsilon])
    # axs.set_yticks([1000,1500,2000,2500], a='center')
    axs.yaxis.set_tick_params(labelrotation=90)

    output_file_hd = output_path + 'meteo_' + basin + f'_temperature_over_elevation_{count}_hd.' + output_format

    mkNestedDir(getPathFromFilepath(output_file_hd))
    fig.savefig( output_file_hd, format=output_format, bbox_inches='tight', facecolor='w', dpi=400 )
