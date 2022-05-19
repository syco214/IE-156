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
            dcc.Store('addproducerprofile_toload',storage_type='memory',data=0),
            html.H2('Producer Details'), 
            html.Hr(),
            dbc.Alert(id='addproducerprofile_alert', is_open=False),
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Producer Name", width=1),
                            dbc.Col(
                                dbc.Input(
                                    type='text',
                                    id='addproducerprofile_title',
                                    placeholder='Producer'
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
                id='addproducerprofile_submit',
                n_clicks=0,
                color='primary'
            ),

        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    'Producer Added Successfuly!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/producers/producers_home',
                        color='primary'
                    )
                )
            ],
            centered=True,
            id='addproducerprofile_successmodal',
            backdrop='static'
        )
    ]
)

@app.callback(
    [
        Output('addproducerprofile_alert', 'color'),
        Output('addproducerprofile_alert', 'children'),
        Output('addproducerprofile_alert', 'is_open'),
        Output('addproducerprofile_successmodal', 'is_open')
    ],
    [
        Input('addproducerprofile_submit', 'n_clicks')
    ],
    [
        State('addproducerprofile_title', 'value'),
        State('url', 'search'),
    ]
)

def movieprofile_saveprofile(submitbtn, producer, search):
    ctx = dash.callback_context
    if ctx.triggered: 
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'addproducerprofile_submit' and submitbtn: 
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not producer: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the Producer Name.'                            
            else:
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                        INSERT INTO producers (producer_name, producer_delete_ind)
                        VALUES (%s, %s)               
                    '''
                    values = [producer, False]

                    db.modifydatabase(sql, values)
                else:
                    raise PreventUpdate
                    
                modal_open = True
            
            return [alert_color, alert_text, alert_open, modal_open]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate