from app import app
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import os

df = gpd.read_file(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/extents.gpkg')))
df.duration = (df.duration / 3600).astype(int)

e = df[(df.threshold == df.threshold[0]) & (df.run_id == df.run_id[0])]

building_depths = gpd.read_file(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/building_depths.gpkg')))

figure_layout = go.Layout(
    hovermode='closest',
    margin=go.layout.Margin(l=0, r=0, b=0, t=0),
    mapbox_style="basic",
    uirevision=True,
    mapbox_accesstoken=os.environ['MAPBOX_ACCESS_TOKEN'],
    mapbox=go.layout.Mapbox(
        center=go.layout.mapbox.Center(
            lat=e.geometry.centroid.y.mean(),
            lon=e.geometry.centroid.x.mean()
        ),
        zoom=11
    )
)

graph = dcc.Graph(
    id='map',
    figure=go.Figure(),
    clear_on_unhover=True,
)


thresholds = df.threshold.unique()
rainfall = df.rainfall.unique()
duration = df.duration.unique()
threshold_marks = {key: str(val) for key, val in enumerate(thresholds)}
rainfall_marks = {key: str(val) for key, val in enumerate(rainfall)}
duration_marks = {key: str(val) for key, val in enumerate(duration)}


def create_slider(title, name, marks):
    return html.Div(
        children=[
            title,
            dcc.Slider(
                id=name,
                min=0,
                max=len(marks)-1,
                marks=marks,
                value=0,
                updatemode='drag'
            )
        ],
        style={
            'margin': 40,
            'marginTop': 0,
            'marginBottom': 20,
            'pointerEvents': 'auto'
        }, className="three columns"
    )


slider = create_slider('Depth Threshold (m)', 'threshold-slider', threshold_marks)
rainfall_slider = create_slider('Rainfall Amount (mm)', 'weather-slider', rainfall_marks)
duration_slider = create_slider('Rainfall Duration (hrs)', 'duration-slider', marks=duration_marks)

green_areas = dcc.Checklist(id='green-areas', options=[{'label': 'Green Areas', 'value': '-'}])
green_areas_div = html.Div(green_areas, className='checkbox')

density = dcc.Checklist(id='density', options=[{'label': 'Show heat-map', 'value': '-'}])
density_div = html.Div(density,  className='checkbox')

buildings = dcc.Checklist(id='buildings', options=[{'label': 'Show building depths', 'value': '-'}])
buildings_div = html.Div(buildings, className='checkbox')

basemap_dropdown = html.Div(children=[

    dcc.Dropdown(
        id='basemap',
        options=[
            {
                'label': s.title().replace('-', ' '), 'value': s} for s in
            [
                "basic",
                "streets",
                "outdoors",
                "light",
                "dark",
                "satellite",
                "satellite-streets",
                "open-street-map",
                "carto-positron",
                "carto-darkmatter",
                "stamen-terrain",
                "stamen-toner",
                "stamen-watercolor"
            ]
        ],
        value='basic'),

])

controls = html.Div(id='controls',
                    children=[
                        html.Div(id='sliders', children=[
                            slider,
                            rainfall_slider,
                            duration_slider
                        ]),
                        html.Div(children=[green_areas_div, density_div, buildings_div, basemap_dropdown],
                                 id='checkbox-container')],
                    )

def layout(navbar):
    return html.Div(children=[navbar, controls, html.Div(graph, id='map-container')],
                    className='main')


below = ''


@app.callback(Output(component_id='map', component_property='figure'),
              [Input(component_id='threshold-slider', component_property='value'),
               Input(component_id='weather-slider', component_property='value'),
               Input(component_id='duration-slider', component_property='value'),
              Input(component_id='green-areas', component_property='value'),
               Input(component_id='basemap', component_property='value'),
               Input(component_id='density', component_property='value'),
               Input(component_id='buildings', component_property='value'),
               ])
def update_plot(threshold: int = 0, rain: int = 0, dur: int = 0,
                green: bool = False, bm: bool = False, dens: bool = False, build: bool = False):

    green = 1 if green else 0

    features = df[(df.threshold == float(threshold_marks[threshold])) &
                  (df.rainfall == float(rainfall_marks[rain])) &
                  (df.duration == float(duration_marks[dur])) &
                  (df.green == green)]

    traces = list()

    traces.append(
        go.Choroplethmapbox(geojson=features.geometry.__geo_interface__,
                            locations=features.index,
                            z=features.threshold,
                            showscale=False,
                            colorscale=[[0, 'royalblue'], [1, 'royalblue']],
                            marker=dict(opacity=0.5),
                            hoverinfo='skip',
                            below=below
                            ))
    if build or dens:
        thresh = float(threshold_marks[threshold])
        depth_values = building_depths['max_depth_{}'.format(features.run_id.iloc[0])]
        buildings_above_threshold = building_depths[depth_values >= thresh]

        if build:

            t = go.Choroplethmapbox(
                geojson=buildings_above_threshold.geometry.__geo_interface__,
                locations=buildings_above_threshold.index,
                z=depth_values[depth_values >= thresh],
                below=below
            )
            traces.append(t)
        else:
            traces.append(go.Choroplethmapbox())

        if dens:
            traces.append(go.Densitymapbox(lat=buildings_above_threshold.y,
                                           lon=buildings_above_threshold.x,
                                           z=depth_values[depth_values >= thresh],
                                           radius=10,
                                           hoverinfo='skip',
                                           showscale=True if not build else False,
                                           below=below
                                           ))
        else:
            traces.append(go.Densitymapbox())

    return go.Figure(traces, figure_layout.update(mapbox_style=bm))
