import os
import functools
from io import BytesIO
import pickle
import pandas as pd
from google.cloud import storage

BUCKET_NAME = os.environ.get("BUCKET_NAME", 'group-3-bucket')

@functools.lru_cache(maxsize=1)
def get_model():
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)

    def load_models(filename):
        blob = bucket.blob(filename)
        model_data = blob.download_as_bytes()
        return pickle.load(BytesIO(model_data))

    # model_treated = load_models(#filename)
    # model_control = load_models(#filename)

    # return model_treated, model_control