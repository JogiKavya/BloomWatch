"""Prediction services. Model-dependent responses never fabricate a result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[2]

IMAGE_MODEL = ROOT / "dl" / "saved_models" / "algae_mobilenetv2.keras"
IMAGE_METADATA = ROOT / "dl" / "saved_models" / "image_metadata.json"

QUALITY_MODEL = ROOT / "ml" / "saved_models" / "water_quality_model.joblib"
QUALITY_METADATA = ROOT / "ml" / "saved_models" / "water_quality_metadata.json"


DATA_LIMITATION = (
    "No supplied environmental dataset contains a validated historical HAB occurrence label. "
    "The current project therefore cannot estimate HAB probability or make a forecast from manual data. "
    "Add dated, location-linked observations with HAB/non-HAB outcomes to train this component."
)


FEATURES = [
    "temperature",
    "ph",
    "dissolved_oxygen",
    "salinity",
    "turbidity",
    "chlorophyll",
    "nitrate",
]


def allowed_image(file) -> bool:
    return (
        file.mimetype in {"image/jpeg", "image/png"}
        and file.filename.lower().endswith((".jpg", ".jpeg", ".png"))
    )


def _validate_measurements(data: dict[str, Any]) -> list[str]:
    errors = []

    for name in FEATURES:
        value = data.get(name)

        if value is None or value == "":
            errors.append(f"{name} is required")
            continue

        try:
            float(value)
        except (TypeError, ValueError):
            errors.append(f"{name} must be numeric")

    return errors


def manual_assessment(data: dict[str, Any]) -> dict[str, Any]:

    errors = _validate_measurements(data)

    if errors:
        return {
            "available": False,
            "validation_errors": errors,
            "message": "Correct the highlighted environmental inputs.",
        }

    if not QUALITY_MODEL.exists() or not QUALITY_METADATA.exists():
        return {
            "available": False,
            "message": (
                "The water-quality model has not been trained. "
                "Run ml/training/train_water_quality_models.py."
            ),
            "early_warning": None,
        }

    import joblib
    import pandas as pd

    metadata = json.loads(
        QUALITY_METADATA.read_text(encoding="utf-8")
    )

    model = joblib.load(QUALITY_MODEL)

    # Compatibility with LogisticRegression models saved
    # using a different scikit-learn version.
    estimator = None

    if hasattr(model, "named_steps"):
        estimator = model.named_steps.get("model")

    if estimator is not None and not hasattr(estimator, "multi_class"):
        estimator.multi_class = "auto"

    frame = pd.DataFrame(
        [[float(data[name]) for name in FEATURES]],
        columns=metadata["source_columns"],
    )

    probability = float(
        model.predict_proba(frame)[0][1]
    )

    concern = (
        "HIGH"
        if probability > 0.66
        else "MODERATE"
        if probability >= 0.33
        else "LOW"
    )

    explanation = []

    if estimator is not None and hasattr(estimator, "coef_"):

        coefficients = sorted(
            zip(
                FEATURES,
                estimator.coef_[0],
                frame.iloc[0],
            ),
            key=lambda row: abs(row[1] * row[2]),
            reverse=True,
        )[:4]

        explanation = [
            {
                "feature": feature.replace("_", " ").title(),
                "relative_contribution": round(
                    float(abs(coef * value)),
                    3,
                ),
            }
            for feature, coef, value in coefficients
        ]

    recommendations = {
        "LOW": [
            "Continue routine water-quality monitoring.",
            "Record measurements consistently for future comparison.",
        ],
        "MODERATE": [
            "Increase monitoring frequency and recheck the measurements.",
            "Inspect the water body for visible changes or algae accumulation.",
        ],
        "HIGH": [
            "Treat this as a water-quality screening alert and recheck measurements.",
            "Avoid direct contact with visibly affected water until it is assessed.",
            "Seek laboratory or environmental-authority assessment if a bloom is suspected.",
        ],
    }[concern]

    return {
        "available": True,
        "assessment_type": "water-quality screening",
        "prediction": (
            "Bad water quality likely"
            if probability >= 0.5
            else "Good water quality likely"
        ),
        "bad_quality_probability": probability,
        "concern_level": concern,
        "explanation": explanation,
        "recommendations": recommendations,
        "early_warning": None,
        "hab_limitation": DATA_LIMITATION,
        "disclaimer": metadata["limitation"],
    }


def _load_image_model():

    if not IMAGE_MODEL.exists() or not IMAGE_METADATA.exists():
        return None, None

    import tensorflow as tf

    return (
        tf.keras.models.load_model(IMAGE_MODEL),
        json.loads(
            IMAGE_METADATA.read_text(encoding="utf-8")
        ),
    )


def image_assessment(file):

    try:
        image = Image.open(file.stream)
        image.verify()
        file.stream.seek(0)

    except (UnidentifiedImageError, OSError):

        return {
            "error": "The uploaded file is not a valid image."
        }, 400

    try:
        model, metadata = _load_image_model()

    except Exception:

        return {
            "error": "The image model could not be loaded."
        }, 503

    if model is None:

        return {
            "available": False,
            "message": (
                "Image model has not been trained yet. "
                "Run dl/training/train_image_model.py "
                "with the supplied paddy algae archive."
            ),
            "dataset_classes": [
                "algae",
                "early_stage",
                "not_algae",
            ],
        }, 503

    import numpy as np

    from tensorflow.keras.applications.mobilenet_v2 import (
        preprocess_input,
    )

    file.stream.seek(0)

    array = np.asarray(
        Image.open(file.stream)
        .convert("RGB")
        .resize((224, 224)),
        dtype="float32",
    )

    probabilities = model.predict(
        preprocess_input(array[None, ...]),
        verbose=0,
    )[0]

    index = int(np.argmax(probabilities))

    label = metadata["class_names"][index]

    confidence = float(
        probabilities[index]
    )

    visible = label in {
        "algae",
        "early_stage",
    }

    return {
        "available": True,
        "prediction": label.replace("_", " ").title(),
        "confidence": confidence,
        "visual_assessment": (
            "Visible algae detected"
            if visible
            else "No visible algae detected"
        ),
        "explanation": (
            "This image classification is a visual screening result. "
            "It does not by itself confirm a harmful algal bloom."
        ),
        "recommendations": [
            "Inspect the water body and record observations.",
            "Use laboratory confirmation for suspected harmful blooms.",
        ],
    }, 200


def combined_assessment(data, image):

    manual = manual_assessment(data)

    image_result, image_status = image_assessment(image)

    return {
        "experimental_combined_assessment": False,
        "manual_assessment": manual,
        "image_assessment": image_result,
        "message": (
            "No combined HAB score is shown because the environmental "
            "HAB component has not been validated."
        ),
    }, max(200, image_status)


def model_performance():

    return {
        "environmental_hab_model": {
            "available": False,
            "reason": DATA_LIMITATION,
        },

        "water_quality_model": (
            json.loads(
                QUALITY_METADATA.read_text(
                    encoding="utf-8"
                )
            )
            if QUALITY_METADATA.exists()
            else {
                "available": False
            }
        ),

        "image_model": {
            "available": IMAGE_MODEL.exists(),
            "model": "MobileNetV2 transfer learning",
            "metrics": (
                None
                if not IMAGE_MODEL.exists()
                else "See dl/saved_models/image_metrics.json"
            ),
        },

        "dataset_note": (
            "Water-quality classes must not be interpreted as HAB labels."
        ),
    }