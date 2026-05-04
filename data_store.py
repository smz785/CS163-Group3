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
def get_df(sample_rows: int | None = None) -> pd.DataFrame:
    """
    Heavy raw-data loader.

    Do not call this during process startup.
    In production, prefer get_precomputed().
    """

    try:
        print(f"loading data from gcs://{BUCKET_NAME}/{FILE_NAME}", flush=True)

        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)

        columns = [
            "treatment",
            "visit",
            "conversion",
            "exposure",
            "f0",
            "f1",
            "f2",
            "f3",
            "f4",
            "f5",
            "f6",
            "f7",
            "f8",
            "f9",
            "f10",
            "f11",
        ]

        with blob.open("rb") as f:
            df = pd.read_parquet(f, columns=columns)

        if sample_rows is not None and len(df) > sample_rows:
            return df.sample(sample_rows, random_state=42)

        return df

    except Exception as e:
        print(f"GCS dataset load failed: {e}", flush=True)
        return pd.DataFrame()


@functools.lru_cache(maxsize=1)
def get_precomputed() -> dict:
    """
    Lightweight production loader.

    These CSV files are small and safe to cache.
    Falls back to local ./precomputed files when GCS is unavailable.
    """

    try:
        print(
            f"loading precomputed results from gcs://{BUCKET_NAME}/precomputed/",
            flush=True
        )

        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        def load_df(filename: str) -> pd.DataFrame:
            blob = bucket.blob(f"precomputed/{filename}")
            data = blob.download_as_bytes()
            return pd.read_csv(BytesIO(data))

        def load_series(filename: str) -> pd.Series:
            df = load_df(filename)

            if df.empty:
                return pd.Series(dtype=float)

            return pd.Series(df.iloc[:, 1].values, index=df.iloc[:, 0].values)

        return {
            "visit_rate": load_series("visit_rate.csv"),
            "conversion_rate": load_series("conversion_rate.csv"),
            "conv_given_visit": load_series("conv_given_visit.csv"),
            "corr": load_df("corr.csv"),
            "pca_sample": load_df("pca_sample.csv"),
            "decile_df": load_df("decile_table.csv"),
            "qini_tbl": load_df("qini_table.csv"),
            "policy_df": load_df("policy_table.csv"),
        }

    except Exception as e:
        print(
            "GCS precomputed load failed. Falling back to local precomputed files.",
            flush=True
        )
        print(e, flush=True)

        return {
            "visit_rate": _read_local_series("visit_rate.csv"),
            "conversion_rate": _read_local_series("conversion_rate.csv"),
            "conv_given_visit": _read_local_series("conv_given_visit.csv"),
            "corr": _read_local_csv("corr.csv"),
            "pca_sample": _read_local_csv("pca_sample.csv"),
            "decile_df": _read_local_csv("decile_table.csv"),
            "qini_tbl": _read_local_csv("qini_table.csv"),
            "policy_df": _read_local_csv("policy_table.csv"),
        }