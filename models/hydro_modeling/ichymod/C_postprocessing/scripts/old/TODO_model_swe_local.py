from lib import *

### simulation selection #############################################################################

current_phase = "best_merano_cal_val"
current_basin = "passirio"
current_node = "merano"

current_type = "kriging"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, \
        sca_passirio, swe1_kr, swe2_kr, swe3_kr, swe4_kr, swe5_kr \
            = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

current_type = "kriging_11"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, \
        sca_passirio, swe1_kr11, swe2_kr11, swe3_kr11, swe4_kr11, swe5_kr11 \
            = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################
### simulation selection #############################################################################

current_type = "reanalysis"

model_flow, model_precipitation, model_temperature, \
    obs_flow, obs_temperature, model_snow_we, model_snow_we_plan, \
        sca_passirio, swe1_rea, swe2_rea, swe3_rea, swe4_rea, swe5_rea \
            = retrieveSimulated( configPath, current_phase, current_basin, current_type, current_node)

### end simulation selection ##########################################################################

# Plan
swe1_kr = swe1_kr.resample('d').mean()
swe1_kr = pd.DataFrame(data=swe1_kr)

swe1_kr_model = pd.DataFrame(index=swe1_kr.index, columns=['swe_kr'])
swe1_kr_model['swe_kr'] = swe1_kr.values

# Prati di Plan
swe2_kr = swe2_kr.resample('d').mean()
swe2_kr = pd.DataFrame(data=swe2_kr)

swe2_kr_model = pd.DataFrame(index=swe2_kr.index, columns=['swe_kr'])
swe2_kr_model['swe_kr'] = swe2_kr.values

# Plata
swe3_kr = swe3_kr.resample('d').mean()
swe3_kr = pd.DataFrame(data=swe3_kr)

swe3_kr_model = pd.DataFrame(index=swe3_kr.index, columns=['swe_kr'])
swe3_kr_model['swe_kr'] = swe3_kr.values

# St. Martino
swe4_kr = swe4_kr.resample('d').mean()
swe4_kr = pd.DataFrame(data=swe4_kr)

swe4_kr_model = pd.DataFrame(index=swe4_kr.index, columns=['swe_kr'])
swe4_kr_model['swe_kr'] = swe4_kr.values

# Alpe del Tumulo
swe5_kr = swe5_kr.resample('d').mean()
swe5_kr = pd.DataFrame(data=swe5_kr)

swe5_kr_model = pd.DataFrame(index=swe5_kr.index, columns=['swe_kr'])
swe5_kr_model['swe_kr'] = swe5_kr.values

# Plan
swe1_kr11 = swe1_kr11.resample('d').mean()
swe1_kr11 = pd.DataFrame(data=swe1_kr11)

swe1_kr11_model = pd.DataFrame(index=swe1_kr11.index, columns=['swe_kr11'])
swe1_kr11_model['swe_kr11'] = swe1_kr11.values

# Prati di Plan
swe2_kr11 = swe2_kr11.resample('d').mean()
swe2_kr11 = pd.DataFrame(data=swe2_kr11)

swe2_kr11_model = pd.DataFrame(index=swe2_kr11.index, columns=['swe_kr11'])
swe2_kr11_model['swe_kr11'] = swe2_kr11.values

# Plata
swe3_kr11 = swe3_kr11.resample('d').mean()
swe3_kr11 = pd.DataFrame(data=swe3_kr11)

swe3_kr11_model = pd.DataFrame(index=swe3_kr11.index, columns=['swe_kr11'])
swe3_kr11_model['swe_kr11'] = swe3_kr11.values

# St. Martino
swe4_kr11 = swe4_kr11.resample('d').mean()
swe4_kr11 = pd.DataFrame(data=swe4_kr11)

swe4_kr11_model = pd.DataFrame(index=swe4_kr11.index, columns=['swe_kr11'])
swe4_kr11_model['swe_kr11'] = swe4_kr11.values

# Alpe del Tumulo
swe5_kr11 = swe5_kr11.resample('d').mean()
swe5_kr11 = pd.DataFrame(data=swe5_kr11)

