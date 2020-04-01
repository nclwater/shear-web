import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Flooding", href="/flood")),
        dbc.NavItem(dbc.NavLink("Rainfall", href="/rain")),
    ],
    brand="Kampala Flood Risk and Rainfall Data Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
)

from app import app
from apps import flood, rain


app.layout = html.Div([
    dcc.Location(id='url', pathname='/flood', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/flood':
        return flood.layout(navbar)
    elif pathname == '/rain':
        return rain.layout(navbar)
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)