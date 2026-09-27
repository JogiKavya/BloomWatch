"""Flask API for the AI-Based HAB Prediction and Risk Assessment System.

This service intentionally refuses environmental HAB predictions until a model
trained with genuine HAB occurrence labels is supplied.  It must never turn a
water-quality label into a HAB label.
"""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from backend.services.assessment import (
    DATA_LIMITATION,
    allowed_image,
    image_assessment,
    manual_assessment,
    combined_assessment,
    model_performance,
)

ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__)
app.config.update(MAX_CONTENT_LENGTH=8 * 1024 * 1024)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGIN", "http://localhost:5173")}})


@app.get("/api/health")
def health():
    from backend.services.assessment import QUALITY_MODEL, QUALITY_METADATA

    model_ready = QUALITY_MODEL.exists() and QUALITY_METADATA.exists()

    return jsonify({
        "status": "ok",
        "service": "HAB Risk Assessment API",
        "environmental_model_ready": model_ready
    })


@app.get("/api/model-performance")
def performance():
    return jsonify(model_performance())


@app.post("/api/predict/manual")
def predict_manual():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send a JSON object containing environmental measurements."}), 400
    return jsonify(manual_assessment(payload))


@app.post("/api/predict/image")
def predict_image():
    image = request.files.get("image")
    if image is None:
        return jsonify({"error": "An image field is required."}), 400
    if not allowed_image(image):
        return jsonify({"error": "Use a PNG, JPG, or JPEG image."}), 400
    result, status = image_assessment(image)
    return jsonify(result), status


@app.post("/api/predict/combined")
def predict_combined():
    image = request.files.get("image")
    raw = request.form.get("environmental_data")
    if image is None or raw is None:
        return jsonify({"error": "Both an image and environmental_data JSON are required."}), 400
    if not allowed_image(image):
        return jsonify({"error": "Use a PNG, JPG, or JPEG image."}), 400
    import json
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return jsonify({"error": "environmental_data must be valid JSON."}), 400
    result, status = combined_assessment(data, image)
    return jsonify(result), status


@app.errorhandler(RequestEntityTooLarge)
def too_large(_):
    return jsonify({"error": "The image is too large. Maximum upload size is 8 MB."}), 413


@app.errorhandler(Exception)
def unexpected(error):
    app.logger.exception("Unhandled API error")
    return jsonify({
        "error": str(error),
        "type": type(error).__name__
    }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
