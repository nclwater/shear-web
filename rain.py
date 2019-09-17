import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os
import geopandas as gpd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

token = 'pk.eyJ1IjoiZm1jY2xlYW4iLCJhIjoiY2swbWpkcXY2MTRhNTNjcHBvM3R2Z2J6MiJ9.zOehGKT1N3eask9zsKmQqA'
stations = pd.DataFrame()
folder = '../rainfall_data'
paths = [p for p in os.listdir(folder) if p.endswith('.txt')]
for locations_graph in paths:
    station = pd.read_csv(os.path.join(folder, locations_graph), sep='\t', parse_dates=[[0, 1]])
    station.columns = [c + ' ' if 'Unnamed' not in c else '' for c in station.columns]
    station.columns = station.columns + station.iloc[0]
    station = station.drop(0)
    station['station_name'] = locations_graph[:-4]
    stations = pd.concat([stations, station])

stations = stations.set_index(pd.to_datetime(stations['Date Time'], format="%d/%m/%y %H:%M", errors='coerce'))
numeric_cols = ['Wind Speed', 'Rain']
stations[numeric_cols] = stations[numeric_cols].apply(pd.to_numeric)
new_index = pd.np.array(stations.index)
new_index[stations.station_name == 'ACTogether-HQ'] = new_index[stations.station_name == 'ACTogether-HQ'] \
                                                      + pd.np.timedelta64(87, 'D')
stations = stations.set_index(new_index)
stations = stations.drop_duplicates(subset=['Date Time', 'station_name'])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

children = [html.H1(children=''),  html.Div(children='')]


children.append(dcc.Graph(id='rainfall'))

df = gpd.read_file('../rainfall_data/station_locations.geojson').sort_values('Name')

lat=df.geometry.y
lon=df.geometry.x
values = df.merge(stations[stations.index == stations.index[100]], left_on='id', right_on='station_name')
print(values.Rain)
data = go.Data([
    go.Densitymapbox(lat=lat, lon=lon, z=values.Rain, radius=100),
    go.Scattermapbox(
        lat=lat,
        lon=lon,
        hovertext=df['Name'],
        hoverinfo='text',
        ids=df['id'],
        marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']),
        # z=values.Rain, radius=10
    ),

])
layout = go.Layout(
    hovermode='closest',
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
    clear_on_unhover=True
)

slider = dcc.Slider(id='time-slider',
                    min=0, max=len(stations.index.unique()), value=0, updatemode='mouseup')

children.append(slider)
children.append(locations_graph)



app.layout = html.Div(children=children)

@app.callback(Output(component_id='rainfall', component_property='figure'),
              [Input(component_id='locations', component_property='hoverData')])
def update_plot(hover):

    traces = []
    for name in stations.station_name.sort_values().unique():
        s = stations[stations.station_name == name].sort_index()
        traces.append({
            'x': s.index, 'y': s['Rain'].values,
            'type': 'line', 'name': name,
            'visible': (True if name == hover['points'][0]['id'] else 'legendonly') if hover else True})

    return {'data': traces}

@app.callback(Output(component_id='locations', component_property='figure'),
              [Input(component_id='time-slider', component_property='value')])
def update_plot(value):
    values = df.merge(stations[stations.index == stations.index[value]], left_on='id', right_on='station_name')
    print(value)
    data = [
        go.Densitymapbox(lat=lat, lon=lon, z=values.Rain, radius=100, zmin=0, zmax=10),
        go.Scattermapbox(
            lat=lat,
            lon=lon,
            hovertext=df['Name'],
            hoverinfo='text',
            ids=df['id'],
            marker=dict(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']),
            # z=values.Rain, radius=10
        ),

    ]

    return go.Figure(data, layout)

if __name__ == '__main__':
    app.run_server(debug=True, port=8889, host='0.0.0.0')
