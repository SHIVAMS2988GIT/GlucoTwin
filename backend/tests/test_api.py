from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_model_info_shape():
    response = client.get("/api/model-info")
    assert response.status_code == 200
    body = response.json()
    assert body["data"] == "synthetic only"
    assert body["clinical_validation"] == "not performed"


def test_patient_list_and_profile():
    patients_response = client.get("/api/patients")
    assert patients_response.status_code == 200
    patients = patients_response.json()
    assert patients
    patient_id = patients[0]["patient_id"]

    profile_response = client.get(f"/api/patients/{patient_id}")
    assert profile_response.status_code == 200
    profile = profile_response.json()
    assert profile["patient_id"] == patient_id
    assert "hba1c_percent" in profile


def test_patient_timeline():
    patients = client.get("/api/patients").json()
    patient_id = patients[0]["patient_id"]
    response = client.get(f"/api/patients/{patient_id}/timeline")
    assert response.status_code == 200
    rows = response.json()
    assert rows
    assert "timestamp" in rows[0]
    assert "glucose_mg_dl" in rows[0]


def test_prediction_shape_and_probability_range():
    response = client.post(
        "/api/predict",
        json={"patient_id": "P-1001", "meal_carbs_g": 55, "stress_level": 4},
    )
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["risk_probability"] <= 1
    assert body["horizon_hours"] == 2
    assert body["patient_id"] == "P-1001"
    assert "synthetic" in body["disclaimer"].lower()


def test_prediction_rejects_out_of_range_inputs():
    response = client.post(
        "/api/predict",
        json={"patient_id": "P-1001", "meal_carbs_g": 55, "stress_level": 11},
    )
    assert response.status_code == 422


def test_unknown_patient_is_404():
    response = client.post("/api/predict", json={"patient_id": "P-DOES-NOT-EXIST"})
    assert response.status_code == 404
