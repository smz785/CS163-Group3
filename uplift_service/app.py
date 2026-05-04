import joblib
import pandas as pd

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Uplift Inference Service")

# Load models (must exist first)
model_treated = joblib.load("models/model_treated.pkl")
model_control = joblib.load("models/model_control.pkl")
feature_cols = joblib.load("models/feature_cols.pkl")


class UserFeatures(BaseModel):
    f0: float
    f1: float
    f2: float
    f3: float
    f4: float
    f5: float
    f6: float
    f7: float
    f8: float
    f9: float
    f10: float
    f11: float


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/predict")
def predict(user: UserFeatures):
    user_df = pd.DataFrame([user.model_dump()])
    user_df = user_df[feature_cols]

    p_treated = model_treated.predict_proba(user_df)[0, 1]
    p_control = model_control.predict_proba(user_df)[0, 1]
    uplift = p_treated - p_control

    recommend_show_ad = bool(uplift > 0)

    if uplift > 0.001:
        segment = "Persuadable"
    elif uplift < -0.001 and (p_treated > 0.2 or p_control > 0.2):
        segment = "Sleeping Dog / Do Not Target"
    elif p_treated < 0.2 and p_control < 0.2:
        segment = "Lost Cause"
    else:
        segment = "Neutral / Low Impact"

    return {
        "p_treated": round(float(p_treated), 6),
        "p_control": round(float(p_control), 6),
        "uplift_score": round(float(uplift), 6),
        "recommend_show_ad": recommend_show_ad,
        "segment": segment
    }