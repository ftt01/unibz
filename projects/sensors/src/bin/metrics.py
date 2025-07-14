import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import os

def getPathFromFilepath(existGDBPath):
    return os.path.dirname(os.path.abspath(existGDBPath))

def mkNestedDir(dirTree):
    os.makedirs(dirTree, exist_ok=True)

def createBoxPlot(df_in, x_label, y_label, output_file, label=None,
                  x_major_locator=None, x_major_formatter=None,
                  output_format="png", xscale="linear", yscale="linear",
                  width=60, height=90, period="MS", scale_factor=1,
                  tick_size=10, label_size=10, legend_fontsize=8,
                  ratio_width=190, ratio=3740/500, my_dpi=500):

    
    import matplotlib.ticker as ticker
    x_major_locator = ticker.MultipleLocator(1)
    x_labels = ['1','3','6','12','24']
    x_major_formatter = ticker.FuncFormatter(lambda x, _: dict(
        zip(range(len(x_labels)), x_labels)).get(x, ""))
    
    plot_x_inches = ratio / ratio_width * width
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(
        1,
        figsize=[plot_x_inches, plot_y_inches],
        tight_layout={'pad': 0},
        dpi=my_dpi
    )

    # add data and data_label to legend
    import seaborn as sns
    PROPS = {
        'boxprops': {'facecolor': 'none', 'edgecolor': 'black', 'linewidth': '1'},
        'medianprops': {'color': 'black', 'linewidth': '1.5'},
        'whiskerprops': {'color': 'black', 'linewidth': '0.75'},
        'capprops': {'color': 'black', 'linewidth': '0.75'}
    }
    # sns.set_style({'style':"whitegrid", 'axes.grid': True})

    df_melted = df_in.melt(var_name='Variable', value_name='Value')

    sns.boxplot(x='Variable', y='Value', data=df_melted,
                ax=axs, **PROPS)

    axs.tick_params(labelsize=tick_size/scale_factor)
    # Define the number of y-ticks
    num_y_ticks = 8
    min_y, max_y = df_in.min().min(), df_in.max().max()
    yticks = np.linspace(min_y, max_y, num_y_ticks)
    axs.set_yticks(yticks)

    axs.set_xscale(xscale)
    axs.set_yscale(yscale)

    axs.set_ylabel(y_label, fontsize=label_size/scale_factor)
    axs.set_xlabel(x_label, fontsize=label_size/scale_factor)

    if label != None:
        axs.text(0.15, 0.15, label, transform=fig.dpi_scale_trans,
                 fontsize=label_size/scale_factor, va='bottom', ha='left')

    if x_major_locator != None:
        axs.xaxis.set_major_locator(x_major_locator)

    if x_major_formatter != None:
        axs.xaxis.set_major_formatter(x_major_formatter)

    # axs.axhline(linewidth=0.5, linestyle="--", color="k")

    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig(output_file, format=output_format,
                bbox_inches='tight', facecolor='w', dpi=my_dpi)

    plt.close(fig=fig)

# Function to remove outliers using the IQR method
def remove_outliers(df):
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[~((df < lower_bound) | (df > upper_bound)).any(axis=1)]

def evaluate_zt(df, index_name, std=None):
    nse_Xh = df.loc[[index_name]]
    if std is None:
        std = np.std(nse_Xh)

    # nse_Xh = remove_outliers(nse_Xh)

    zt = [np.abs(1-nsejt)/std for nsejt in nse_Xh.values[0]]
    
    return zt

def evaluate_metrics(df, std_df):

    zt_1h = evaluate_zt(df, '1', std=std_df.loc['1'])
    zt_3h = evaluate_zt(df, '3', std=std_df.loc['3'])
    zt_6h = evaluate_zt(df, '6', std=std_df.loc['6'])
    zt_12h = evaluate_zt(df, '12h', std=std_df.loc['12h'])
    zt_24h = evaluate_zt(df, '24', std=std_df.loc['24'])

    df_metrics = pd.DataFrame([zt_1h,zt_3h,zt_6h,zt_12h,zt_24h], index=['1h','3h','6h','12h','24h'])
    return df_metrics

