from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
PATIENTS_FILE = DATA_DIR / "synthetic_patients.csv"
SENSORS_FILE = DATA_DIR / "synthetic_sensor_timeseries.csv"
MODEL_FILE = MODEL_DIR / "glucotwin_model.joblib"
