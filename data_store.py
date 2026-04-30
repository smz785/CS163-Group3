import os
import functools
import pandas as pd
from google.cloud import storage
from io import BytesIO

#----- Converted the cvs file to parquet and uploaded it to GCS bucket -------------
# df = pd.read_csv("C:/Users/SyedZain/Downloads/criteo-uplift-v2.1.csv/criteo-uplift-v2.1.csv")
#
# df.to_parquet('C:/Users/SyedZain/Desktop/criteo-uplift-v2.1.parquet')

BUCKET_NAME = os.environ.get("BUCKET_NAME", 'group-3-bucket')
FILE_NAME = "criteo-uplift-v2.1.parquet"

@functools.lru_cache(maxsize=1)
def get_df():
    print(f" loading data from gcs://{BUCKET_NAME}/{FILE_NAME} ")
    client = storage.Client()
    blob_data = client.bucket(BUCKET_NAME).blob(FILE_NAME)
    data = blob_data.download_as_bytes()
    df = pd.read_parquet(BytesIO(data))
    return df