def createBarPlot(df_in, x_label, y_label, output_file, 
                  output_format="png", xscale="linear",
                  width=60, height=90, scale_factor=1,
                  tick_size=10, label_size=10, legend_fontsize=8,
                  ratio_width=190, ratio=3740/500, my_dpi=500):
    
    plot_x_inches = ratio / ratio_width * width
    plot_y_inches = ratio / ratio_width * height

    fig, axs = plt.subplots(
        1,
        figsize=[plot_x_inches, plot_y_inches],
        tight_layout={'pad': 0},
        dpi=my_dpi
    )

    # Bar plot style properties
    barprops = {
        'edgecolor': 'black',  # Color of the bar edges
        'linewidth': 1      # Width of the bar edges
        # 'color': 'white'       # Face color of the bars
    }

    # Plot the data with custom styles
    bars = df_in.plot(kind='bar', ax=axs, **barprops)

    # df_in.plot(kind='bar', ax=axs)

    axs.set_xlabel(x_label)
    axs.set_ylabel(y_label)

    axs.legend()

    mkNestedDir(getPathFromFilepath(output_file))
    fig.savefig(output_file, format=output_format, bbox_inches='tight', facecolor='w', dpi=my_dpi)

    plt.close(fig=fig)

## NSE general ##############################

passirio_nse_path = "/media/windows/projects/aa-data-driven/bruno/basins/8/res/bests/metrics_tst.csv"
df_passirio_nse = pd.read_csv(passirio_nse_path, index_col=0)
passirio_nse_1h = df_passirio_nse.loc['1','nse']
passirio_nse_3h = df_passirio_nse.loc['3','nse']
passirio_nse_6h = df_passirio_nse.loc['6','nse']
passirio_nse_12h = df_passirio_nse.loc['12h','nse']
passirio_nse_24h = df_passirio_nse.loc['24','nse']


isarco_nse_path = "/media/windows/projects/aa-data-driven/bruno/basins/21/res/bests/metrics_tst.csv"
df_isarco_nse = pd.read_csv(isarco_nse_path, index_col=0)
isarco_nse_1h = df_isarco_nse.loc['1','nse']
isarco_nse_3h = df_isarco_nse.loc['3','nse']
isarco_nse_6h = df_isarco_nse.loc['6','nse']
isarco_nse_12h = df_isarco_nse.loc['12h','nse']
isarco_nse_24h = df_isarco_nse.loc['24','nse']


adige_nse_path = "/media/windows/projects/aa-data-driven/bruno/basins/25/res/bests/metrics_tst.csv"
df_adige_nse = pd.read_csv(adige_nse_path, index_col=0)
adige_nse_1h = df_adige_nse.loc['1','nse']
adige_nse_3h = df_adige_nse.loc['3','nse']
adige_nse_6h = df_adige_nse.loc['6','nse']
adige_nse_12h = df_adige_nse.loc['12h','nse']
adige_nse_24h = df_adige_nse.loc['24','nse']

nse_df = pd.DataFrame([
    [passirio_nse_1h, passirio_nse_3h, passirio_nse_6h, passirio_nse_12h, passirio_nse_24h],
    [isarco_nse_1h, isarco_nse_3h, isarco_nse_6h, isarco_nse_12h, isarco_nse_24h],
    [adige_nse_1h, adige_nse_3h, adige_nse_6h, adige_nse_12h, adige_nse_24h]
], index=['Passirio', 'Isarco', 'Adige'], columns=['1','3','6','12','24'])

createBarPlot(
    nse_df.T, 
    x_label='Forecast Horizon (hours)', 
    y_label='NSE',
    height=95,
    width=190, 
    output_file="/media/windows/projects/aa-data-driven/bruno/basins/best_nse_barplot.png")

## PASSIRIO #################################
passirio_nse_cv = pd.read_csv("/media/windows/projects/aa-data-driven/bruno/basins/8/res/bests/cv_NSE_tst.csv", index_col=0)
# passirio_nse_cv[passirio_nse_cv<0] = np.NaN

output_path = "/media/windows/projects/aa-data-driven/bruno/basins/8/res/bests/"

passirio_nse_temperature = passirio_nse_cv.iloc[:,1:6]
passirio_nse_precipitation = passirio_nse_cv.iloc[:,6:8]
passirio_nse_streamflow = passirio_nse_cv.iloc[:,8:]

