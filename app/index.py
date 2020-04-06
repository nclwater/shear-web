import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from app import app
from apps import flood, weather

app.title = "Kampala Flood Risk and Weather Data Dashboard"

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Flooding", href="/flood")),
        dbc.NavItem(dbc.NavLink("Weather", href="/weather")),
        dbc.NavItem(dbc.NavLink("GitHub", href="http://github.com/fmcclean/shear-web")),
    ],
    brand=app.title,
    brand_href="#",
    color="primary",
    dark=True,
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

server = app.server


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return html.Div(id='home')
    if pathname == '/flood':
        return flood.layout(navbar)
    elif pathname == '/weather':
        return weather.layout(navbar)
    else:
        return '404'


@app.callback(Output('url', 'pathname'), [Input('home', 'children')])
def home(_):
    return '/flood'


if __name__ == '__main__':
    app.run_server(debug=True)
