### READ FROM DB TO INPUT BIAS
The bias is working on a matrix file as input both for the model rather than the reference dataset.
The first line is the header and is normally: datetime,1,2,3,4,5... that represent the index and the grid id of each cell.
On each subsequent line of the matrix there is the datetime [YYYY-mm-dd HH:MM:SS] and the data.
On each coloum is a point of the grid.

The IDs that are the columns of the matrix have the metadata in another file: grid.csv

So:
1. read the metadata file                                                                   DONE
2. for each id, read the point and retrieve from the db the nearest point ID                DONE
3. read the data from start_date to end_date and then save it in the dataframe              DONE
4. save the full dataframe in a CSV                                                         DONE

### shift to have data from 00 to 01 as data at 01:00 >>> too expensive
WITH dataset as (
	SELECT value FROM ecmwf.era5_data
-- 	WHERE datetime >= '2010-01-01 00:00' AND datetime <= '2019-12-31 23:59' AND variable = '2t'
	ORDER BY datetime ASC, point ASC, variable ASC
),
dtm as (
	SELECT datetime + interval '1 hour' as dt, point, variable, um FROM ecmwf.era5_data
-- 	WHERE datetime >= '2010-01-01 00:00' AND datetime <= '2010-01-01 23:59' AND variable = '2t'
	ORDER BY datetime ASC, point ASC, variable ASC
)
INSERT INTO ecmwf.era5_values(datetime, point, variable, um, value)
SELECT dtm.dt, dtm.point, dtm.variable, dtm.um, dataset.value
FROM dtm,dataset
ON CONFLICT DO NOTHING