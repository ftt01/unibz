#!/usr/bin/env python
# coding: utf-8

import sys

lib_dir = "/home/daniele/documents/github/ftt01/phd/share/lib"
sys.path.insert( 0, lib_dir )

from lib import *
import subprocess
import psycopg2

from multiprocessing import Pool
from multiprocessing import cpu_count

# input_parser = argparse.ArgumentParser()
# input_parser.add_argument('start_date', type=str)
# input_parser.add_argument('end_date', type=str)
# input_parser.add_argument('file', type=str)
# input_parser.add_argument('variable', type=str)
# args = input_parser.parse_args()

start_date_str = "2017-12-28T00:00:00"
end_date_str = "2019-12-31T23:00:00"
# start_date_str = args.start_date + "T00:00:00"
# end_date_str = args.end_date + "T23:00:00"
start_date = dt.datetime.strptime( start_date_str, '%Y-%m-%dT%H:%M:%S' )
end_date = dt.datetime.strptime( end_date_str, '%Y-%m-%dT%H:%M:%S' )
dates = pd.date_range(start_date, end_date, freq='d')

# variables = [
#     ('tp', "/media/windows/projects/bias_correction/applications/era5/data/unbiased/p_best_ls.csv"),
#     ('2t', "/media/windows/projects/bias_correction/applications/era5/data/unbiased/t_best_eqm.csv")
#     ]

variables = [
    ('tp', "/media/windows/projects/bias_correction/applications/era5/data/unbiased/p_best_ls_testing.csv"),
    ('2t', "/media/windows/projects/bias_correction/applications/era5/data/unbiased/t_best_eqm_testing.csv")
    ]

grid_path = "/media/windows/projects/bias_correction/applications/era5/data/unbiased/grid.csv"
             
def get_postgres_connection():

    db_name = 'meteo'
    db_user = 'postgres'
    db_password = 'postgres'
    db_host = '172.20.0.2'

    return psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host)

def add_point( y, x, epsg=4326, tolerance=0.01 ):

    c_id = None

    sql_exist = '''
        SELECT COUNT(*)
        FROM ecmwf.era5land_points
        WHERE ST_Contains(
            ST_Transform(
                ST_MakeEnvelope({min_lon}, {min_lat}, {max_lon}, {max_lat}, {epsg}), 4326 ),
            era5land_points.geom)
        LIMIT 1;'''

    min_lat = y - tolerance
    max_lat = y + tolerance
    min_lon = x - tolerance
    max_lon = x + tolerance

    sql_exist = sql_exist.format(
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon,
        epsg=epsg
    )
    
    print(sql_exist)

    sql_insert = '''
        INSERT INTO ecmwf.era5land_points(geom)
        VALUES ( ST_SetSRID(ST_MakePoint({x},{y}),{epsg}) )
        ON CONFLICT DO NOTHING;'''.format(
            x=x,
            y=y,
            epsg=epsg
    )

    sql_select = '''
        SELECT ecmwf.era5land_points.id
        FROM ecmwf.era5land_points
        ORDER BY ecmwf.era5land_points.geom <#> ST_SetSRID(ST_MakePoint({x},{y}),{epsg})
        LIMIT 1;'''.format(
            x=x,
            y=y,
            epsg=epsg
        )
    
    # print(sql_select)

    conn = get_postgres_connection()
    try:
        with conn.cursor() as cur:
            # print(sql_insert)
            # cur.execute(sql_insert)
            # conn.commit()

            # cur.execute(sql_select)
            # c_id = int(cur.fetchall()[0][0])
            cur.execute(sql_exist)
            rows = cur.fetchall()
            if rows[0][0] != 0:
                cur.execute(sql_select)
                c_id = int(cur.fetchall()[0][0])
            else:
                print(sql_insert)
                cur.execute(sql_insert)
                conn.commit()
                cur.execute(sql_select)
                c_id = int(cur.fetchall()[0][0])
    finally:
        conn.close()

    return c_id

