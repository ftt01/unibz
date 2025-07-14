import sys

locallib_dir = "/home/daniele/documents/github/ftt01/phd/ITstuff/pytorch/src/lib"
sys.path.insert( 0, locallib_dir )

from locallib import *

def get_postgres_connection():

    db_name = 'meteo'
    db_user = 'postgres'
    db_password = 'password'
    db_host = '172.20.0.4'

    return psycopg2.connect(database=db_name, user=db_user, password=db_password, host=db_host)

def sql_to_dataframe(conn, query, column_names):

    # print(query)
    cursor = conn.cursor()
    try:
        cursor.execute(query)
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return 1
    # The execute returns a list of tuples:
    tuples_list = cursor.fetchall()
    cursor.close()
    # Now we need to transform the list into a pandas DataFrame:
    df = DataFrame(tuples_list, columns=column_names)
    return df

def extract_pab(start_date, end_date, variable, station_id=None, lat=None, lon=None, n=1):

    if variable == "streamflow":
        var = "Q"

    aggregation_at = '1H'
    dates = date_range(start_date, end_date, freq=aggregation_at)

    full_df = DataFrame(index=dates)
    full_df.index.name = 'datetime'

    if station_id is None:
        sql_select_points = f'''
        WITH current_sensors AS (
            SELECT type, variable, units, station, id
            FROM bz.sensors
            WHERE type = '{var}'
        ),
        current_station AS (
            SELECT bz.stations.id AS id_station, current_sensors.id AS id_sensor, scode, geom
            FROM bz.stations, current_sensors
            WHERE bz.stations.id = current_sensors.station
        )
        SELECT current_station.id_station, current_station.id_sensor
        FROM current_station
        ORDER BY ST_Distance(ST_MakePoint({lon}, {lat})::geography, geom::geography)
        LIMIT {n}
        '''
    else:
        sql_select_points = f'''
        WITH current_sensors AS (
            SELECT type, variable, units, station, id
            FROM bz.sensors
            WHERE type = '{var}'
        )
        SELECT bz.stations.id AS id_station, current_sensors.id AS id_sensor
        FROM bz.stations, current_sensors
        WHERE bz.stations.scode = '{station_id}' AND bz.stations.id = current_sensors.station
        '''

    select_data = '''
    SELECT datetime, value
    FROM bz.hourly
    WHERE datetime >= '{start_datetime}' 
        AND datetime <= '{end_datetime}' 
        AND id_sensor = {id_sensor}
    GROUP BY datetime, value
    '''

    # select_data = '''
    # SELECT datetime, (value + COALESCE(LAG(value) OVER (ORDER BY datetime), 0) + COALESCE(LEAD(value) OVER (ORDER BY datetime), 0)) / 3 AS value
    # FROM bz.hourly
    # WHERE datetime >= '{start_datetime}' 
    #     AND datetime <= '{end_datetime}' 
    #     AND id_sensor = {id_sensor}
    # GROUP BY datetime, value
    # '''

    db_points = sql_to_dataframe( get_postgres_connection(), sql_select_points, column_names = ['id_station','id_sensor'])

    for point in db_points["id_sensor"].to_list():
      
        sql_get_data = select_data.format(
                start_datetime = (start_date-dt.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
                end_datetime = end_date.strftime('%Y-%m-%d %H:%M'),
                id_sensor = point
            )

        # print(sql_get_data)
        
        c_df = sql_to_dataframe( get_postgres_connection(), sql_get_data, column_names = ['datetime', 'value'])

        c_df.set_index('datetime', inplace=True)
        ### put the old_id or the point in the columns of full_df
        c_df.rename(columns={'value':point}, inplace=True)

        c_df = c_df.astype(float)
        
        # ## precipitation
        # if variable == 'tp':
        #     # c_df = resample_timeseries( 
        #     #     c_df, res_type='sum', 
        #     #     step=aggregation_at, offset=True )
        #     # from meters to mm
        #     c_df = c_df * 1000
        #     c_df = c_df[start_date:end_date]
        # ## temperature
        # elif variable == '2t':
        #     # c_df = resample_timeseries( 
        #     #     c_df, res_type='mean', 
        #     #     step=aggregation_at, offset=True )
        #     # from Kelvin to Celsius
        #     c_df = c_df - 273.15

        full_df = concat([full_df,c_df], axis=1)

    full_df = full_df.round(decimals=3)

    return full_df


def extract_cum_pab(start_date, end_date, variable, cum_lag=None, station_id=None, lat=None, lon=None, n=1):

    if variable == "streamflow":
        var = "Q"

    aggregation_at = '1H'
    dates = date_range(start_date, end_date, freq=aggregation_at)

    full_df = DataFrame(index=dates)
    full_df.index.name = 'datetime'

    if station_id is None:
        sql_select_points = f'''
        WITH current_sensors AS (
            SELECT type, variable, units, station, id
            FROM bz.sensors
            WHERE type = '{var}'
        ),
        current_station AS (
            SELECT bz.stations.id AS id_station, current_sensors.id AS id_sensor, scode, geom
            FROM bz.stations, current_sensors
            WHERE bz.stations.id = current_sensors.station
        )
        SELECT current_station.id_station, current_station.id_sensor
        FROM current_station
        ORDER BY ST_Distance(ST_MakePoint({lon}, {lat})::geography, geom::geography)
        LIMIT {n}
        '''
    else:
        sql_select_points = f'''
        WITH current_sensors AS (
            SELECT type, variable, units, station, id
            FROM bz.sensors
            WHERE type = '{var}'
        )
        SELECT bz.stations.id AS id_station, current_sensors.id AS id_sensor
        FROM bz.stations, current_sensors
        WHERE bz.stations.scode = '{station_id}' AND bz.stations.id = current_sensors.station
        '''

    select_data = '''
    SELECT datetime,
        AVG(value) OVER (
            ORDER BY datetime 
            ROWS BETWEEN {lag} PRECEDING AND CURRENT ROW
        ) AS value
    FROM bz.hourly
    WHERE datetime >= '{start_datetime}' 
        AND datetime <= '{end_datetime}' 
        AND id_sensor = {id_sensor}
    GROUP BY datetime, value
    '''

    db_points = sql_to_dataframe( get_postgres_connection(), sql_select_points, column_names = ['id_station','id_sensor'])

    for point in db_points["id_sensor"].to_list():
      
        sql_get_data = select_data.format(
            lag = cum_lag,
            start_datetime = (start_date-dt.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
            end_datetime = end_date.strftime('%Y-%m-%d %H:%M'),
            id_sensor = point
        )

        # print(sql_get_data)
        
        c_df = sql_to_dataframe( get_postgres_connection(), sql_get_data, column_names = ['datetime', 'value'])

        c_df.set_index('datetime', inplace=True)
        ### put the old_id or the point in the columns of full_df
        c_df.rename(columns={'value':point}, inplace=True)

        c_df = c_df.astype(float)
        
        # ## precipitation
        # if variable == 'tp':
        #     # c_df = resample_timeseries( 
        #     #     c_df, res_type='sum', 
        #     #     step=aggregation_at, offset=True )
        #     # from meters to mm
        #     c_df = c_df * 1000
        #     c_df = c_df[start_date:end_date]
        # ## temperature
        # elif variable == '2t':
        #     # c_df = resample_timeseries( 
        #     #     c_df, res_type='mean', 
        #     #     step=aggregation_at, offset=True )
        #     # from Kelvin to Celsius
        #     c_df = c_df - 273.15

        full_df = concat([full_df,c_df], axis=1)

    full_df = full_df.round(decimals=3)

    return full_df


def extract_era5land(start_date, end_date, variable, poly=None, lat=None, lon=None, n=1):

    aggregation_at = '1H'
    dates = date_range(start_date, end_date, freq=aggregation_at)

    full_df = DataFrame(index=dates)
    full_df.index.name = 'datetime'

    if poly is None:
        select_points = f'''
        SELECT id
        FROM ecmwf.era5land_points
        ORDER BY ST_Distance(ST_MakePoint({lon}, {lat})::geography, geom::geography)
        LIMIT {n}
        '''
    else:
        select_points = f'''
        SELECT id
        FROM ecmwf.era5land_points
        WHERE ST_Contains(ST_PolygonFromText('{poly}', 4326), geom)
        ORDER BY ST_Distance(ST_PolygonFromText('{poly}', 4326)::geography, geom::geography)
        LIMIT {n}
        '''

    select_data_tp = '''
    SELECT datetime,
        CASE
            WHEN EXTRACT(hour FROM datetime) = 1 THEN value
            ELSE (value - LAG(value) OVER (ORDER BY datetime))
        END AS value
    FROM ecmwf.era5land_values
    WHERE datetime >= '{start_datetime}' 
        AND datetime <= '{end_datetime}' 
        AND variable = '{variable}'
        AND point = {point}
    GROUP BY datetime, value
    ORDER BY datetime'''

    select_data_2t = '''
    SELECT datetime, value
    FROM ecmwf.era5land_values
    WHERE datetime >= '{start_datetime}' 
        AND datetime <= '{end_datetime}' 
        AND variable = '{variable}'
        AND point = {point}
    GROUP BY datetime, value
    ORDER BY datetime'''

    # print(select_points)

    db_points = sql_to_dataframe( get_postgres_connection(), select_points, column_names = ['id'])

    for point in db_points["id"].to_list():

        if variable == 'tp':
            sql_get_data = select_data_tp.format(
                    start_datetime = (start_date-dt.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
                    end_datetime = end_date.strftime('%Y-%m-%d %H:%M'),
                    variable = variable,
                    point = point
                )

        elif variable == '2t':
            sql_get_data = select_data_2t.format(
                    start_datetime = (start_date-dt.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
                    end_datetime = end_date.strftime('%Y-%m-%d %H:%M'),
                    variable = variable,
                    point = point
                )

        # print(sql_get_data)
        c_df = sql_to_dataframe( get_postgres_connection(), sql_get_data, column_names = ['datetime', 'value'])

        c_df.set_index('datetime', inplace=True)
        ### put the old_id or the point in the columns of full_df
        c_df.rename(columns={'value':point}, inplace=True)

        c_df = c_df.astype(float)
        
        ## precipitation
        if variable == 'tp':
            # c_df = resample_timeseries( 
            #     c_df, res_type='sum', 
            #     step=aggregation_at, offset=True )
            # from meters to mm
            c_df = c_df * 1000
            c_df = c_df[start_date:end_date]
        ## temperature
        elif variable == '2t':
            # c_df = resample_timeseries( 
            #     c_df, res_type='mean', 
            #     step=aggregation_at, offset=True )
            # from Kelvin to Celsius
            c_df = c_df - 273.15

        full_df = concat([full_df,c_df], axis=1, join='inner')

    full_df = full_df.round(decimals=3)

    return full_df

###############

def extract_cum_era5land(start_date, end_date, variable, cum_lag, poly=None, lat=None, lon=None, n=1):

    aggregation_at = '1H'
    dates = date_range(start_date, end_date, freq=aggregation_at)

    full_df = DataFrame(index=dates)
    full_df.index.name = 'datetime'

    if poly is None:
        select_points = f'''
        SELECT id
        FROM ecmwf.era5land_points
        ORDER BY ST_Distance(ST_MakePoint({lon}, {lat})::geography, geom::geography)
        LIMIT {n}
        '''
    else:
        select_points = f'''
        SELECT id
        FROM ecmwf.era5land_points
        WHERE ST_Contains(ST_PolygonFromText('{poly}', 4326), geom)
        ORDER BY ST_Distance(ST_PolygonFromText('{poly}', 4326)::geography, geom::geography)
        LIMIT {n}
        '''

    select_data_tp = '''
    SELECT datetime,
        SUM(value) OVER (
            ORDER BY datetime 
            ROWS BETWEEN {lag} PRECEDING AND CURRENT ROW
        ) AS value
    FROM ecmwf.era5land_values
    WHERE datetime >= '{start_datetime}' 
        AND datetime <= '{end_datetime}' 
        AND variable = '{variable}'
        AND point = {point}
    GROUP BY datetime, value
    ORDER BY datetime'''

    select_data_2t = '''
    SELECT datetime,
        AVG(value) OVER (
            ORDER BY datetime 
            ROWS BETWEEN {lag} PRECEDING AND CURRENT ROW
        ) AS value
    FROM ecmwf.era5land_values
    WHERE datetime >= '{start_datetime}' 
        AND datetime <= '{end_datetime}' 
        AND variable = '{variable}'
        AND point = {point}
    GROUP BY datetime, value
    ORDER BY datetime'''

    # print(select_points)

    db_points = sql_to_dataframe( get_postgres_connection(), select_points, column_names = ['id'])

    for point in db_points["id"].to_list():

        if variable == 'tp':
            sql_get_data = select_data_tp.format(
                lag=cum_lag,
                start_datetime = (start_date-dt.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
                end_datetime = end_date.strftime('%Y-%m-%d %H:%M'),
                variable = variable,
                point = point
            )

        elif variable == '2t':
            sql_get_data = select_data_2t.format(
                lag=cum_lag,
                start_datetime = (start_date-dt.timedelta(hours=1)).strftime('%Y-%m-%d %H:%M'),
                end_datetime = end_date.strftime('%Y-%m-%d %H:%M'),
                variable = variable,
                point = point
            )

        # print(sql_get_data)
        c_df = sql_to_dataframe( get_postgres_connection(), sql_get_data, column_names = ['datetime', 'value'])

        c_df.set_index('datetime', inplace=True)
        ### put the old_id or the point in the columns of full_df
        c_df.rename(columns={'value':point}, inplace=True)

        c_df = c_df.astype(float)
        
        ## precipitation
        if variable == 'tp':
            # c_df = resample_timeseries( 
            #     c_df, res_type='sum', 
            #     step=aggregation_at, offset=True )
            # from meters to mm
            c_df = c_df * 1000
            c_df = c_df[start_date:end_date]
        ## temperature
        elif variable == '2t':
            # c_df = resample_timeseries( 
            #     c_df, res_type='mean', 
            #     step=aggregation_at, offset=True )
            # from Kelvin to Celsius
            c_df = c_df - 273.15

        full_df = concat([full_df,c_df], axis=1, join='inner')

    full_df = full_df.round(decimals=3)

    return full_df