from app import app
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import os
import geopandas as gpd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/weather'))

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

df = gpd.read_file(os.path.join(folder, 'station_locations.geojson')).sort_values('Name')

lat = df.geometry.y
lon = df.geometry.x
values = df.merge(stations[stations.index == stations.index[100]], left_on='id', right_on='station_name')

data = [
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
locations_layout = go.Layout(
    hovermode='closest',
    margin=go.layout.Margin(l=0, r=0, b=0, t=0),
    height=300,
    uirevision=True,
    mapbox=go.layout.Mapbox(
        accesstoken=os.environ['MAPBOX_ACCESS_TOKEN'],
        center=go.layout.mapbox.Center(
            lat=df.geometry.y.mean(),
            lon=df.geometry.x.mean()
        ),
        zoom=10
    )
)

locations_figure = go.Figure(data, locations_layout)

locations_graph = dcc.Graph(
    id='locations',
    figure=locations_figure,
    clear_on_unhover=True,
)

children = [

    html.Div(dcc.Loading(dcc.Graph(id='weather')), id='weather-container'),
    html.Div(
        [locations_graph,
         html.Div(children=[
             html.Div(
                 dcc.Dropdown(options=[
                     dict(label='Hourly', value='1H'),
                     dict(label='Daily', value='1D'),
                     dict(label='Monthly', value='1M')],
                     id='interval', value='1H', className='dropdown'),
             ),

             dcc.Dropdown(options=[
                 dict(label='Rain (mm)', value='rain'),
                 dict(label='Wind Speed (km/h)', value='wind_speed'),
                 dict(label='Temperature (C)', value='temp_out')
             ], id='variable', value='rain', className='dropdown'),

             html.A(id='download-link', children='Download Data')

         ], className='weather-dropdowns'),
         ],
        id='map-and-dropdown-container'
    )

]

def layout(navbar):
    return html.Div(children=[navbar] + children, className='main')


@app.callback(Output(component_id='weather', component_property='figure'),
              [Input(component_id='locations', component_property='clickData'),
               Input(component_id='interval', component_property='value'),
               Input(component_id='variable', component_property='value')])
def update_lines(clicked_point, interval, variable):

    traces = []
    for name in stations.station_name.sort_values().unique():
        s = stations[stations.station_name == name].sort_index()[variable].resample(interval)
        if variable == 'temp_out':
            s = s.mean()
        else:
            s = s.sum()
        traces.append(go.Scatter(
            x=s.index, y=s.values,
            name=name,
            visible=(True if name == clicked_point['points'][0]['id'] else 'legendonly') if clicked_point else True)
        )

    return go.Figure(data=traces, layout=go.Layout(
        legend_orientation="h",
        hovermode='closest',
        uirevision=True,
        margin=go.layout.Margin(l=30, r=0, b=30, t=30)
        ))

@app.callback(Output('download-link', 'href'),
              [
                  Input(component_id='interval', component_property='value'),
                  Input(component_id='variable', component_property='value')
               ])
def update_href(interval, variable):
    return '/{}/{}'.format(variable, interval)


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
                           attachment_filename='shear-{}.csv'.format(variable),
                           as_attachment=True)
