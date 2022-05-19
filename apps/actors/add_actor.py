from platform import release
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app
from apps import dbconnect as db
from urllib.parse import urlparse, parse_qs

layout = html.Div(
    [
            dcc.Store('addactorprofile_toload',storage_type='memory',data=0),
            html.H2('Actor Details'), 
            html.Hr(),
            dbc.Alert(id='addactorprofile_alert', is_open=False),
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Actor Name", width=1),
                            dbc.Col(
                                dbc.Input(
                                    type='text',
                                    id='addactorprofile_title',
                                    placeholder='Title'
                                ),
                                width=5
                            )
                        ],
                        row=True
                    ),                   
                ]
            ),
            dbc.Button(
                'Submit',
                id='addactorprofile_submit',
                n_clicks=0,
                color='primary'
            ),

        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    'Actor Added Successfuly!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/actors/actors_home',
                        color='primary'
                    )
                )
            ],
            centered=True,
            id='addactorprofile_successmodal',
            backdrop='static'
        )
    ]
)

@app.callback(
    [
        Output('addactorprofile_alert', 'color'),
        Output('addactorprofile_alert', 'children'),
        Output('addactorprofile_alert', 'is_open'),
        Output('addactorprofile_successmodal', 'is_open')
    ],
    [
        Input('addactorprofile_submit', 'n_clicks')
    ],
    [
        State('addactorprofile_title', 'value'),
        State('url', 'search'),
    ]
)

def movieprofile_saveprofile(submitbtn, actor, search):
    ctx = dash.callback_context
    if ctx.triggered: 
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'addactorprofile_submit' and submitbtn: 
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not actor: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the Actor Name.'                            
            else:
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                        INSERT INTO actors (actor_name, actor_delete_ind)
                        VALUES (%s, %s)               
                    '''
                    values = [actor, False]

                    db.modifydatabase(sql, values)
                else:
                    raise PreventUpdate
                    
                modal_open = True
            
            return [alert_color, alert_text, alert_open, modal_open]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate