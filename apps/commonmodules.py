import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app 

navlink_style = {
    'color': '#fff'
}

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("156 Case App", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/home",
        ),
        dbc.NavLink("Home", href="/home", style=navlink_style),
        dbc.NavLink("Movies", href="/movies/movies_home", style=navlink_style),
        dbc.NavLink("Genres", href="/genres", style=navlink_style),
    ],
    dark=True,
    color='black'
)