from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20261019)

def main():
    n_patients = 80
    n_points = 7 * 24 * 12  # 7 days, 5-minute intervals
    patient_rows, sensor_rows = [], []
    start = pd.Timestamp("2026-10-01T00:00:00")
    for i in range(n_patients):
        pid = f"P-{1001+i}"
        age = int(rng.integers(35, 79))
        duration = round(float(rng.uniform(0.5, 18)), 1)
        hba1c = round(float(np.clip(rng.normal(7.4, 1.0), 5.8, 11.5)), 1)
        adherence = round(float(rng.uniform(0.45, 1.0)), 2)
        hypertension = int(rng.random() < 0.42)
        sex = str(rng.choice(["F", "M"]))
        patient_rows.append({
            "patient_id": pid, "age": age, "sex": sex,
            "diabetes_duration_years": duration, "hba1c_percent": hba1c,
            "medication_adherence_proxy": adherence, "hypertension": hypertension,
            "prior_glucose_mean_mg_dl": round(float(rng.normal(155 + (hba1c-7)*9, 18)), 1),
            "comorbidity_count": int(rng.integers(0, 4)),
        })
        base = 110 + (hba1c - 6.5) * 13 + rng.normal(0, 10)
        glucose = float(np.clip(base, 85, 220))
        hrv_base = float(rng.uniform(24, 65))
        for t in range(n_points):
            ts = start + pd.Timedelta(minutes=5*t)
            hour = ts.hour + ts.minute / 60
            meal_window = any(abs(hour - m) < 0.75 for m in [8, 13, 19])
            carb_bump = rng.normal(17, 8) if meal_window else rng.normal(0, 3)
            glucose += carb_bump * 0.07 + rng.normal(0, 3.0)
            glucose += (base - glucose) * 0.025
            glucose = float(np.clip(glucose, 65, 320))
            steps = int(max(0, rng.normal(500 if 7 <= hour <= 21 else 35, 260)))
            hr = float(np.clip(rng.normal(72 + steps/180, 8), 48, 145))
            hrv = float(np.clip(rng.normal(hrv_base - max(0, hr-75)*0.45, 8), 8, 100))
            sleep = float(np.clip(rng.normal(6.7 if 0 <= hour <= 6 else 0.2, 0.7), 0, 9))
            sensor_rows.append({
                "patient_id": pid, "timestamp": ts.isoformat(),
                "glucose_mg_dl": round(glucose, 2),
                "heart_rate_bpm": round(hr, 2), "hrv_ms": round(hrv, 2),
                "sleep_hours": round(sleep, 2), "steps_last_hour": steps,
                "activity_level": int(min(3, steps // 250)),
            })
    patients = pd.DataFrame(patient_rows)
    sensors = pd.DataFrame(sensor_rows)
    patients.to_csv(DATA / "synthetic_patients.csv", index=False)
    sensors.to_csv(DATA / "synthetic_sensor_timeseries.csv", index=False)

    # Training examples are derived from each patient's EHR and random sensor windows.
    # Event generation is intentionally synthetic and transparent, not a clinical definition.
    examples = []
    for _, p in patients.iterrows():
        s = sensors[sensors.patient_id == p.patient_id].reset_index(drop=True)
        for _ in range(100):
            idx = int(rng.integers(6, len(s)-24))
            current = s.iloc[idx]
            prior = s.iloc[idx-6]
            future = s.iloc[idx+24]
            carbs = float(rng.uniform(10, 120))
            stress = int(rng.integers(1, 11))
            delta30 = float(current.glucose_mg_dl - prior.glucose_mg_dl)
            future_delta = float(future.glucose_mg_dl - current.glucose_mg_dl)
            # A synthetic label: a substantial future rise is more likely with higher carbs,
            # current upward trend, higher baseline risk and low recent activity.
            latent = (
                -3.2 + 0.018*carbs + 0.045*delta30
                + 0.18*(p.hba1c_percent-7)
                + 0.12*(stress-5)
                - 0.001*float(current.steps_last_hour)
                + 0.025*future_delta
                + rng.normal(0, 0.8)
            )
            prob = 1/(1+np.exp(-np.clip(latent, -8, 8)))
            label = int(rng.random() < prob)
            examples.append({
                "age": p.age, "diabetes_duration_years": p.diabetes_duration_years,
                "hba1c_percent": p.hba1c_percent,
                "medication_adherence_proxy": p.medication_adherence_proxy,
                "hypertension": p.hypertension,
                "current_glucose_mg_dl": current.glucose_mg_dl,
                "glucose_change_30m": delta30,
                "heart_rate_bpm": current.heart_rate_bpm,
                "hrv_ms": current.hrv_ms, "sleep_hours": current.sleep_hours,
                "steps_last_hour": current.steps_last_hour,
                "meal_carbs_g": carbs, "stress_level": stress, "target": label,
            })
    pd.DataFrame(examples).to_csv(DATA / "synthetic_training_examples.csv", index=False)
    print(f"Generated {len(patients)} synthetic patients, {len(sensors)} sensor rows, {len(examples)} training examples.")

if __name__ == "__main__":
    main()
