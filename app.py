# Import packages
import dash
# Optional / future imports (uncomment when used):
from dash import Dash, html, dcc, dash_table, dcc, callback, Output, Input
# import pandas as pd
# import plotly.express as px
# from google.cloud import storage
# import os
# from io import StringIO
# import functools

app = Dash(__name__, use_pages=True)

# Minimal Dash layout so the Dash endpoints are available.
app.layout = html.Div([

    html.Header([
        html.Div("CS 163 - Group 3", className = "course-tag"),
        html.H1("Criteo Uplift Data Modeling and Analysis"),
        html.P("Predicting Treatment Effect on User Conversions Using Machine Learning")
    ]),

    html.Nav([
        dcc.Link("Overview", href='/'),
        dcc.Link("Dataset", href='/dataset'),
        dcc.Link("Methods", href="/methods"),
        dcc.Link("Analytics", href="/analytics")
    ]),

    html.Footer("CS 163 &mdash; Group 3 &bull; Spring 2026 &bull; Built with HTML &amp; CSS"),
    dash.page_container
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
