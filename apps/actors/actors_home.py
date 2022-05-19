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
        html.Div(
            [
                dcc.Store(id='actorprofile_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2('Actor Movie Details'), 
        html.Hr(),
        dbc.Alert(id='actorprofile_alert', is_open=False),
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.H3('Manage Records')
                    ]
                ),
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                dbc.Button(
                                    "Add Actor",
                                    href='/actors/actors_profile?mode=add',
                                    color='primary',
                                    className="me-1"
                                )
                            ],
                            className="d-grid gap-2 mx-auto"
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Download Movie Actor Data'),
                                dbc.Button(
                                    'CSV',
                                    id='downloadmovieactorstable',
                                    color="primary",
                                    n_clicks=0,
                                    className="me-1"
                                ),
                                dcc.Download(id="download-component"),
                            ],
                            className="d-grid gap-2 mx-auto"
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Actors'),
                                html.Div(
                                    dbc.Form(
                                        dbc.FormGroup(
                                            [
                                                dbc.Label("Search Title", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='actorhome_titlefilter',
                                                        placeholder='Actor Name'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                            row=True
                                        )
                                    )
                                ),
                                html.Div(
                                    "Table with actors will go here",
                                    id = 'actorhome_actorlist'
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

@app.callback(
    [
        Output('actorhome_actorlist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('actorhome_titlefilter', 'value')
    ]
)
def actorhome_loadactorlist(pathname, filter_title):
    if pathname == '/actors/actors_home':
        sql = """ SELECT movie_actors_id, actor_name, movie_title 
            FROM movie_actors m 
                INNER JOIN movies g ON m.movie_id = g.movie_id
                INNER JOIN actors a ON m.actor_id = a.actor_id 
            WHERE movie_actor_delete_ind = false
        """
        values = []
        if filter_title:
            sql += " AND actor_name ILIKE %s"
            values += [f"%{filter_title}%"]
        cols = ['ID', 'Actor', 'Movie Title']
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape[0]:
            linkcolumn = {}
            for index, row in df.iterrows():
                linkcolumn[index] = dcc.Link(
                    'Edit',
                    href='/actors/actors_profile?mode=edit&movieactorsid='+str(row["ID"])
                )
            dictionarydata = {'Action': linkcolumn}
            data_dict = df.to_dict()
            data_dict.update(dictionarydata)
            df = pd.DataFrame.from_dict(data_dict)
            df = df[['Actor', 'Movie Title', 'Action']]
        table = dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True, size='sm')
        if df.shape[0]:
            return [table]
        else:
            return ['No records to display']
        pass
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('actorprofile_actor', 'value'), 
        Output('actorprofile_movie', 'value'), 
    ],
    [
        Input('actorprofile_toload', 'modified_timestamp')
    ],
    [
        State('actorprofile_toload', 'data'), 
        State('url', 'search'),
    ]
)
def actorprofile_loadprofile(timestamp, toload, search):
    print('here', toload) 
    if toload:
        parsed = urlparse(search) 
        movieid = parse_qs(parsed.query)['movieactorsid'][0]
        sql = """ 
            SELECT actor_id, movie_id
            FROM movie_actors 
            WHERE movie_actors_id = %s
        """
        values = [movieid]
        col = ['actorid', 'movieid']
        df = db.querydatafromdatabase(sql, values, col)

        actorid = int(df['actorid'][0])
        movieid = int(df['movieid'][0])        
        return [actorid, movieid] 
    else: 
        raise PreventUpdate

@app.callback(
        Output("download-component", "data"),
        Input("downloadmovieactorstable", "n_clicks"),
        Input('url', 'pathname'),
        prevent_initial_call=True,
)

def func(n_clicks, pathname):
    if pathname == '/actors/actors_home':
        sql = """ SELECT actor_name, movie_title 
            FROM movie_actors m 
                INNER JOIN movies g ON m.movie_id = g.movie_id
                INNER JOIN actors a ON m.actor_id = a.actor_id 
            WHERE movie_actor_delete_ind = false
        """
        values = []
        cols = ['Actor', 'Movie Title']
        df = db.querydatafromdatabase(sql, values, cols)
        return dcc.send_data_frame(df.to_csv, "actor_movie_data.csv")
    else: 
        raise PreventUpdate