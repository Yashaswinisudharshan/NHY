import os
import pickle

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_FILE = BASE_DIR / "data" / "fraud_dataset.csv"
MODEL_FILE = BASE_DIR / "models" / "fraud_model.pkl"


categorical_columns = [
    "project_type",
    "department",
    "state",
    "district",
    "inspection_status",
]


def get_risk_level(fraud_score):
    """Convert fraud probability into a simple risk level."""
    if fraud_score < 0.3:
        return "LOW"
    if fraud_score < 0.7:
        return "MEDIUM"
    return "HIGH"


def get_rule_based_reasons(input_data):
    """Create beginner-friendly reasons based on suspicious input values."""
    reasons = []

    if input_data.get("budget_claim_ratio", 0) > 0.8:
        reasons.append("High budget claim ratio")

    if input_data.get("work_money_gap", 0) > 0.3:
        reasons.append("High gap between claimed money and completed work")

    if input_data.get("delay_ratio", 0) > 1.2:
        reasons.append("Project is delayed compared to expected duration")

    if input_data.get("quantity_mismatch_ratio", 0) > 0.3:
        reasons.append("High mismatch between claimed and verified work quantity")

    if input_data.get("geo_tagged_proof_submitted", 1) == 0:
        reasons.append("Geo-tagged proof is missing")

    if str(input_data.get("inspection_status", "")).upper() == "PENDING":
        reasons.append("Inspection is still pending")

    if input_data.get("complaints_count", 0) > 10:
        reasons.append("High number of public complaints")

    if input_data.get("contractor_blacklist_flag", 0) == 1:
        reasons.append("Contractor has a blacklist flag")

    if not reasons:
        reasons.append("No major rule-based warning signs found")

    return reasons


def main():
    """Load the dataset, train the model, print metrics, and save the pipeline."""
    dataset = pd.read_csv(DATASET_FILE)

    # fraud_label is the target used for classification.
    y = dataset["fraud_label"]

    # Drop fraud_score because it was used to create fraud_label.
    # Keeping it would cause data leakage.
    X = dataset.drop(columns=["fraud_score", "fraud_label"])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # All non-categorical columns are passed through unchanged.
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_columns)
        ],
        remainder="passthrough",
    )

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42,
        class_weight="balanced",
    )

    # Pipeline keeps preprocessing and model training together.
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred))
    print("Recall:", recall_score(y_test, y_pred))
    print("F1 score:", f1_score(y_test, y_pred))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Create the models folder automatically if it does not exist.
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with MODEL_FILE.open("wb") as file:
        pickle.dump(pipeline, file)

    print("Model saved as:", MODEL_FILE)


if __name__ == "__main__":
    main()