swe5_kr11_model = pd.DataFrame(index=swe5_kr11.index, columns=['swe_kr11'])
swe5_kr11_model['swe_kr11'] = swe5_kr11.values

# Plan
swe1_rea = swe1_rea.resample('d').mean()
swe1_rea = pd.DataFrame(data=swe1_rea)

swe1_rea_model = pd.DataFrame(index=swe1_rea.index, columns=['swe_rea'])
swe1_rea_model['swe_rea'] = swe1_rea.values

# Prati di Plan
swe2_rea = swe2_rea.resample('d').mean()
swe2_rea = pd.DataFrame(data=swe2_rea)

swe2_rea_model = pd.DataFrame(index=swe2_rea.index, columns=['swe_rea'])
swe2_rea_model['swe_rea'] = swe2_rea.values

# Plata
swe3_rea = swe3_rea.resample('d').mean()
swe3_rea = pd.DataFrame(data=swe3_rea)

swe3_rea_model = pd.DataFrame(index=swe3_rea.index, columns=['swe_rea'])
swe3_rea_model['swe_rea'] = swe3_rea.values

# St. Martino
swe4_rea = swe4_rea.resample('d').mean()
swe4_rea = pd.DataFrame(data=swe4_rea)

swe4_rea_model = pd.DataFrame(index=swe4_rea.index, columns=['swe_rea'])
swe4_rea_model['swe_rea'] = swe4_rea.values

# Alpe del Tumulo
swe5_rea = swe5_rea.resample('d').mean()
swe5_rea = pd.DataFrame(data=swe5_rea)

swe5_rea_model = pd.DataFrame(index=swe5_rea.index, columns=['swe_rea'])
swe5_rea_model['swe_rea'] = swe5_rea.values

def read_local_csv(fileName):
    from pandas import read_csv
    df = read_csv(fileName, skiprows=1, index_col=0, parse_dates=True, names=['depth_obs'], dayfirst=True)

    df['depth_obs'] = pd.to_numeric(df['depth_obs'])
    df[df['depth_obs']<0] = None
    return df.resample('d').mean()

def get_doy( datetime, model='S10' ):

    if model == 'S10':
        curr_year = str(datetime.year)
        ref_date = pd.Timestamp(curr_year + '-10-01')

        if datetime.dayofyear >= ref_date.dayofyear:
            return - 92 + datetime.dayofyear - ref_date.dayofyear
        else:
            return datetime.dayofyear
    else:
        return None

def depth_2_rho_snow( df, model='S10'):

    df_out = pd.DataFrame(index=df.index, columns=['rho_snow'])
    for index, row in df.iterrows():
        
        depth = row['depth_obs']

        model_doy = get_doy( index, model=model )
        rho_snow = density_eval(depth, doy=model_doy, model=model)

        df_out.at[index, 'rho_snow'] = round(rho_snow,2)
        
    return pd.concat([df, df_out], axis=1)

# def swe_from_depth(depth, rho_snow, rho_w=997, unit='cm'):
#     if unit == 'm':
#         unit_conv = 1000
#     if unit == 'cm':
#         unit_conv = 10
#     if unit == 'mm':
#         unit_conv = 1
#     out = rho_snow / rho_w * depth * unit_conv
#     return out

# def evaluate_swe( df ):

#     df_out = pd.DataFrame(index=df.index, columns=['swe'])
#     for index, row in df.iterrows():
#         depth = row['depth_obs']
#         rho_snow = row['rho_snow']
        
#         swe = swe_from_depth(depth, rho_snow)

#         # to avoid negative SWE
#         if swe >= 0:
#             df_out.at[index, 'swe'] = round(swe,2)
#         else:
#             df_out.at[index, 'swe'] = None

#     return pd.concat([df, df_out], axis=1)

def depth_from_swe(swe, rho_snow, rho_w=997, unit='cm'):
    if unit == 'm':
        unit_conv = 1000
    if unit == 'cm':
        unit_conv = 10
    if unit == 'mm':
        unit_conv = 1

    # print("swe: " + str(swe))
    # print("rho_snow: " + str(rho_snow))
    # print("rho_w: " + str(rho_w))
    # print("unit_conv: " + str(unit_conv))

    out = swe * rho_w / rho_snow / unit_conv
    return out

def evaluate_depth( df, dataset ):

    out_feature_name = 'depth_' + dataset
    in_swe_name = 'swe_' + dataset

    df_out = pd.DataFrame(index=df.index, columns=[out_feature_name])
    for index, row in df.iterrows():
        swe = row[in_swe_name]
        rho_snow = row['rho_snow']
        depth = depth_from_swe(swe, rho_snow)

        # to avoid negative depth
        if depth >= 0:
            df_out.at[index, out_feature_name] = round(swe,2)
        else:
            df_out.at[index, out_feature_name] = None

    return pd.concat([df, df_out], axis=1)


def printing(df, current_phase):

    datasets = ["kr", "kr11", "rea"]

    df_name = [x for x in globals() if globals()[x] is df][0]

    outfile = config["output_path"] + "model\\passirio\\swe\\daily\\" \
        + "model_passirio_model_depth_" + df_name + '.' + output_format

    plots = []

    plots.append( (df['depth_obs'], {"label":"Observed"}) )
    
    for el in datasets:
        feature_name = 'depth_' + el
        if el == 'kr':
            label = "Kriging 1x1"
        if el == 'kr11':
            label = "Kriging 11x8"
        if el == 'rea':
            label = "Reanalysis 11x8"
        plots.append( (df[feature_name], {"label": label}) )
        # print(feature_name)

    createPlot( plots, "Time $[day]$", 'Depth $[cm]$', outfile, output_format=output_format, my_dpi=600 )

    ####################

    # outfile = config["output_path"] + "model\\passirio\\swe\\daily\\" \
    # + "model_passirio_depth_" + df_name + '_' + current_phase + '.' + output_format

    # plots = []
    # plt_conf = {}

    # plots.append( (df['depth_obs'], plt_conf) )

    # createPlot( plots, "Time $[day]$", 'Depth $[mm]$', outfile, output_format=output_format, my_dpi=600 )

    ####################

    outfile = config["output_path"] + "model\\passirio\\swe\\daily\\" \
    + "model_passirio_rho_snow_" + df_name + '.' + output_format

    plots = []
    plt_conf = {}

    plots.append( (df['rho_snow'], plt_conf) )

    createPlot( plots, "Time $[day]$", 'Density $[kg/m^3]$', outfile, output_format=output_format, my_dpi=600 )

fileName_belpiano = "D:\\hydrology\\data\\da_Nicola\\dati neve da Uff. Idro. BZ\\mod\\00390SF Belpiano HS TagMittel.csv"
df_belpiano = read_local_csv(fileName_belpiano)

fileName_alpedeltumulo = "D:\\hydrology\\data\\da_Nicola\\dati neve da Uff. Idro. BZ\\mod\\20050SF Alpe del Tumulo HS TagMittel.csv"
df_alpedeltumulo = read_local_csv(fileName_alpedeltumulo)

fileName_plan = "D:\\hydrology\\data\\da_Nicola\\dati neve da Uff. Idro. BZ\\mod\\20580BL Plan Mod 1 HS TagMomentan.csv"
df_plan = read_local_csv(fileName_plan)

fileName_pratiplan = "D:\\hydrology\\data\\da_Nicola\\dati neve da Uff. Idro. BZ\\mod\\20690SF Prati di Plan HS TagMittel.csv"
df_pratiplan = read_local_csv(fileName_pratiplan)

fileName_plata = "D:\\hydrology\\data\\da_Nicola\\dati neve da Uff. Idro. BZ\\mod\\20900MS Plata HS Beobachter TagMomentan.csv"
df_plata = read_local_csv(fileName_plata)

fileName_stmartino = "D:\\hydrology\\data\\da_Nicola\\dati neve da Uff. Idro. BZ\\mod\\22200BM SMartino in Passiria.csv"
df_stmartino = read_local_csv(fileName_stmartino)

fileName_merano = "D:\\hydrology\\data\\da_Nicola\\dati neve da Uff. Idro. BZ\\mod\\23200MS Merano.csv"
df_merano = read_local_csv(fileName_merano)

df_alpedeltumulo = depth_2_rho_snow( df_alpedeltumulo )
df_belpiano = depth_2_rho_snow( df_belpiano )
df_merano = depth_2_rho_snow( df_merano )
df_plan = depth_2_rho_snow( df_plan )
df_plata = depth_2_rho_snow( df_plata )
df_pratiplan = depth_2_rho_snow( df_pratiplan )
df_stmartino = depth_2_rho_snow( df_stmartino )

current_type = "kr"

# Plan # SG1
df_plan = pd.concat([swe1_kr_model, df_plan], axis=1)
df_plan = evaluate_depth( df_plan, current_type )

# Prati di Plan # SG2
df_pratiplan = pd.concat([swe2_kr_model, df_pratiplan], axis=1)
df_pratiplan = evaluate_depth( df_pratiplan, current_type )

# Plata # SG3
df_plata = pd.concat([swe3_kr_model, df_plata], axis=1)
df_plata = evaluate_depth( df_plata, current_type )

# St. Martino # SG4
df_stmartino = pd.concat([swe4_kr_model, df_stmartino], axis=1)
df_stmartino = evaluate_depth( df_stmartino, current_type )

# Alpe del Tumulo # SG5
df_alpedeltumulo = pd.concat([swe5_kr_model, df_alpedeltumulo], axis=1)
df_alpedeltumulo = evaluate_depth( df_alpedeltumulo, current_type )

current_type = "kr11"

# Plan # SG1
df_plan = pd.concat([swe1_kr11_model, df_plan], axis=1)
df_plan = evaluate_depth( df_plan, current_type )

# Prati di Plan # SG2
df_pratiplan = pd.concat([swe2_kr11_model, df_pratiplan], axis=1)
df_pratiplan = evaluate_depth( df_pratiplan, current_type )

# Plata # SG3
df_plata = pd.concat([swe3_kr11_model, df_plata], axis=1)
df_plata = evaluate_depth( df_plata, current_type )

# St. Martino # SG4
df_stmartino = pd.concat([swe4_kr11_model, df_stmartino], axis=1)
df_stmartino = evaluate_depth( df_stmartino, current_type )

# Alpe del Tumulo # SG5
df_alpedeltumulo = pd.concat([swe5_kr11_model, df_alpedeltumulo], axis=1)
df_alpedeltumulo = evaluate_depth( df_alpedeltumulo, current_type )

current_type = "rea"

# Plan # SG1
df_plan = pd.concat([swe1_rea_model, df_plan], axis=1)
df_plan = evaluate_depth( df_plan, current_type )

# Prati di Plan # SG2
df_pratiplan = pd.concat([swe2_rea_model, df_pratiplan], axis=1)
df_pratiplan = evaluate_depth( df_pratiplan, current_type )

# Plata # SG3
df_plata = pd.concat([swe3_rea_model, df_plata], axis=1)
df_plata = evaluate_depth( df_plata, current_type )

# St. Martino # SG4
df_stmartino = pd.concat([swe4_rea_model, df_stmartino], axis=1)
df_stmartino = evaluate_depth( df_stmartino, current_type )

# Alpe del Tumulo # SG5
df_alpedeltumulo = pd.concat([swe5_rea_model, df_alpedeltumulo], axis=1)
df_alpedeltumulo = evaluate_depth( df_alpedeltumulo, current_type )

df_plan = df_plan.loc['2013-10-10':'2018-12-31']
printing(df_plan, current_phase)

df_pratiplan = df_pratiplan.loc['2014-10-10':'2018-12-31']
printing(df_pratiplan, current_phase)

df_plata = df_plata.loc['2014-10-10':'2018-12-31']
printing(df_plata, current_phase)

df_stmartino = df_stmartino.loc['2014-10-10':'2018-12-31']
printing(df_stmartino, current_phase)

df_alpedeltumulo = df_alpedeltumulo.loc['2014-10-10':'2018-12-31']
printing(df_alpedeltumulo, current_phase)