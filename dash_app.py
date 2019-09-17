import dash

from dash.dependencies import Input, Output
import dash_html_components as html


app = dash.Dash(__name__)

# app.scripts.config.serve_locally = True
# app.css.config.serve_locally = True

#
# for feature in lines['features']:
#
#     feature['geometry']['coordinates'] = swapCoords(feature['geometry']['coordinates'])


app.layout = html.Div([
    # dash_leaflet.DashLeaflet(
    #     id='getMap',
    #
    #     mapOptions={
    #
    #         'bounds': [[47.82, 10.50], [45.80, 5.93]],
    #         'maxZoom': 18,
    #         'maxBounds': [[47.82, 10.50], [45.80, 5.93]]
    #
    #     },
    #
    #     style={'height': '95vh'},
    #
    #     baselayer=
    #         {
    #             'name': 'OSM',
    #             'url': 'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png',
    #             # 'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    #         }
    # ),

    html.Div(id='output')
])



if __name__ == '__main__':

    app.run_server(debug=False, host='0.0.0.0')
