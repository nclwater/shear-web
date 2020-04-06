from app import app
import dash_core_components as dcc
import dash_html_components as html
import os
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from . import utils
import numpy as np
from plotly.colors import DEFAULT_PLOTLY_COLORS

stations = utils.read_weather_data()
locations = utils.read_station_locations()


locations_figure = go.Figure(
    data=[
        go.Scattermapbox(
            lat=locations.geometry.y,
            lon=locations.geometry.x,
            hovertext=locations['Name'],
            hoverinfo='text',
            ids=locations['id'],
            marker=dict(
                color=DEFAULT_PLOTLY_COLORS[:5],
                size=10
            ),
        )],

    layout=go.Layout(
        hovermode='closest',
        margin=go.layout.Margin(l=0, r=0, b=0, t=0),
        uirevision=True,
        mapbox=go.layout.Mapbox(
            accesstoken=os.environ['MAPBOX_ACCESS_TOKEN'],
            center=go.layout.mapbox.Center(
                lat=locations.geometry.y.mean(),
                lon=locations.geometry.x.mean()),
            zoom=10
        )))

locations_graph = dcc.Graph(
    id='locations',
    figure=locations_figure
)

children = [

    html.Div(id='loading-container', children=[
        dcc.Loading(dcc.Graph(id='weather', clear_on_unhover=True))]),
    html.Div(
        [html.Div(locations_graph, id='locations-container'),
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
    for _, row in locations.iterrows():
        s = stations[stations.station_name == row.id].sort_index()[variable].resample(interval)
        if variable == 'temp_out':
            s = s.mean()
        else:
            s = s.sum()
        traces.append(go.Scatter(
            x=s.index, y=s.values,
            name=row.Name,
            visible=(True if row.id == clicked_point['points'][0]['id'] else 'legendonly')
            if clicked_point else True
        ))

    return go.Figure(data=traces, layout=go.Layout(
        hovermode='closest',
        uirevision=True,
        margin=go.layout.Margin(l=30, r=0, b=30, t=30),
        colorway=DEFAULT_PLOTLY_COLORS
        ))

@app.callback(Output(component_id='locations', component_property='figure'),
              [Input(component_id='weather', component_property='hoverData')])
def highlight_point(hover_data):
    if hover_data is None:
        return locations_figure

    fig = locations_figure.to_dict()

    station_id = locations.id.values[hover_data['points'][0]['curveNumber']]
    ids = fig['data'][0]['ids']
    idx = np.where(ids == station_id)[0]
    size = np.full(len(ids), 5)
    size[idx] = 12

    fig['data'][0]['marker']['size'] = size

    return fig


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
