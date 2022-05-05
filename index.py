import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import webbrowser

from app import app
from apps import commonmodules as cm
from apps import home
from apps.movies import movies_home, movies_profile

CONTENT_STYLE = {
    "margin-left": "1em",
    "margin-right": "1em",
    "padding": "1em 1em",
}

server = app.server

app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=True),
        cm.navbar,
        html.Div(id='page-content', style=CONTENT_STYLE),
    ]
)

@app.callback(
    [
        Output('page-content', 'children')
    ],
    [
        Input('url','pathname')
    ]
)
def displaypage(pathname):
    ctx = dash.callback_context
    returnlayout = []

    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'url':
            if pathname == '/' or pathname == '/home':
                returnlayout = home.layout
            elif pathname == '/movies/movies_home':
                returnlayout = movies_home.layout
            elif pathname == '/movies/movies_profile':
                returnlayout = movies_profile.layout
            else:
                returnlayout = 'error404'
        else: 
            raise PreventUpdate
    else: 
        raise PreventUpdate
    
    return [returnlayout]

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new=0, autoraise=True)
    app.run_server(debug=False)