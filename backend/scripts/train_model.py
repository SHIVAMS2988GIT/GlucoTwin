from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from app.config import DATA_DIR, MODEL_DIR, MODEL_FILE
from app.features import FEATURE_COLUMNS

def main():
    source = DATA_DIR / "synthetic_training_examples.csv"
    if not source.exists():
        raise SystemExit("Training data missing. Run: python scripts/generate_data.py")
    df = pd.read_csv(source)
    X, y = df[FEATURE_COLUMNS], df["target"].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=220, max_depth=9, min_samples_leaf=4,
        class_weight="balanced", random_state=42, n_jobs=-1
    )
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    prob = model.predict_proba(X_test)[:, 1]
    metrics = {
        "evaluation": "random holdout from synthetic generated examples",
        "n_train": int(len(X_train)), "n_test": int(len(X_test)),
        "positive_rate_test": float(y_test.mean()),
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, prob)) if y_test.nunique() > 1 else None,
        "warning": "Synthetic-only software sanity metrics; not evidence of clinical performance."
    }
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    (MODEL_DIR / "evaluation_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
    print(f"Saved model to {MODEL_FILE}")

if __name__ == "__main__":
    main()
