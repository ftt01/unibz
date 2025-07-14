## dev: to run a docker with RStudio using rocker/tidyverse

### to run the docker
<pre><code>docker-compose up hydrological_forecasting_r_debug</code></pre>

## prod: to run a stand-alone image using rocker/r-base

### to build the docker
<pre><code>docker-compose build hydrological_forecasting_r_prod</code></pre>

### to run the docker
<pre><code>docker run hydrological_forecasting_r_prod</code></pre> 

cdo -f grb2 -sellonlatbox,6.5,14.5,44,47.5 in.grib2 out.grib2