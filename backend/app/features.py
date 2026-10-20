import pandas as pd

FEATURE_COLUMNS = [
    "age", "diabetes_duration_years", "hba1c_percent",
    "medication_adherence_proxy", "hypertension",
    "current_glucose_mg_dl", "glucose_change_30m",
    "heart_rate_bpm", "hrv_ms", "sleep_hours",
    "steps_last_hour", "meal_carbs_g", "stress_level"
]

def make_features(patient: dict, sensor: dict, meal_carbs_g: float, stress_level: int) -> pd.DataFrame:
    glucose_change = float(sensor["glucose_mg_dl"] - sensor.get("glucose_30m_ago_mg_dl", sensor["glucose_mg_dl"]))
    row = {
        "age": patient["age"],
        "diabetes_duration_years": patient["diabetes_duration_years"],
        "hba1c_percent": patient["hba1c_percent"],
        "medication_adherence_proxy": patient["medication_adherence_proxy"],
        "hypertension": int(bool(patient["hypertension"])),
        "current_glucose_mg_dl": sensor["glucose_mg_dl"],
        "glucose_change_30m": glucose_change,
        "heart_rate_bpm": sensor["heart_rate_bpm"],
        "hrv_ms": sensor["hrv_ms"],
        "sleep_hours": sensor["sleep_hours"],
        "steps_last_hour": sensor["steps_last_hour"],
        "meal_carbs_g": meal_carbs_g,
        "stress_level": stress_level,
    }
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)
