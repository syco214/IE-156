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
            dcc.Store('actorprofile_toload',storage_type='memory',data=0),
            html.H2('Actor Details'), 
            html.Hr(),
            dbc.Alert(id='actorprofile_alert', is_open=False),
            dbc.Form(
                [
                    dbc.FormGroup(
                        [
                            dbc.Label("Actor", width=1),
                            dbc.Col(
                                dcc.Dropdown(
                                    id='actorprofile_actor',
                                    placeholder='Actor'
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
                                    id='actorprofile_movie',
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
                                    id = 'actorprofile_removerecord',
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
                id='actorprofile_remove_div',
                style={'display':'none'}
            ),
            dbc.Button(
                'Submit',
                id='actorprofile_submit',
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
            id='actorprofile_successmodal',
            backdrop='static'
        )
    ]
)

@app.callback(
    [
        Output('actorprofile_actor', 'options'), 
        Output('actorprofile_toload', 'data'),
        Output('actorprofile_remove_div', 'style')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def actorprofile_populateactors(pathname, search):
    if pathname == '/actors/actors_profile':
        sql = """ 
        SELECT actor_name as label, actor_id as value 
        FROM actors 
        WHERE actor_delete_ind = False 
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        actor_options = df.to_dict('records')
        parsed = urlparse(search) 
        create_mode = parse_qs(parsed.query)['mode'][0] 
        to_load = 1 if create_mode == 'edit' else 0
        if create_mode == 'edit': 
            remove_div_style = {'display': 'unset'} 
        else: 
            remove_div_style = {'display': 'none'}
        return [actor_options, to_load, remove_div_style]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('actorprofile_movie', 'options'),          
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)
def actorprofile_populatemovies(pathname, search):
    if pathname == '/actors/actors_profile':
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
        Output('actorprofile_alert', 'color'),
        Output('actorprofile_alert', 'children'),
        Output('actorprofile_alert', 'is_open'),
        Output('actorprofile_successmodal', 'is_open')
    ],
    [
        Input('actorprofile_submit', 'n_clicks')
    ],
    [
        State('actorprofile_actor', 'value'),
        State('actorprofile_movie', 'value'),
        State('url', 'search'),
        State('actorprofile_removerecord', 'value')
    ]
)

def actorprofile_saveprofile(submitbtn, actor, movie, search, remove_checked):
    ctx = dash.callback_context
    if ctx.triggered: 
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'actorprofile_submit' and submitbtn: 
            alert_open = False
            modal_open = False
            alert_color = ''
            alert_text = ''

            if not actor: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the Actor.'
            elif not movie: 
                alert_open = True
                alert_color = 'danger'
                alert_text = 'Check your inputs. Please supply the Movie.'
            else:
                parsed = urlparse(search)
                create_mode = parse_qs(parsed.query)['mode'][0]
                if create_mode == 'add':
                    sql = '''
                        INSERT INTO movie_actors (actor_id, movie_id, movie_actor_delete_ind)
                        VALUES (%s, %s, %s)                
                    '''
                    values = [actor, movie, False]

                    db.modifydatabase(sql, values)
                elif create_mode == 'edit':
                    movieactorid = int(parse_qs(parsed.query)['movieactorsid'][0])
                    sql = ''' 
                        UPDATE movie_actors 
                        SET 
                            actor_id = %s, 
                            movie_id = %s, 
                            movie_actor_delete_ind = %s 
                        WHERE 
                            movie_actors_id = %s
                    '''
                    delete_ind = bool(remove_checked)
                    values = [actor, movie, delete_ind, movieactorid]
                    db.modifydatabase(sql, values)
                else:
                    raise PreventUpdate
                    
                modal_open = True
            
            return [alert_color, alert_text, alert_open, modal_open]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate