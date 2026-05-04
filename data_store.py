import os
import functools
from io import BytesIO

import pandas as pd
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError


BUCKET_NAME = os.environ.get("BUCKET_NAME", "group-3-bucket")
FILE_NAME = "criteo-uplift-v2.1.parquet"


def _load_local_precomputed(filename):
    path = os.path.join("precomputed", os.path.basename(filename))
    return path


@functools.lru_cache(maxsize=1)
def get_df():
    try:
        print(f"loading data from gcs://{BUCKET_NAME}/{FILE_NAME}")
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)
        data = blob.download_as_bytes()
        return pd.read_parquet(BytesIO(data))

    except Exception as e:
        print("GCS dataset load failed locally:", e)
        print("Returning empty DataFrame for local development.")
        return pd.DataFrame()


@functools.lru_cache(maxsize=1)
def get_precomputed():
    try:
        print(f"loading precomputed results from gcs://{BUCKET_NAME}/precomputed/")
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        def load_series(filename):
            blob = bucket.blob(filename)
            data = blob.download_as_bytes()
            return pd.read_csv(BytesIO(data), index_col=0).squeeze()

        def load_df(filename):
            blob = bucket.blob(filename)
            data = blob.download_as_bytes()
            return pd.read_csv(BytesIO(data))

        return {
            "visit_rate": load_series("precomputed/visit_rate.csv"),
            "conversion_rate": load_series("precomputed/conversion_rate.csv"),
            "conv_given_visit": load_series("precomputed/conv_given_visit.csv"),
            "decile_df": load_df("precomputed/decile_uplift.csv"),
            "qini_tbl": load_df("precomputed/qini_table.csv"),
            "policy_df": load_df("precomputed/policy_table.csv"),
        }

    except Exception as e:
        print("GCS precomputed load failed. Falling back to local precomputed files.")
        print(e)

        def load_local_series(filename):
            path = _load_local_precomputed(filename)
            if os.path.exists(path):
                return pd.read_csv(path, index_col=0).squeeze()
            return pd.Series(dtype=float)

        def load_local_df(filename):
            path = _load_local_precomputed(filename)
            if os.path.exists(path):
                return pd.read_csv(path)
            return pd.DataFrame()

        return {
            "visit_rate": load_local_series("visit_rate.csv"),
            "conversion_rate": load_local_series("conversion_rate.csv"),
            "conv_given_visit": load_local_series("conv_given_visit.csv"),
            "decile_df": load_local_df("decile_uplift.csv"),
            "qini_tbl": load_local_df("qini_table.csv"),
            "policy_df": load_local_df("policy_table.csv"),
        }