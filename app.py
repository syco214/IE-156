import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import logging

app = dash.Dash(__name__, external_stylesheets=["assets/bootstrap.css"])

server = app.server

app.config.suppress_callback_exceptions = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.title = 'IE 156 Case'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

