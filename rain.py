import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os
import geopandas as gpd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

import sys

if len(sys.argv) > 1:
    folder = sys.argv[1]
else:
    folder = '../rainfall_data'

token = 'pk.eyJ1IjoiZm1jY2xlYW4iLCJhIjoiY2swbWpkcXY2MTRhNTNjcHBvM3R2Z2J6MiJ9.zOehGKT1N3eask9zsKmQqA'
stations = pd.DataFrame()
paths = [p for p in os.listdir(folder) if p.endswith('.txt')]
for locations_graph in paths:

    station = pd.read_csv(os.path.join(folder, locations_graph), sep='\t', parse_dates=[[0, 1]], header=[0, 1],
                        dayfirst=True, na_values='---')
    station = station.drop_duplicates(station.columns[0]).set_index(station.columns[0]).sort_index()
    station.index.name = 'time'
    station.columns = [' '.join([c.strip() for c in col if 'Unnamed' not in c]).lower() for col in station.columns]
    station.columns = [col.replace(' ', '_').replace('.', '') for col in station.columns]
    station['station_name'] = locations_graph[:-4]

    stations = pd.concat([stations, station])

# numeric_cols = ['wind_speed', 'rain', 'temp']

new_index = pd.np.array(stations.index)
new_index[(stations.station_name == 'ACTogether-HQ') &
          (stations.index < pd.datetime(day=31, month=7, year=2019))] += pd.np.timedelta64(87, 'D')

stations = stations.set_index(new_index)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

children = [dcc.Dropdown(options=[dict(label='Hourly', value='1H'),
                                  dict(label='Daily', value='1D'),
                                  dict(label='Monthly', value='1M')],
                         id='interval', value='1H'), dcc.Graph(id='rainfall'),
            dcc.Dropdown(options=[dict(label='Rain (mm)', value='rain'),
                                  dict(label='Wind Speed (km/h)', value='wind_speed'),
                                  dict(label='Temperature (C)', value='temp_out')
                                  ], id='variable', value='rain')]

df = gpd.read_file(os.path.join(folder, 'station_locations.geojson')).sort_values('Name')

lat = df.geometry.y
lon = df.geometry.x
values = df.merge(stations[stations.index == stations.index[100]], left_on='id', right_on='station_name')

data = [
    go.Densitymapbox(lat=lat, lon=lon, z=values.rain, radius=100),
    go.Scattermapbox(
        lat=lat,
        lon=lon,
        hovertext=df['Name'],
        hoverinfo='text',
        ids=df['id'],
        marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']),
        # z=values.rain, radius=10
    ),

]
layout = go.Layout(
    hovermode='closest',
    uirevision=True,
    mapbox=go.layout.Mapbox(
        accesstoken=token,
        center=go.layout.mapbox.Center(
            lat=df.geometry.y.mean(),
            lon=df.geometry.x.mean()
        ),
        zoom=10
    )
)
locations_figure = go.Figure(data, layout)

locations_graph = dcc.Graph(
    id='locations',
    figure=locations_figure,
    clear_on_unhover=True,
)

slider = dcc.Slider(id='time-slider',
                    min=0, max=len(stations.index.unique()), value=0, updatemode='mouseup')

children.append(slider)
children.append(locations_graph)

app.layout = html.Div(children=children)


@app.callback(Output(component_id='rainfall', component_property='figure'),
              [Input(component_id='locations', component_property='hoverData'),
               Input(component_id='interval', component_property='value'),
               Input(component_id='variable', component_property='value')])
def update_lines(hover, interval, variable):

    traces = []
    for name in stations.station_name.sort_values().unique():
        s = stations[stations.station_name == name].sort_index()[variable].resample(interval)
        if variable == 'temp_out':
            s = s.mean()
        else:
            s = s.sum()
        traces.append({
            'x': s.index, 'y': s.values,
            'type': 'line', 'name': name,
            'visible': (True if name == hover['points'][0]['id'] else 'legendonly') if hover else True})

    return {'data': traces, 'layout': dict(hovermode='closest', uirevision=True)}


@app.callback(Output(component_id='locations', component_property='figure'),
              [Input(component_id='time-slider', component_property='value'),
               Input(component_id='interval', component_property='value'),
               Input(component_id='variable', component_property='value')])
def update_map(value, interval, variable):
    s = stations.groupby(['station_name', pd.Grouper(freq=interval)]).sum().reset_index().set_index('level_1')
    times = get_times(interval)
    max_values = {
        'rain': {'1H': 50, '1D': 80, '1M': 300},
        'wind_speed': {'1H': 6, '1D': 6*24, '1M': 6*24*30},
        'temp_out': {'1H': 30, '1D': 30, '1M': 30}
    }
    merged = df.merge(s[s.index == times[value]], left_on='id', right_on='station_name', how='left')
    import math
    return go.Figure([

        go.Densitymapbox(
            lat=lat,
            lon=lon,
            z=merged[variable],
            radius=100,
            zmin=0,
            zmax=max_values[variable][interval],
            colorscale='Blues'
        ),

        go.Scattermapbox(
            lat=lat,
            lon=lon,
            hovertext=merged.apply(lambda row: '<b>{}</b><br>{}'.format(
                row.Name, '{} mm at {}'.format(round(row[variable], 1), times[value])
                if not math.isnan(row[variable]) else 'No Data'),
                axis=1),
            hoverinfo='text',
            ids=df['id'],
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']),
            text=df['Name'],
            textposition='top center',
            mode='markers+text'
        ),

    ], layout)


@app.callback(Output(component_id='time-slider', component_property='value'),
              [Input(component_id='rainfall', component_property='hoverData'),
               Input(component_id='interval', component_property='value')])
def update_slider_value(hover, interval):
    if hover:
        times = get_times(interval)
        time = pd.to_datetime(hover['points'][0]['x'])
        return times.get_loc(time, method='nearest')
    else:
        return 0


@app.callback(Output(component_id='time-slider', component_property='max'),
              [Input(component_id='interval', component_property='value')])
def update_slider_max(interval):
    return len(get_times(interval))


def get_times(interval):
    return stations.resample(interval).sum().index


# @app.callback(Output('download-link', 'href'),
#               [Input('dropdown', 'value')])
# def update_href(dropdown_value):
#     df = pd.DataFrame({dropdown_value: [1, 2, 3]})
#     relative_filename = os.path.join(
#         'downloads',
#         '{}-download.xlsx'.format(dropdown_value)
#     )
#     absolute_filename = os.path.join(os.getcwd(), relative_filename)
#     writer = pd.ExcelWriter(absolute_filename)
#     df.to_excel(writer, 'Sheet1')
#     writer.save()
#     return '/{}'.format(relative_filename)


@app.server.route('/<variable>/<frequency>')
def serve_static(variable, frequency):
    import flask
    import io
    csv = io.StringIO()
    stations.pivot(columns='station_name', values=variable).resample(frequency).sum().to_csv(csv)

    mem = io.BytesIO()
    mem.write(csv.getvalue().encode('utf-8'))
    mem.seek(0)

    return flask.send_file(mem,
                           mimetype='text/csv',
                           attachment_filename='shear-data.csv',
                           as_attachment=True)


if __name__ == '__main__':
    app.run_server(debug=True, port=8889, host='0.0.0.0')