df_metrics_temp = evaluate_metrics(passirio_nse_temperature, std_df=np.std(passirio_nse_cv.T))
df_metrics_prec = evaluate_metrics(passirio_nse_precipitation, std_df=np.std(passirio_nse_cv.T))
df_metrics_flow = evaluate_metrics(passirio_nse_streamflow, std_df=np.std(passirio_nse_cv.T))

createBoxPlot(df_metrics_temp.T, "Forecast Horizon (hours)", "Normalised NSE [Z]", f"{output_path}passirio_temperature.png", output_format="png", my_dpi=300, width=65, label='(a)')
createBoxPlot(df_metrics_prec.T, "Forecast Horizon (hours)", None, f"{output_path}passirio_precipitation.png", output_format="png", my_dpi=300, label='(b)')
createBoxPlot(df_metrics_flow.T, "Forecast Horizon (hours)", None, f"{output_path}passirio_streamflow.png", output_format="png", my_dpi=300, label='(c)')


## ISARCO #################################
isarco_nse_cv = pd.read_csv("/media/windows/projects/aa-data-driven/bruno/basins/21/res/bests/cv_NSE_tst.csv", index_col=0)
# isarco_nse_cv[isarco_nse_cv<0] = np.NaN

output_path = "/media/windows/projects/aa-data-driven/bruno/basins/21/res/bests/"

isarco_nse_temperature = isarco_nse_cv.iloc[:,1:29]
isarco_nse_precipitation = isarco_nse_cv.iloc[:,29:47]
isarco_nse_streamflow = isarco_nse_cv.iloc[:,47:]

df_metrics_temp = evaluate_metrics(isarco_nse_temperature, std_df=np.std(isarco_nse_cv.T))
df_metrics_prec = evaluate_metrics(isarco_nse_precipitation, std_df=np.std(isarco_nse_cv.T))
df_metrics_flow = evaluate_metrics(isarco_nse_streamflow, std_df=np.std(isarco_nse_cv.T))

createBoxPlot(df_metrics_temp.T, "Forecast Horizon (hours)", "Normalised NSE [Z]", f"{output_path}isarco_temperature.png", output_format="png", my_dpi=300, width=65, label='(a)')
createBoxPlot(df_metrics_prec.T, "Forecast Horizon (hours)", None, f"{output_path}isarco_precipitation.png", output_format="png", my_dpi=300, label='(b)')
createBoxPlot(df_metrics_flow.T, "Forecast Horizon (hours)", None, f"{output_path}isarco_streamflow.png", output_format="png", my_dpi=300, label='(c)')


## ADIGE #################################
adige_nse_cv = pd.read_csv("/media/windows/projects/aa-data-driven/bruno/basins/25/res/bests/cv_NSE_tst.csv", index_col=0)
# adige_nse_cv[adige_nse_cv<0] = np.NaN

output_path = "/media/windows/projects/aa-data-driven/bruno/basins/25/res/bests/"

adige_nse_temperature = adige_nse_cv.iloc[:,1:65]
adige_nse_precipitation = adige_nse_cv.iloc[:,65:106]
adige_nse_streamflow = adige_nse_cv.iloc[:,106:]

df_metrics_temp = evaluate_metrics(adige_nse_temperature, std_df=np.std(adige_nse_cv.T))
df_metrics_prec = evaluate_metrics(adige_nse_precipitation, std_df=np.std(adige_nse_cv.T))
df_metrics_flow = evaluate_metrics(adige_nse_streamflow, std_df=np.std(adige_nse_cv.T))

createBoxPlot(df_metrics_temp.T, "Forecast Horizon (hours)", "Normalised NSE [Z]", f"{output_path}adige_temperature.png", output_format="png", my_dpi=300, width=65, label='(a)')
createBoxPlot(df_metrics_prec.T, "Forecast Horizon (hours)", None, f"{output_path}adige_precipitation.png", output_format="png", my_dpi=300, label='(b)')
createBoxPlot(df_metrics_flow.T, "Forecast Horizon (hours)", None, f"{output_path}adige_streamflow.png", output_format="png", my_dpi=300, label='(c)')