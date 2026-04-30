import os
import functools
import pandas as pd
from google.cloud import storage
from io import StringIO

BUCKET_NAME = os.environ.get("BUCKET_NAME", 'group-3-bucket')
FILE_NAME = "criteo-uplift-v2.1.csv"

@functools.lru_cache(maxsize=1)
def get_df():
    print(f" loading data from gcs://{BUCKET_NAME}/{FILE_NAME} ")
    client = storage.Client()
    blob_data = client.bucket(BUCKET_NAME).blob(FILE_NAME)
    data = blob_data.download_as_text()
    df = pd.read_csv(StringIO(data))
    return df