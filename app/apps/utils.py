import os
import pandas as pd
import numpy as np
from datetime import datetime
import geopandas as gpd

weather_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/weather'))


def read_weather_data():

    dfs = []
    paths = [p for p in os.listdir(weather_data_folder) if p.endswith('.txt')]
    for path in paths:
        station = pd.read_csv(os.path.join(weather_data_folder, path), sep='\t', parse_dates=[[0, 1]], header=[0, 1],
                              dayfirst=True, na_values='---')
        station = station.drop_duplicates(station.columns[0]).set_index(station.columns[0]).sort_index()
        station.index.name = 'time'
        station.columns = [' '.join([c.strip() for c in col if 'Unnamed' not in c]).lower() for col in station.columns]
        station.columns = [col.replace(' ', '_').replace('.', '') for col in station.columns]
        station['station_name'] = path[:-4]

        dfs.append(station)

    df = pd.concat(dfs)

    new_index = np.array(df.index)
    new_index[(df.station_name == 'ACTogether-HQ') &
              (df.index < datetime(day=31, month=7, year=2019))] += np.timedelta64(87, 'D')

    df = df.set_index(new_index)

    return df


def read_station_locations():
    return gpd.read_file(os.path.join(weather_data_folder, 'station_locations.geojson')).sort_values('id')