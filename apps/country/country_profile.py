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
            dcc.Store('countryprofile_toload',storage_type='memory',data=0),
            html.H2('Country Details'), 
            html.Hr(),
            dbc.Alert(id='countryprofile_alert', is_open=False),
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Country", width=1),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='countryprofile_country',
                                    placeholder='Country'
                                ),
                                width=5
                            )
                        ],
                        row=True
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Movie", width=1),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='countryprofile_movie',
                                    placeholder='Movie'
                                ),
                                width=5
                            )
                        ],
                        row=True
                    ),
                ]
            ),
            html.Div(
                [
                    dbc.Form(
                        dbc.FormGroup(
                            [
                                dbc.Checklist(
                                    id = 'countryprofile_removerecord',
                                    options = [
                                        {
                                            'label': "Mark for Deletion", 
                                            'value': 1
                                        }
                                    ],
                                    style={'fontWeight':'bold'},
                                )
                            ]
                        )
                    )
                ],
                id='countryprofile_remove_div',
                style={'display':'none'}
            ),
            dbc.Button(
                'Submit',
                id='countryprofile_submit',
                n_clicks=0,
                color='primary'
            ),
        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    'country Added Successfuly!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/countrys/countrys_home',
                        color='primary'
                    )
                )
            ],
            centered=True,
            id='countryprofile_successmodal',
            backdrop='static'
        )
    ]
)

@app.callback(
    [
        Output('countryprofile_country', 'options'), 
        Output('countryprofile_toload', 'data'),
        Output('countryprofile_remove_div', 'style')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def countryprofile_populatecountries(pathname, search):
    if pathname == '/country/country_profile':
        sql = """ 
        SELECT country_name as label, country_id as value 
        FROM countries 
        WHERE country_delete_ind = False 
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        country_options = df.to_dict('records')
        parsed = urlparse(search) 
        create_mode = parse_qs(parsed.query)['mode'][0] 
        to_load = 1 if create_mode == 'edit' else 0
        if create_mode == 'edit': 
            remove_div_style = {'display': 'unset'} 
        else: 
            remove_div_style = {'display': 'none'}
        return [country_options, to_load, remove_div_style]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('countryprofile_movie', 'options'),          
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def countryprofile_populatemovies(pathname, search):
    if pathname == '/country/country_profile':
        sql = """ 
        SELECT movie_title as label, movie_id as value 
        FROM movies 
        WHERE movie_delete_ind = False 
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        movie_options = df.to_dict('records')
        parsed = urlparse(search) 
        create_mode = parse_qs(parsed.query)['mode'][0] 
        return [movie_options]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('countryprofile_alert', 'color'),
        Output('countryprofile_alert', 'children'),
        Output('countryprofile_alert', 'is_open'),
        Output('countryprofile_successmodal', 'is_open')
    ],
    [
        Input('countryprofile_submit', 'n_clicks')
    ],
    [
        State('countryprofile_country', 'value'),
        State('countryprofile_movie', 'value'),
        State('url', 'search'),
        State('countryprofile_removerecord', 'value')
    ]
)

def countryprofile_saveprofile(submitbtn, country, movie, search, remove_checked):
    ctx = dash.callback_context
    if ctx.triggered: 
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'countryprofile_submit' and submitbtn: 
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not country: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the country.'
            elif not movie: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the Movie.'
            else:
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                        INSERT INTO movie_countries (country_id, movie_id, movie_country_delete_ind)
                        VALUES (%s, %s, %s)                
                    '''
                    values = [country, movie, False]

                    db.modifydatabase(sql, values)
                elif create_mode == 'edit':
                    moviecountryid = int(parse_qs(parsed.query)['moviecountriesid'][0])
                    sql = ''' 
                        UPDATE movie_countries
                        SET 
                            country_id = %s, 
                            movie_id = %s, 
                            movie_country_delete_ind = %s 
                        WHERE 
                            movie_countries_id = %s
                    '''
                    delete_ind = bool(remove_checked)
                    values = [country, movie, delete_ind, moviecountryid]
                    db.modifydatabase(sql, values)
                else:
                    raise PreventUpdate
                    
                modal_open = True
            
            return [alert_color, alert_text, alert_open, modal_open]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate