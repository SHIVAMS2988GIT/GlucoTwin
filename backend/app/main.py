from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import MODEL_FILE
from .schemas import PredictRequest, PredictResponse
from .service import load_data, patient_record, predict, DISCLAIMER

app = FastAPI(
    title="GlucoTwin API",
    description="Synthetic digital-twin proof of concept for two-hour glucose-spike risk.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "GlucoTwin API"}

@app.get("/api/patients")
def list_patients():
    try:
        patients, sensors = load_data()
        latest = sensors.sort_values("timestamp").groupby("patient_id").tail(1).set_index("patient_id")
        result = []
        for _, p in patients.iterrows():
            s = latest.loc[p.patient_id]
            result.append({
                "patient_id": p.patient_id,
                "age": int(p.age),
                "sex": p.sex,
                "hba1c_percent": round(float(p.hba1c_percent), 1),
                "latest_glucose_mg_dl": round(float(s.glucose_mg_dl), 1),
            })
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str):
    try:
        patient, sensor, _ = patient_record(patient_id)
        return {
            "patient_id": patient_id,
            "age": int(patient["age"]),
            "sex": patient["sex"],
            "diabetes_duration_years": round(float(patient["diabetes_duration_years"]), 1),
            "hba1c_percent": round(float(patient["hba1c_percent"]), 1),
            "medication_adherence_proxy": round(float(patient["medication_adherence_proxy"]), 2),
            "hypertension": bool(patient["hypertension"]),
            "latest_glucose_mg_dl": round(float(sensor["glucose_mg_dl"]), 1),
            "latest_heart_rate_bpm": round(float(sensor["heart_rate_bpm"]), 1),
            "latest_steps": int(sensor["steps_last_hour"]),
            "latest_sleep_hours": round(float(sensor["sleep_hours"]), 1),
        }
    except KeyError:
        raise HTTPException(status_code=404, detail="Synthetic patient not found")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/api/patients/{patient_id}/timeline")
def get_timeline(patient_id: str):
    try:
        _, _, sensors = patient_record(patient_id)
        rows = sensors[sensors.patient_id == patient_id].sort_values("timestamp").tail(48)
        return [{
            "timestamp": r.timestamp.isoformat(),
            "glucose_mg_dl": round(float(r.glucose_mg_dl), 1),
            "heart_rate_bpm": round(float(r.heart_rate_bpm), 1),
            "steps_last_hour": int(r.steps_last_hour),
            "sleep_hours": round(float(r.sleep_hours), 1),
        } for _, r in rows.iterrows()]
    except KeyError:
        raise HTTPException(status_code=404, detail="Synthetic patient not found")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/api/predict", response_model=PredictResponse)
def predict_endpoint(request: PredictRequest):
    try:
        return predict(request.patient_id, request.meal_carbs_g, request.stress_level)
    except KeyError:
        raise HTTPException(status_code=404, detail="Synthetic patient not found")
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/api/model-info")
def model_info():
    return {
        "model": "RandomForestClassifier",
        "target": "Synthetic glucose rise event within 2 hours",
        "feature_groups": ["historical EHR", "wearable-style time series", "scenario inputs"],
        "artifact_available": MODEL_FILE.exists(),
        "data": "synthetic only",
        "clinical_validation": "not performed",
        "disclaimer": DISCLAIMER,
    }
