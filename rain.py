import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os
import plotly.express as px
import geopandas as gpd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

token = 'pk.eyJ1IjoiZm1jY2xlYW4iLCJhIjoiY2swbWpkcXY2MTRhNTNjcHBvM3R2Z2J6MiJ9.zOehGKT1N3eask9zsKmQqA'
stations = pd.DataFrame()
folder = '../rainfall_data'
paths = [p for p in os.listdir(folder) if p.endswith('.txt')]
for p in paths:
    station = pd.read_csv(os.path.join(folder, p), sep='\t', parse_dates=[[0,1]])
    station.columns = [c + ' ' if not 'Unnamed' in c else '' for c in station.columns ]
    station.columns = station.columns + station.iloc[0]
    station = station.drop(0)
    station['station_name'] = p[:-4]
    stations = pd.concat([stations, station])

stations = stations.set_index(pd.to_datetime(stations['Date Time'], format="%d/%m/%y %H:%M", errors='coerce'))
numeric_cols = ['Wind Speed', 'Rain']
stations[numeric_cols] = stations[numeric_cols].apply(pd.to_numeric)
new_index = pd.np.array(stations.index)
new_index[stations.station_name=='ACTogether-HQ'] = new_index[stations.station_name=='ACTogether-HQ'] + pd.np.timedelta64(87,'D')
stations = stations.set_index(new_index)
stations = stations.drop_duplicates(subset=['Date Time', 'station_name'])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


children = [
    html.H1(children=''),

    html.Div(children='''
        
    '''),
]
lines = []
for station_name in stations.station_name.sort_values().unique():
    s = stations[stations.station_name == station_name].sort_index()
    lines.append({'x': s.index, 'y': s['Rain'].values, 'type': 'line', 'name': station_name})
graph = dcc.Graph(
    id='rainfall',
    figure={
        'data': lines,
        'layout': {
            'title': ''
        }
    }
)

children.append(graph)

df = gpd.read_file('../rainfall_data/station_locations.geojson').sort_values('Name')

locations = go.Figure(go.Scattermapbox(lat=df.geometry.y, lon=df.geometry.x, hovertext=df['Name'],
                          hoverinfo='text',
                          ids=df['id'],
                                       marker=dict(color=['#1f77b4',
                                                          '#ff7f0e',
                                                          '#2ca02c',
                                                          '#d62728'])))

locations.update_layout(
    hovermode='closest',
    mapbox=go.layout.Mapbox(
        accesstoken=token,
        # bearing=0,
        center=go.layout.mapbox.Center(
            lat=df.geometry.y.mean(),
            lon=df.geometry.x.mean()
        ),
        # pitch=0,
        zoom=10
    )
)


# locations.update_layout(mapbox_style="osm")

p = dcc.Graph(
    id='locations',
    figure=locations,
    clear_on_unhover=True
)
children.append(p)

app.layout = html.Div(children=children)

@app.callback(Output(component_id='rainfall', component_property='figure'),
              [Input(component_id='locations', component_property='hoverData')])
def update_plot(hover):
    if hover:
        lines = []
        for station_name in stations.station_name.sort_values().unique():
            s = stations[stations.station_name == station_name].sort_index()
            lines.append({
                'x': s.index, 'y': s['Rain'].values,
                'type': 'line', 'name': station_name,
                'visible': True if station_name == hover['points'][0]['id'] else 'legendonly'})

        # s = stations[stations.station_name == hover['points'][0]['customdata'][0]].sort_index()
        # data = {'x': s.index, 'y': s['Rain'].values, 'type': 'line', 'name': station_name}

        return {'data': lines}
    else:
        return graph.figure
if __name__ == '__main__':
    app.run_server(debug=True, port=8889, host='0.0.0.0')
