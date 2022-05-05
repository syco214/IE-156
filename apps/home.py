import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app

layout = html.Div(
    [
        html.H2('Welcome to our app!'),
        html.Hr(),
        html.Div(
            [
                html.Span(
                    "Through this app, you can manage a database, of movies that are classified according to genres.",
                ),
                html.Br(),
                html.Br(),
                html.Span(
                    "Contact the owner if you need assistance!",
                    style={'font-style':'italic'}
                ),
            ]
        )
    ]
)