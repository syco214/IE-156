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
        dbc.DropdownMenu(
            label="Search Movies By",
            color="secondary",
            style={
                "padding": "10px 10px 10px 10px"
            },
            toggleClassName="border-none",
            children=[
                dbc.DropdownMenuItem("Movies", href="/movies/movies_home"),
                dbc.DropdownMenuItem("Actors", href="/actors/actors_home"),
                dbc.DropdownMenuItem("Producers", href="/producers/producers_home"),
                dbc.DropdownMenuItem("Country", href="/country/country_home"),
                dbc.DropdownMenuItem("Data", href="/data"),
            ],),
        dbc.DropdownMenu(
            label="Add",
            color="secondary",
            style={
                "padding": "10px 10px 10px 10px"
            },
            toggleClassName="border-none",
            children=[
                dbc.DropdownMenuItem("Movies", href="/movies/movies_profile?mode=add"),
                dbc.DropdownMenuItem("Actors", href="/actors/add_actors?mode=add"),
                dbc.DropdownMenuItem("Producers", href="/producers/add_producers?mode=add"),
            ],),
        dbc.DropdownMenu(
            label="Transact",
            color="secondary",
            style={
                "padding": "10px 10px 10px 10px"
            },
            toggleClassName="border-none",
            children=[
                dbc.DropdownMenuItem("Customer", href="/tickets/tickets_home"),
                dbc.DropdownMenuItem("Producer", href="/prodtran/prodtran_home"),
            ],),
    ],
    dark=True,
    color='black'
)