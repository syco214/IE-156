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
                dcc.Store(id='countryprofile_toload', storage_type='memory', data=0),
            ]
        ),
        html.H2('Country Movie Details'), 
        html.Hr(),
        dbc.Alert(id='countryprofile_alert', is_open=False),
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
                                    "Add Movie Country",
                                    href='/country/country_profile?mode=add',
                                    color='primary',
                                    className="me-1"
                                )
                            ],
                            className="d-grid gap-2 mx-auto"
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Download Movie Country Data'),
                                dbc.Button(
                                    'CSV',
                                    id='downloadmoviecountrytable',
                                    color="primary",
                                    n_clicks=0,
                                    className="me-1"
                                ),
                                dcc.Download(id="countrydownload-component"),
                            ],
                            className="d-grid gap-2 mx-auto"
                        ),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4('Find Movies'),
                                html.Div(
                                    dbc.Form(
                                        dbc.FormGroup(
                                            [
                                                dbc.Label("Search Country", width=1),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type='text',
                                                        id='countryhome_titlefilter',
                                                        placeholder='Country'
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
                                    id = 'countryhome_countrylist'
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
        Output('countryhome_countrylist', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('countryhome_titlefilter', 'value')
    ]
)
def moviehome_loadmovielist(pathname, filter_title):
    if pathname == '/country/country_home':
        sql = """ SELECT   movie_countries_id, country_name, movie_title
            FROM movie_countries m 
                INNER JOIN movies g ON m.movie_id = g.movie_id
                INNER JOIN countries c ON m.country_id = c.country_id 
            WHERE country_delete_ind = false
        """ 
        values = []
        if filter_title:
            sql += " AND country_name ILIKE %s"
            values += [f"%{filter_title}%"]
        cols = ['ID', 'Country', 'Movie Title']
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape[0]:
            linkcolumn = {}
            for index, row in df.iterrows():
                linkcolumn[index] = dcc.Link(
                    'Edit',
                    href='/country/country_profile?mode=edit&moviecountriesid='+str(row["ID"])
                )
            dictionarydata = {'Action': linkcolumn}
            data_dict = df.to_dict()
            data_dict.update(dictionarydata)
            df = pd.DataFrame.from_dict(data_dict)
            df = df[['Country', 'Movie Title', 'Action']]
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
        Output('countryprofile_country', 'value'), 
        Output('countryprofile_movie', 'value'), 
    ],
    [
        Input('countryprofile_toload', 'modified_timestamp')
    ],
    [
        State('countryprofile_toload', 'data'), 
        State('url', 'search'),
    ]
)
def countryprofile_loadprofile(timestamp, toload, search):
    print('here', toload) 
    if toload:
        parsed = urlparse(search) 
        movieid = parse_qs(parsed.query)['moviecountriesid'][0]
        sql = """ 
            SELECT country_id, movie_id
            FROM movie_countries 
            WHERE movie_countries_id = %s
        """
        values = [movieid]
        col = ['countryid', 'movieid']
        df = db.querydatafromdatabase(sql, values, col)

        countryid = int(df['countryid'][0])
        movieid = int(df['movieid'][0])    
        return [countryid, movieid] 
    else: 
        raise PreventUpdate

@app.callback(
        Output("countrydownload-component", "data"),
        Input("downloadmoviecountrytable", "n_clicks"),
        Input('url', 'pathname'),
        prevent_initial_call=True,
)

def func(n_clicks, pathname):
    if pathname == '/country/country_home':
        sql = """ SELECT country_name, movie_title
            FROM movie_countries m 
                INNER JOIN movies g ON m.movie_id = g.movie_id
                INNER JOIN countries c ON m.country_id = c.country_id 
            WHERE country_delete_ind = false
        """ 
        values = []
        cols = ['Country', 'Movie Title']
        df = db.querydatafromdatabase(sql, values, cols)
        return dcc.send_data_frame(df.to_csv, "country_movie_data.csv")
    else: 
        raise PreventUpdate