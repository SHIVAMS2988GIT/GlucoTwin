from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    patient_id: str = Field(..., examples=["P-1001"])
    meal_carbs_g: float = Field(default=45, ge=0, le=250)
    stress_level: int = Field(default=3, ge=1, le=10)

class RiskFactors(BaseModel):
    current_glucose_mg_dl: float
    glucose_change_30m: float
    sleep_hours: float
    steps_last_hour: int
    heart_rate_bpm: float
    hrv_ms: float
    hba1c_percent: float
    meal_carbs_g: float

class PredictResponse(BaseModel):
    patient_id: str
    risk_probability: float
    risk_category: str
    horizon_hours: int
    prediction_label: str
    factors: RiskFactors
    disclaimer: str

class PatientSummary(BaseModel):
    patient_id: str
    age: int
    sex: str
    diabetes_duration_years: float
    hba1c_percent: float
    medication_adherence_proxy: float
    hypertension: bool
    latest_glucose_mg_dl: float
    latest_heart_rate_bpm: float
    latest_steps: int
    latest_sleep_hours: float
