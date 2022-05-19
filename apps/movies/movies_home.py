from turtle import pensize
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
                                html.H4('Download Movie Data'),
                                dbc.Button(
                                    'CSV',
                                    id='downloadmoviestable',
                                    color="primary",
                                    n_clicks=0,
                                ),
                                dcc.Download(id="moviedownload-component"),
                            ]
                        ),
                                html.Hr(),
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
        sql = """ SELECT movie_id, movie_title, movie_produced_year, movie_description, genre_name, producer_name  
            FROM movies m 
                INNER JOIN genres g ON m.genre_id = g.genre_id
                INNER JOIN producers p ON m.producer_id =p.producer_id 
            WHERE movie_delete_ind = false
        """ 
        values = []
        if filter_title:
            sql += " AND movie_title ILIKE %s"
            values += [f"%{filter_title}%"]
        cols = ['ID', 'Movie Title', 'Year Produced', 'Movie Description', 'Genre', 'Producer']
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
            df = df[['Movie Title', 'Year Produced', 'Movie Description', 'Genre', 'Producer', 'Action']]
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
        Output('movieprofile_year', 'value'),
        Output('movieprofile_description', 'value'),        
        Output('movieprofile_genre', 'value'),
        Output('movieprofile_producer', 'value'),
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
            SELECT movie_title, movie_produced_year, movie_description, genre_id, producer_id
            FROM movies 
            WHERE movie_id = %s
        """
        values = [movieid]
        col = ['movietitle', 'yearproduced', 'moviedescription', 'genreid', 'producerid']
        df = db.querydatafromdatabase(sql, values, col)

        movietitle = df['movietitle'][0]
        yearproduced = df['yearproduced'][0]
        moviedescription = df['moviedescription'][0]
        genreid = int(df['genreid'][0])
        producerid = int(df['producerid'][0])
        return [movietitle, yearproduced, moviedescription, genreid, producerid] 
    else: 
        raise PreventUpdate

@app.callback(
        Output("moviedownload-component", "data"),
        Input("downloadmoviestable", "n_clicks"),
        Input('url', 'pathname'),
        prevent_initial_call=True,
)

def func(n_clicks, pathname):
    if pathname == '/movies/movies_home':
        sql = """ SELECT movie_title, movie_produced_year, movie_description, genre_name, producer_name  
        FROM movies m 
            INNER JOIN genres g ON m.genre_id = g.genre_id
            INNER JOIN producers p ON m.producer_id =p.producer_id 
        WHERE movie_delete_ind = false
        """ 
        values = []
        cols = ['Movie Title', 'Year Produced', 'Movie Description', 'Genre', 'Producer']
        df = db.querydatafromdatabase(sql, values, cols)
        return dcc.send_data_frame(df.to_csv, "movie_data.csv")
    else: 
        raise PreventUpdate