# def add_data( y, x, epsg, datetime_UTC, value, variable, um ):

#     # print(point)

#     sql_insert = '''
#         SELECT ecmwf.era5land_points.id
#         FROM ecmwf.era5land_points
#         ORDER BY ST_Distance(ST_SetSRID(ST_MakePoint({x},{y}),{epsg}), ecmwf.era5land_points.geom)
#         LIMIT 1;'''.format(
#             x=x,
#             y=y,
#             epsg=epsg
#         )
    
#     print(sql_insert)

#     conn = get_postgres_connection()
#     try:
#         with conn.cursor() as cur:
#             cur.execute(sql_insert)
#             conn.commit()
#     finally:
#         conn.close()

def add_data( y, x, epsg, datetime_UTC, value, variable, um ):

    # print(point)

    sql_insert = '''
        INSERT INTO biascorrection.era5land_unbiased(
	        datetime, value, point, variable, um)
	    VALUES ('{datetime}'::timestamp, {value},
            (   SELECT ecmwf.era5land_points.id
                FROM ecmwf.era5land_points
                ORDER BY ST_Distance(ST_SetSRID(ST_MakePoint({x},{y}),{epsg}), ecmwf.era5land_points.geom)
                LIMIT 1
            ), '{variable}', '{um}')
        ON CONFLICT DO NOTHING;'''.format(
            x=x,
            y=y,
            epsg=epsg,
            datetime=datetime_UTC, 
            value=value, 
            variable=variable,
            um=um
        )
    print(sql_insert)
    
    conn = get_postgres_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql_insert)
            conn.commit()
    finally:
        conn.close()

def save2DB(cell_id):

    c_id = cell_id[0]
    pos = cell_id[1]
    lines = cell_id[2]
    start_hour = cell_id[3]
    var_meta = cell_id[4]

    # print(f"ID: {c_id}")
            
    lat = grid_df[grid_df['ID'] == int(c_id)]['lat'].values[0]
    lon = grid_df[grid_df['ID'] == int(c_id)]['lon'].values[0]
    epsg = 4326

    # print(f"Latitude: {lat}")
    # print(f"Longitude: {lon}")

    cum = 0
    for line in lines[1:]:

        value = float(line.split(",")[pos]) / 1000

        datetime = dt.datetime.strptime(line.split(",")[0], "%Y-%m-%d %H:%M:%S") + dt.timedelta(hours=start_hour)
        datetime_str = dt.datetime.strftime(datetime, format="%Y-%m-%d %H:%M:%S")

        if var_meta[0]  == 'tp':

            if datetime.hour == 1:
                cum = 0
            cum = round(cum + value,6)
            add_data( lat, lon, epsg, datetime_str, cum, var_meta[0], var_meta[1] )

        elif var_meta[0] == '2t':
            value = value + 273.15

            add_data( lat, lon, epsg, datetime_str, value, var_meta[0], var_meta[1] )

def load_on_db( var_meta, c_file, start_hour=0 ):

    ## data from 00:00 to 01:00 is saved as data at 00:00 if start_hour = -1
    i = 0 + start_hour

    ## read file and for each line add the point if it does not exist, then add the data to era5land_unbiased
    with open(c_file, 'r') as f:
        lines = f.readlines()
        list_of_cells = lines[0].replace("\"","").split(",")[1:]

        to_save = []
        pos = 0
        for c in list_of_cells:
            pos = pos + 1
            to_save.append( [c,pos,lines,i,var_meta] )

        p = Pool(int(cpu_count()*2/3))
        p.map(save2DB, to_save)
                    
        f.close()

grid_df = pd.read_csv(grid_path)

for datas in variables:

    model_varname = datas[0]
    file = datas[1]
    print('Processing: ' + str(file))

    if model_varname == 'tp':
        variable = 'tp'
        um = 'm'
    elif model_varname == '2t':
        variable = '2t'
        um = 'K'

    load_on_db( (variable, um), file, start_hour=-1 )