import datetime as dt
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

###### BASE PATHS ####################################################################################

configPath = "C:\\Users\\daniele\\Documents\\GitHub\\ftt01\\phd\\hydro_modeling\\A_preprocessing\\a_precipitation_lapse_rate\\"

with open(configPath + 'config.json') as config_file:
    config = json.load(config_file)

###### SETUP PLOTS ###################################################################################
 
plt.style.use('C:\\Users\\daniele\\Documents\\GitHub\\ftt01\\phd\\ITstuff\\python\\matplotlib\\template.mplstyle')

#my_dpi = 600
output_format = 'png'

#width = 90
#height = 60

#tick_size=10
#label_size=10
#legend_fontsize=8
#ratio_width=190
#ratio=3740/500

######################################################################################################

def mkNestedDir(dirTree):
    from pathlib import Path
    Path(dirTree).mkdir(parents=True, exist_ok=True)

def getPathFromFilepath(existGDBPath):
    import os
    return os.path.dirname(os.path.abspath(existGDBPath))

def createBoxPlot( df_in, x_label, y_label, output_file, \
    x_major_locator=None, x_major_formatter=None, \
    output_format="pdf", xscale="linear", yscale="linear", \
    width=190, height=90, period="MS", scale_factor=1, \
    tick_size=10, label_size=10, legend_fontsize=8, \
    ratio_width=190, ratio=3740/500, my_dpi=500 ):

    if period == "MS":
        import matplotlib.ticker as ticker
        x_major_locator=ticker.MultipleLocator(1)
        x_labels = range(1,12+1)
        x_major_formatter=ticker.FuncFormatter(lambda x, _: dict(zip(range(len(x_labels)), x_labels)).get(x, ""))
    elif period == "H":
        import matplotlib.ticker as ticker
        x_major_locator=ticker.MultipleLocator(2)
        x_labels = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
        x_major_formatter=ticker.FuncFormatter(lambda x, _: dict(zip(range(len(x_labels)), x_labels)).get(x, ""))
        
    plot_x_inches = ratio / ratio_width * width
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
        figsize = [plot_x_inches, plot_y_inches],
        tight_layout = {'pad': 0},
        dpi=my_dpi
    ) 

    #add data and data_label to legend
    from seaborn import boxplot
    if period == "MS":
        boxplot(x=df_in.index.month, y=df_in.values, ax=axs)
    elif period == "D":
        boxplot(x=df_in.index.daily, y=df_in.values, ax=axs)
    elif period == "H":
        boxplot(x=df_in.index.hour, y=df_in.values, ax=axs)

    axs.tick_params( labelsize=tick_size/scale_factor )

    axs.set_xscale( xscale )
    axs.set_yscale( yscale )

    axs.set_ylabel( y_label, fontsize=label_size/scale_factor )
    axs.set_xlabel( x_label, fontsize=label_size/scale_factor )
    
    if x_major_locator != None:
        axs.xaxis.set_major_locator(x_major_locator)

    if x_major_formatter != None:
        axs.xaxis.set_major_formatter(x_major_formatter)

    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=my_dpi )

    plt.close(fig=fig)

def instantiatePlot( x_label, y_label, \
    output_format='png', xscale="linear", yscale="linear", \
    width=190, height=90, scale_factor=1, \
    tick_size=10, label_size=10, legend_fontsize=8, \
    ratio_width=190, ratio=3740/500, my_dpi=600 ):

    plot_x_inches = ratio / ratio_width * width 
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
        figsize = [plot_x_inches, plot_y_inches],
        tight_layout = {'pad': 0},
        dpi = my_dpi
    )

    axs.tick_params( labelsize=tick_size/scale_factor )
    
    axs.set_xscale( xscale )
    axs.set_yscale( yscale )

    axs.set_ylabel( y_label, fontsize=label_size/scale_factor )
    axs.set_xlabel( x_label, fontsize=label_size/scale_factor )
    axs.legend(fontsize=legend_fontsize/scale_factor)

    return fig, axs

def createPlot( plots, x_label, y_label, output_file, \
    x_major_locator=None, x_major_formatter=None, \
    output_format='png', xscale="linear", yscale="linear", \
    width=190, height=90, scale_factor=1, \
    tick_size=10, label_size=10, legend_fontsize=8, \
    ratio_width=190, ratio=3740/500, my_dpi=600 ):

    plot_x_inches = ratio / ratio_width * width 
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(1,
        figsize = [plot_x_inches, plot_y_inches],
        tight_layout = {'pad': 0},
        dpi = my_dpi
    )

    axs.tick_params( labelsize=tick_size/scale_factor )
    
    axs.set_xscale( xscale )
    axs.set_yscale( yscale )

    axs.set_ylabel( y_label, fontsize=label_size/scale_factor )
    axs.set_xlabel( x_label, fontsize=label_size/scale_factor )
    
    if x_major_locator != None:
        axs.xaxis.set_major_locator(x_major_locator)

    if x_major_formatter != None:
        axs.xaxis.set_major_formatter(x_major_formatter) 
    
    #add data and data_label to legend
    for tp in plots:

        label=None
        linestyle="solid"

        if "label" in tp[1].keys():
            label=tp[1]["label"]
        
        if "linestyle" in tp[1].keys():
            linestyle=tp[1]["linestyle"]

        axs.plot(tp[0], label=label, linestyle=linestyle)
    
    axs.legend(fontsize=legend_fontsize/scale_factor)
    
    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig( output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=my_dpi )
    plt.close(fig=fig)

def evaluateECDF( data_to_use ):
    data = np.sort( data_to_use )

    # calculate the proportional values of samples
    norm_cdf = 100. * np.arange(len(data)) / (len(data) - 1)

    data = pd.DataFrame(data, columns=["data"])
    cdf = pd.DataFrame(norm_cdf, columns=["cdf"])

    ecdf_frame = pd.concat([data, cdf], axis=1)
    ecdf_frame.set_index('data', inplace=True) 

    return ecdf_frame

def rewriteDF( df ):
    '''This function takes a dataframe with white spaces as separator, first column as date (%Y-%m-%d) and
    second column as day (%h). It returns a dataframe with index the date and hour (%Y-%m-%dT%H:%M%S)'''

    import pandas as pd
    from datetime import timedelta

    date_time = []
    for i in range(len(df)):
        hour = df[i:i+1]["date"][0]
        #print(hour)
        date = pd.to_datetime(df[i:i+1].index[0])
        #print(date)

        if hour == 24:
            date_updated = date.replace(hour=0)
            date_updated = date_updated + timedelta(days=-1)
        else:
            date_updated = date.replace(hour=hour)
        #print(date_updated)
        date_time.append(date_updated)

    df.set_index(np.array(date_time), drop=True, inplace=True)
    df.drop("date", inplace=True, axis=1)

    return df

