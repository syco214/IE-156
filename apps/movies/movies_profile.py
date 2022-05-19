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
            dcc.Store('movieprofile_toload',storage_type='memory',data=0),
            html.H2('Movie Details'), 
            html.Hr(),
            dbc.Alert(id='movieprofile_alert', is_open=False),
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Title", width=1),
                            dbc.Col(
                                dbc.Input(
                                    type='text',
                                    id='movieprofile_title',
                                    placeholder='Title'
                                ),
                                width=5
                            )
                        ],
                        row=True
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Year Produced", width=1),
                            dbc.Col(
                                dbc.Input(
                                    type='number',
                                    id='movieprofile_year',
                                    placeholder='Year'
                                ),
                                width=5
                            )
                        ],
                        row=True
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Movie Description", width=1),
                            dbc.Col(
                                dbc.Input(
                                    type='text',
                                    id='movieprofile_description',
                                    placeholder='Description'
                                ),
                                width=5
                            )
                        ],
                        row=True
                    ),                                     
                    dbc.FormGroup(
                        [
                            dbc.Label("Genre", width=1),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='movieprofile_genre',
                                    placeholder='Genre'
                                ),
                                width=5
                            )
                        ],
                        row=True
                    ),
                    dbc.FormGroup(
                        [
                            dbc.Label("Producer", width=1),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='movieprofile_producer',
                                    placeholder='Producer'
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
                                    id = 'movieprofile_removerecord',
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
                id='movieprofile_remove_div',
                style={'display':'none'}
            ),
            dbc.Button(
                'Submit',
                id='movieprofile_submit',
                n_clicks=0,
                color='primary'
            ),

        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4('Save Success')
                ),
                dbc.ModalBody(
                    'Movie Added Successfuly!'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Proceed",
                        href='/movies/movies_home',
                        color='primary'
                    )
                )
            ],
            centered=True,
            id='movieprofile_successmodal',
            backdrop='static'
        )
    ]
)
@app.callback(
    [
        Output('movieprofile_genre', 'options'),          
        Output('movieprofile_toload', 'data'),
        Output('movieprofile_remove_div', 'style')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def movieprofile_populategenres(pathname, search):
    if pathname == '/movies/movies_profile':
        sql = """ 
        SELECT genre_name as label, genre_id as value 
        FROM genres 
        WHERE genre_delete_ind = False 
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        genre_options = df.to_dict('records')
        parsed = urlparse(search) 
        create_mode = parse_qs(parsed.query)['mode'][0] 
        to_load = 1 if create_mode == 'edit' else 0
        if create_mode == 'edit': 
            remove_div_style = {'display': 'unset'} 
        else: 
            remove_div_style = {'display': 'none'}
        return [genre_options, to_load, remove_div_style]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('movieprofile_producer', 'options'),          
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def movieprofile_populateproducers(pathname, search):
    if pathname == '/movies/movies_profile':
        sql = """ 
        SELECT producer_name as label, producer_id as value 
        FROM producers 
        WHERE producer_delete_ind = False 
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        producer_options = df.to_dict('records')
        parsed = urlparse(search) 
        create_mode = parse_qs(parsed.query)['mode'][0] 
        return [producer_options]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('movieprofile_alert', 'color'),
        Output('movieprofile_alert', 'children'),
        Output('movieprofile_alert', 'is_open'),
        Output('movieprofile_successmodal', 'is_open')
    ],
    [
        Input('movieprofile_submit', 'n_clicks')
    ],
    [
        State('movieprofile_title', 'value'),
        State('movieprofile_year', 'value'),
        State('movieprofile_description', 'value'),        
        State('movieprofile_genre', 'value'),
        State('movieprofile_producer', 'value'),
        State('url', 'search'),
        State('movieprofile_removerecord', 'value')
    ]
)

def movieprofile_saveprofile(submitbtn, title, year, description, genre, producer, search, remove_checked):
    ctx = dash.callback_context
    if ctx.triggered: 
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'movieprofile_submit' and submitbtn: 
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not title: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie title.'
            elif not year: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the year movie was produced.'
            elif not description: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie description.'
            elif not genre: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the movie genre.'                
            elif not producer: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please the movie producer.'                                
            else:
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                        INSERT INTO movies (movie_title, movie_produced_year,
                            movie_description, genre_id, producer_id, movie_delete_ind)
                        VALUES (%s, %s, %s, %s, %s, %s)               
                    '''
                    values = [title, year, description, genre, producer, False]

                    db.modifydatabase(sql, values)
                elif create_mode == 'edit':
                    movieid = int(parse_qs(parsed.query)['movieid'][0])
                    sql = ''' 
                        UPDATE movies 
                        SET 
                            movie_title = %s, 
                            movie_produced_year = %s,
                            movie_description = %s,
                            genre_id = %s,
                            producer_id = %s,
                            movie_delete_ind = %s 
                        WHERE 
                            movie_id = %s
                    '''
                    delete_ind = bool(remove_checked)
                    values = [title, year, description, genre, producer, delete_ind, movieid]
                    db.modifydatabase(sql, values)
                else:
                    raise PreventUpdate
                    
                modal_open = True
            
            return [alert_color, alert_text, alert_open, modal_open]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate