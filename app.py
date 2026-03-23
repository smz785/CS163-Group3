# Import packages
from dash import Dash, html

# Optional / future imports (uncomment when used):
# from dash import dash_table, dcc, callback, Output, Input
# import pandas as pd
# import plotly.express as px
# from google.cloud import storage
# import os
# from io import StringIO
# import functools

from flask import send_from_directory


# Initialize the app
# Run Dash under the '/dash/' path so the Flask root ('/') can serve the static HTML page.
app = Dash(__name__, routes_pathname_prefix='/dash/', requests_pathname_prefix='/dash/')

# the underlying Flask server instance that Dash uses to run the application
# Many WSGI servers (e.g., Gunicorn, uWSGI) expect a server object.
# https://dash.plotly.com/deployment
server = app.server


# Minimal Dash layout so the Dash endpoints are available.
app.layout = html.Div([
    html.H1("Dash app running (mounted at /dash/ )"),
    html.P("Click below to open the static CS163 webpage served at the root URL."),
    html.A("Open CS163_Webpage.html (root)", href='/', target='_self'),
    html.Div(style={'height': '1rem'}),
    html.P("Or visit the Dash app directly at /dash/")
])


# Serve the standalone HTML file from the 'static' folder at the root URL.
@server.route('/')
def index():
    return send_from_directory('static', 'CS163_Webpage.html')


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
