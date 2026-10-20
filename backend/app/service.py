import joblib
import pandas as pd
from .config import MODEL_FILE, PATIENTS_FILE, SENSORS_FILE
from .features import make_features, FEATURE_COLUMNS

DISCLAIMER = (
    "Synthetic educational prototype only. This score is not a diagnosis or medical advice "
    "and must not guide treatment. Clinical validation is required before real-world use."
)

def load_data():
    if not PATIENTS_FILE.exists() or not SENSORS_FILE.exists():
        raise RuntimeError("Synthetic data missing. Run: python scripts/generate_data.py")
    patients = pd.read_csv(PATIENTS_FILE)
    sensors = pd.read_csv(SENSORS_FILE, parse_dates=["timestamp"])
    return patients, sensors

def latest_sensor(sensors: pd.DataFrame, patient_id: str) -> dict:
    rows = sensors[sensors.patient_id == patient_id].sort_values("timestamp")
    if rows.empty:
        raise KeyError(patient_id)
    latest = rows.iloc[-1].to_dict()
    prior = rows[rows.timestamp <= rows.iloc[-1]["timestamp"] - pd.Timedelta(minutes=30)]
    latest["glucose_30m_ago_mg_dl"] = float(prior.iloc[-1].glucose_mg_dl) if not prior.empty else float(latest["glucose_mg_dl"])
    return latest

def get_model():
    if not MODEL_FILE.exists():
        raise RuntimeError("Model missing. Run: python scripts/train_model.py")
    return joblib.load(MODEL_FILE)

def patient_record(patient_id: str):
    patients, sensors = load_data()
    matches = patients[patients.patient_id == patient_id]
    if matches.empty:
        raise KeyError(patient_id)
    patient = matches.iloc[0].to_dict()
    sensor = latest_sensor(sensors, patient_id)
    patient["hypertension"] = bool(int(patient["hypertension"]))
    return patient, sensor, sensors

def predict(patient_id: str, meal_carbs_g: float, stress_level: int):
    patient, sensor, _ = patient_record(patient_id)
    model = get_model()
    X = make_features(patient, sensor, meal_carbs_g, stress_level)
    probability = float(model.predict_proba(X[FEATURE_COLUMNS])[0][1])
    category = "Elevated" if probability >= 0.65 else ("Moderate" if probability >= 0.35 else "Lower")
    factors = {
        "current_glucose_mg_dl": round(float(sensor["glucose_mg_dl"]), 1),
        "glucose_change_30m": round(float(sensor["glucose_mg_dl"] - sensor["glucose_30m_ago_mg_dl"]), 1),
        "sleep_hours": round(float(sensor["sleep_hours"]), 1),
        "steps_last_hour": int(sensor["steps_last_hour"]),
        "heart_rate_bpm": round(float(sensor["heart_rate_bpm"]), 1),
        "hrv_ms": round(float(sensor["hrv_ms"]), 1),
        "hba1c_percent": round(float(patient["hba1c_percent"]), 1),
        "meal_carbs_g": float(meal_carbs_g),
    }
    return {
        "patient_id": patient_id,
        "risk_probability": round(probability, 4),
        "risk_category": category,
        "horizon_hours": 2,
        "prediction_label": "Synthetic glucose-spike event risk",
        "factors": factors,
        "disclaimer": DISCLAIMER,
    }
