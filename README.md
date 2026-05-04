# Criteo Uplift Data Modeling and Analysis
### CS 163 — Group 3 · Spring 2026

A multi-page interactive web application for causal analysis of the [Criteo Uplift v2.1 dataset](https://ailab.criteo.com/criteo-uplift-modeling-dataset/). The app evaluates the incremental effectiveness of online advertising using uplift modeling, with a focus on heterogeneous treatment effects and targeting efficiency.

**Live App →** `https://cs163-group-3.wl.r.appspot.com`  
**Inference API →** `https://uplift-api-929926879239.us-west2.run.app/predict`
---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Data Pipeline](#data-pipeline)
- [App Pages](#app-pages)
- [Deployment](#deployment)
- [Inference Service](#inference-service)
- [Team](#team)

---

## Overview

Traditional predictive models identify users likely to convert. This project goes further — it estimates **incremental impact**: how much does advertising *change* user behavior compared to a counterfactual where they saw no ad?

Three core hypotheses are investigated:

1. Whether advertising primarily drives **engagement** (visits) or **purchasing** (conversions)
2. Whether **treatment effects vary** across user segments (heterogeneous effects)
3. Whether **uplift-based targeting** outperforms a treat-all strategy

Key findings from the analysis:
- Advertising increases visit rates from **3.82% → 4.85%** and conversion rates from **0.19% → 0.31%**
- Treatment effects are **highly concentrated** — the top decile has ~5x the average treatment effect
- Targeting only the **top 10% of users** by predicted uplift captures ~50% of total incremental conversions

---

## Project Structure

```
CS163test/
├── app.py                  # Dash app entry point, shared layout, nav
├── data_store.py           # GCS data loaders with lru_cache
├── Dockerfile              # Container definition (web app)
├── app.yaml                # Google App Engine configuration
├── requirements.txt        # Python dependencies
├── .dockerignore           # Files excluded from Docker image
├── .gcloudignore           # Files excluded from App Engine deploy
│
├── pages/
│   ├── home.py             # Project overview and motivation
│   ├── dataset.py          # Dataset description and schema
│   ├── methods.py          # Methodology: T-learner, Qini, policy eval
│   ├── EDA.py              # Exploratory data analysis with live charts
│   └── preliminary_results.py  # ML results: decile uplift, Qini curve, policy table
│
├── uplift_service/         # ML inference API (NEW)
│   ├── app.py              # FastAPI inference service (/predict endpoint)
│   ├── Dockerfile          # Container for inference API (Cloud Run)
│   ├── requirements.txt    # API dependencies
│   └── models/             # Saved trained model artifacts
│       ├── model_treated.pkl
│       ├── model_control.pkl
│       └── feature_cols.pkl
│
└── assets/
    └── style.css           # Global styles
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend / App** | [Plotly Dash](https://dash.plotly.com/) |
| **Charting** | Plotly Express, Plotly Graph Objects |
| **Data** | Pandas, PyArrow (Parquet) |
| **ML** | scikit-learn — `HistGradientBoostingClassifier` (T-Learner) |
| **Dimensionality Reduction** | scikit-learn PCA |
| **Cloud Storage** | Google Cloud Storage |
| **Serving** | Gunicorn + Flask (via Dash) |
| **Deployment** | Google App Engine (Standard, Python 3.10) |
| **Containerization** | Docker |
| **Inference API** | FastAPI |
| **Cloud Inference** | Google Cloud Run |
---

## Getting Started

### Prerequisites

- Python 3.10+
- A Google Cloud project with a GCS bucket
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`) installed and authenticated

### 1. Clone the repository

```bash
git clone https://github.com/your-org/CS163test.git
cd CS163test
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Google Cloud authentication

```bash
gcloud auth application-default login
```

This allows `google-cloud-storage` to authenticate using your personal credentials during local development. On App Engine, the default service account is used automatically — no key file needed.

### 5. Set environment variables

```bash
# Windows
set BUCKET_NAME=your-bucket-name

# macOS / Linux
export BUCKET_NAME=your-bucket-name
```

Or create a `.env` file (do not commit this):
```
BUCKET_NAME=your-bucket-name
```

### 6. Run the app locally

```bash
python app.py
```

Visit `http://127.0.0.1:8050` in your browser.

---

## Data Pipeline

The dataset is the [Criteo Uplift v2.1](https://ailab.criteo.com/criteo-uplift-modeling-dataset/) CSV (~3.5 GB, ~14M rows). It is stored in Google Cloud Storage and loaded at app startup.

### Converting CSV → Parquet (one-time setup)

Parquet loads 5–10x faster than CSV and is ~300–500 MB vs 3.5 GB. Run this once locally:

```python
import pandas as pd
df = pd.read_csv(r"path\to\criteo-uplift-v2.1.csv")
df.to_parquet(r"path\to\criteo-uplift-v2.1.parquet")
```

Then upload to your GCS bucket:
- Go to **Google Cloud Console → Cloud Storage → your bucket**
- Upload `criteo-uplift-v2.1.parquet`
- Upload all files under `precomputed/` to a `precomputed/` prefix in the bucket

### GCS Bucket Configuration

| Setting | Value |
|---|---|
| **Access control** | Uniform |
| **IAM principal** | `your-project-id@appspot.gserviceaccount.com` |
| **IAM role** | `Storage Object Viewer` |
| **Region** | Same region as App Engine for lowest latency |

### How data is loaded (`data_store.py`)

```
App startup
    │
    ├── get_df()           → downloads criteo-uplift-v2.1.parquet from GCS
    │                         cached in RAM via lru_cache (runs once per instance)
    │
    └── get_precomputed()  → downloads 6 small CSVs from GCS precomputed/ folder
                              cached in RAM via lru_cache (runs once per instance)
```

`EDA.py` uses `get_df()` and computes aggregations live. `preliminary_results.py` uses `get_precomputed()` for ML outputs that cannot be recomputed at runtime.

### Precomputed files (generated offline, stored in GCS)

| File | Description |
|---|---|
| `precomputed/visit_rate.csv` | Mean visit rate by treatment group |
| `precomputed/conversion_rate.csv` | Mean conversion rate by treatment group |
| `precomputed/conv_given_visit.csv` | Conversion rate conditioned on visit |
| `precomputed/decile_uplift.csv` | Realized uplift per predicted-uplift decile (T-Learner) |
| `precomputed/qini_table.csv` | Cumulative incremental conversions vs % targeted |
| `precomputed/policy_table.csv` | Treat-all vs uplift targeting policy comparison |

---

## App Pages

| Page | Path | Description |
|---|---|---|
| Overview | `/` | Project motivation and summary of findings |
| Dataset | `/dataset` | Schema, size, class imbalance, variable definitions |
| Methods | `/methods` | T-Learner methodology, Qini coefficient, policy evaluation |
| EDA | `/analytics` | EDA: funnel analysis, lift, correlation heatmap, PCA |
| Findings | `/preliminary_results` | ML results across 3 hypotheses with Qini curve and policy tables |

---

## Deployment

### Google App Engine

```bash
gcloud app deploy app.yaml
```

Key settings in `app.yaml`:

```yaml
runtime: python310
instance_class: F4_1G    # 3.75 GB RAM — required for 14M row dataset
max_instances: 1          # Single instance keeps one cached copy of the data
entrypoint: gunicorn -b :$PORT --timeout 300 app:server
```

`--timeout 300` is critical — the first request after a cold start triggers the GCS download (~10–30s for Parquet) and Gunicorn's default 30s timeout would kill it.

### Docker (local or other platforms)

```bash
# Build
docker build -t criteo-uplift-app .

# Run
docker run -p 8080:8080 \
  -e BUCKET_NAME=your-bucket-name \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/key.json \
  -v /path/to/key.json:/app/key.json \
  criteo-uplift-app
```

Visit `http://localhost:8080`.

---

## Inference Service

This project includes a Dockerized ML inference service deployed on Google Cloud Run. The service exposes the trained uplift model through a REST API, allowing new user feature inputs to receive real-time uplift predictions.

### Live Endpoint

```text
POST https://uplift-api-929926879239.us-west2.run.app/predict

## Example Request

```bash
curl -X POST "https://uplift-api-929926879239.us-west2.run.app/predict" \
-H "Content-Type: application/json" \
-d '{
  "f0": 25.516106,
  "f1": 10.059654,
  "f2": 9.039079,
  "f3": 4.679882,
  "f4": 10.280525,
  "f5": 4.115453,
  "f6": -13.293861,
  "f7": 4.833815,
  "f8": 3.88265,
  "f9": 13.190056,
  "f10": 5.300375,
  "f11": -0.168679
}'

## Example Response
```json
{
  "p_treated": 0.081558,
  "p_control": 0.087148,
  "uplift_score": -0.00559,
  "recommend_show_ad": false,
  "segment": "Lost Cause"
}
```
---

## Team

**CS 163 — Group 3 · Spring 2026**

| Name | GitHub |

|------|--------|

| Syed Zain | [@syedzain]((https://github.com/smz785)) |

| Ayman | [@ayrabia](https://github.com/ayrabia) |

| Thang | [@thang-cao13](https://github.com/thang-cao13) |

---
