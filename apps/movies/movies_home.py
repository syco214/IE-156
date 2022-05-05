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
                dcc.Store(id='movieprofile_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2('Movie Details'), 
        html.Hr(),
        dbc.Alert(id='movieprofile_alert', is_open=False),
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
                                    "Add Movie",
                                    href='/movies/movies_profile?mode=add',
                                    color='primary'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Movies'),
                                html.Div(
                                    dbc.Form(
                                        dbc.FormGroup(
                                            [
                                                dbc.Label("Search Title", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='moviehome_titlefilter',
                                                        placeholder='Movie Title'
                                                    ),
                                                    width=5
                                                )
                                            ],
                                            row=True
                                        )
                                    )
                                ),
                                html.Div(
                                    "Table with movies will go here",
                                    id = 'moviehome_movielist'
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
        Output('moviehome_movielist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('moviehome_titlefilter', 'value')
    ]
)
def moviehome_loadmovielist(pathname, filter_title):
    if pathname == '/movies/movies_home':
        sql = """ SELECT movie_id, movie_name, genre_name 
            FROM movies m 
                INNER JOIN genres g ON m.genre_id = g.genre_id 
            WHERE movie_delete_ind = false
        """
        values = []
        if filter_title:
            sql += " AND movie_name ILIKE %s"
            values += [f"%{filter_title}%"]
        cols = ['ID', 'Movie Title', 'Genre']
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape[0]:
            linkcolumn = {}
            for index, row in df.iterrows():
                linkcolumn[index] = dcc.Link(
                    'Edit',
                    href='/movies/movies_profile?mode=edit&movieid='+str(row["ID"])
                )
            dictionarydata = {'Action': linkcolumn}
            data_dict = df.to_dict()
            data_dict.update(dictionarydata)
            df = pd.DataFrame.from_dict(data_dict)
            df = df[['Movie Title', 'Genre', 'Action']]
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
        Output('movieprofile_title', 'value'), 
        Output('movieprofile_genre', 'value'), 
        Output('movieprofile_releasedate', 'date'),
    ],
    [
        Input('movieprofile_toload', 'modified_timestamp')
    ],
    [
        State('movieprofile_toload', 'data'), 
        State('url', 'search'),
    ]
)
def movieprofile_loadprofile(timestamp, toload, search):
    print('here', toload) 
    if toload:
        parsed = urlparse(search) 
        movieid = parse_qs(parsed.query)['movieid'][0]
        sql = """ 
            SELECT movie_name, genre_id, movie_release_date 
            FROM movies 
            WHERE movie_id = %s
        """
        values = [movieid]
        col = ['moviename', 'genreid', 'releasedate']
        df = db.querydatafromdatabase(sql, values, col)

        moviename = df['moviename'][0]
        genreid = int(df['genreid'][0])
        releasedate = df['releasedate'][0]
        return [moviename, genreid, releasedate] 
    else: 
        raise PreventUpdate