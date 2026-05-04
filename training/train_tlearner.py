import os
from io import BytesIO
import joblib
import pandas as pd

from google.cloud import storage
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import roc_auc_score

# Config
BUCKET_NAME = "group-3-bucket"
FILE_NAME = "criteo-uplift-v2.1.parquet"

MODEL_DIR = "uplift_service/models"
os.makedirs(MODEL_DIR, exist_ok=True)


# Load data from Google Cloud Storage
print("Loading data from GCS...")

client = storage.Client(project="cs163-group-3")
bucket = client.bucket(BUCKET_NAME)
blob = bucket.blob(FILE_NAME)

data = blob.download_as_bytes()
df = pd.read_parquet(BytesIO(data))

print("Data loaded:", df.shape)


# Prepare features and target
feature_cols = [c for c in df.columns if c.startswith("f")]

X = df[feature_cols]
T = df["treatment"].astype(int)
Y = df["conversion"].astype(int)

print("Feature columns:", feature_cols)
print("Treatment distribution:")
print(T.value_counts(normalize=True))


# Train / test split
print("Splitting data...")

X_train, X_test, T_train, T_test, y_train, y_test = train_test_split(
    X,
    T,
    Y,
    test_size=0.2,
    random_state=42,
    stratify=Y
)


# Split treated and control users
X_train_treated = X_train[T_train == 1]
y_train_treated = y_train[T_train == 1]

X_train_control = X_train[T_train == 0]
y_train_control = y_train[T_train == 0]

print("Treated training rows:", len(X_train_treated))
print("Control training rows:", len(X_train_control))


# Handle class imbalance
w_treated = compute_sample_weight(
    class_weight="balanced",
    y=y_train_treated
)

w_control = compute_sample_weight(
    class_weight="balanced",
    y=y_train_control
)


# Train treated model
print("Training treated model...")

model_treated = HistGradientBoostingClassifier(
    max_iter=200,
    learning_rate=0.03,
    max_leaf_nodes=15,
    min_samples_leaf=1000,
    l2_regularization=1.0,
    early_stopping=True,
    random_state=42
)

model_treated.fit(
    X_train_treated,
    y_train_treated,
    sample_weight=w_treated
)


# Train control model
print("Training control model...")

model_control = HistGradientBoostingClassifier(
    max_iter=200,
    learning_rate=0.03,
    max_leaf_nodes=15,
    min_samples_leaf=1000,
    l2_regularization=1.0,
    early_stopping=True,
    random_state=42
)

model_control.fit(
    X_train_control,
    y_train_control,
    sample_weight=w_control
)


# Evaluate model AUC
print("Evaluating models...")

p_treated = model_treated.predict_proba(X_test)[:, 1]
p_control = model_control.predict_proba(X_test)[:, 1]

auc_treated = roc_auc_score(
    y_test[T_test == 1],
    p_treated[T_test == 1]
)

auc_control = roc_auc_score(
    y_test[T_test == 0],
    p_control[T_test == 0]
)

print(f"Treated model AUC: {auc_treated:.4f}")
print(f"Control model AUC: {auc_control:.4f}")


# Save model artifacts
print("Saving models...")

joblib.dump(model_treated, f"{MODEL_DIR}/model_treated.pkl")
joblib.dump(model_control, f"{MODEL_DIR}/model_control.pkl")
joblib.dump(feature_cols, f"{MODEL_DIR}/feature_cols.pkl")

print("Done. Models saved to:", MODEL_DIR)