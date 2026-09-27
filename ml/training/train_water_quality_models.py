"""Train water-quality classifiers using a supplied CSV.

IMPORTANT: the target is the dataset's Quality column (Good/Bad), not HAB
occurrence. This script must never manufacture a HAB label from thresholds.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

ROOT = Path(__file__).resolve().parents[2]
FEATURES = ["Temperature", "pH", "Dissolved_Oxygen", "Salinity", "Turbidity", "Chlorophyll", "Nitrate"]


def score(name, model, x_test, y_test):
    pred = model.predict(x_test)
    probability = model.predict_proba(x_test)[:, 1]
    return {
        "model": name,
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision_bad": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall_bad": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1_bad": round(float(f1_score(y_test, pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
        "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    }


def make_pipeline(model, scaled=True):
    steps = [("imputer", SimpleImputer(strategy="median"))]
    if scaled:
        steps.append(("scaler", StandardScaler()))
    steps.append(("model", model))
    return Pipeline(steps)


def main():
    parser = argparse.ArgumentParser(description="Train the water-quality screening models.")
    parser.add_argument("csv", type=Path, help="CSV containing the Quality target")
    parser.add_argument("--output", type=Path, default=ROOT / "ml" / "saved_models")
    args = parser.parse_args()

    if not args.csv.exists():
        raise FileNotFoundError(f"Dataset not found: {args.csv}")
    data = pd.read_csv(args.csv)
    required = FEATURES + ["Quality"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    x = data[FEATURES]
    y = (data["Quality"].astype(str).str.strip().str.lower() == "bad").astype(int)
    if y.nunique() < 2:
        raise ValueError("Quality must contain both Good and Bad classes.")

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=.2, random_state=42, stratify=y
    )
    models = {
        "Logistic Regression": make_pipeline(LogisticRegression(max_iter=2000, class_weight="balanced")),
        "Decision Tree": make_pipeline(DecisionTreeClassifier(max_depth=12, class_weight="balanced", random_state=42), False),
        "Random Forest": make_pipeline(RandomForestClassifier(n_estimators=250, min_samples_leaf=3, class_weight="balanced", random_state=42, n_jobs=-1), False),
        "XGBoost": make_pipeline(XGBClassifier(n_estimators=250, max_depth=6, learning_rate=.08, subsample=.85, colsample_bytree=.85, eval_metric="logloss", random_state=42, n_jobs=4), False),
        "KNN": make_pipeline(KNeighborsClassifier(n_neighbors=15, weights="distance")),
    }

    results, fitted = [], {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        results.append(score(name, model, x_test, y_test))
        fitted[name] = model

    # The deployed screening model prioritizes detection of the Bad class.
    selected = max(results, key=lambda row: (row["recall_bad"], row["f1_bad"], row["roc_auc"]))
    args.output.mkdir(parents=True, exist_ok=True)
    joblib.dump(fitted[selected["model"]], args.output / "water_quality_model.joblib")
    metadata = {
        "target": "Quality (Bad=1, Good=0)",
        "feature_columns": [f.lower() for f in FEATURES],
        "source_columns": FEATURES,
        "best_model": selected["model"],
        "selection_rule": "Highest Bad-class recall, then F1 and ROC-AUC on held-out stratified test data.",
        "class_distribution": {"Good": int((y == 0).sum()), "Bad": int((y == 1).sum())},
        "results": results,
        "dataset_file": str(args.csv),
        "limitation": "This is water-quality classification from the supplied Quality label, not HAB prediction or forecasting.",
    }
    (args.output / "water_quality_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
