import os
import functools
from io import BytesIO

import pandas as pd
from google.cloud import storage


BUCKET_NAME = os.environ.get("BUCKET_NAME", "group-3-bucket")
FILE_NAME = "criteo-uplift-v2.1.parquet"


def _local_precomputed_path(filename: str) -> str:
    return os.path.join(
        os.path.dirname(__file__),
        "precomputed",
        os.path.basename(filename)
    )


def _read_local_csv(filename: str) -> pd.DataFrame:
    path = _local_precomputed_path(filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


def _read_local_series(filename: str) -> pd.Series:
    df = _read_local_csv(filename)

    if df.empty:
        return pd.Series(dtype=float)

    # Expected format:
    # column 0 = treatment/index
    # column 1 = metric value
    if df.shape[1] >= 2:
        return pd.Series(df.iloc[:, 1].values, index=df.iloc[:, 0].values)

    return df.squeeze()


@functools.lru_cache(maxsize=1)
def get_df():
    try:
        print(f"Loading dataset from gs://{BUCKET_NAME}/{FILE_NAME}")
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)
        data = blob.download_as_bytes()
        return pd.read_parquet(BytesIO(data))

    except Exception as e:
        raise RuntimeError(
            f"Failed to load full dataset from gs://{BUCKET_NAME}/{FILE_NAME}. "
            "Check bucket name, object path, Cloud Run service account permissions, "
            "or local Google credentials."
        ) from e

@functools.lru_cache(maxsize=1)
def get_precomputed():
    try:
        print(f"Loading precomputed files from gs://{BUCKET_NAME}/precomputed/")
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        def load_series(filename):
            blob = bucket.blob(f"precomputed/{filename}")
            data = blob.download_as_bytes()
            return pd.read_csv(BytesIO(data), index_col=0).squeeze()

        def load_df(filename):
            blob = bucket.blob(f"precomputed/{filename}")
            data = blob.download_as_bytes()
            return pd.read_csv(BytesIO(data))

        return {
            "visit_rate": load_series("visit_rate.csv"),
            "conversion_rate": load_series("conversion_rate.csv"),
            "conv_given_visit": load_series("conv_given_visit.csv"),
            "decile_df": load_df("decile_table.csv"),
            "qini_tbl": load_df("qini_table.csv"),
            "policy_df": load_df("policy_table.csv"),
            "pca_df": load_df("pca_df.csv"),
            "corr": load_df("corr.csv"),
        }

    except Exception as e:
        print("GCS precomputed load failed. Falling back to local precomputed files.")
        print(e)

        def load_local_series(filename):
            path = os.path.join("precomputed", filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing local fallback file: {path}")
            return pd.read_csv(path, index_col=0).squeeze()

        def load_local_df(filename):
            path = os.path.join("precomputed", filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing local fallback file: {path}")
            return pd.read_csv(path)

        return {
            "visit_rate": load_local_series("visit_rate.csv"),
            "conversion_rate": load_local_series("conversion_rate.csv"),
            "conv_given_visit": load_local_series("conv_given_visit.csv"),
            "decile_df": load_local_df("decile_table.csv"),
            "qini_tbl": load_local_df("qini_table.csv"),
            "policy_df": load_local_df("policy_table.csv"),
            "pca_df": load_local_df("pca_df.csv"),
            "corr": load_local_df("corr.csv"),
        }