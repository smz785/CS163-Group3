# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

from google.cloud import storage
import os
from io import StringIO
import functools


# BLOB is an acronym for "Binary Large Object". It's a data type that stores binary data, such as images, videos, and audio.
@functools.lru_cache(maxsize = 1)
def get_csv_from_gcs(bucket_name, source_blob_name, n_rows = 10000):
    """Downloads a blob from the bucket."""


    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)


    blob = bucket.blob(source_blob_name)
    with blob.open("r") as f:
        return pd.read_csv(f)


# Initialize the app
app = Dash()

# the underlying Flask server instance that Dash uses to run the application
# Many WSGI servers (e.g., Gunicorn, uWSGI) expect a server object.
# https://dash.plotly.com/deployment
server = app.server

# Cloud Storage demo
BUCKET_NAME = os.environ.get("BUCKET_NAME")
df = get_csv_from_gcs(BUCKET_NAME, 'criteo-uplift-v2.1.csv')
print(df)


# App layout
app.layout = html.Div([
     html.Div(children=''),
#     html.Hr(),
#     dcc.RadioItems(options=['pop', 'lifeExp', 'gdpPercap'], value='lifeExp', id='controls-and-radio-item'),
#     dash_table.DataTable(data=df.to_dict('records'), page_size=6),
#     dcc.Graph(figure={}, id='controls-and-graph'),
#     html.Hr(),
#     # this is a separate table for google cloud storage demo
     dash_table.DataTable(data=df.to_dict('records'), page_size=6)
 ])



# Run the app
if __name__ == '__main__':
    app.run(debug=True)
