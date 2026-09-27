# BloomWatch — AI-Based Harmful Algal Bloom Screening & Water-Quality Assessment

BloomWatch is a final-year academic decision-support prototype for environmental monitoring. It combines:

1. **Water-quality classification** using seven environmental measurements.
2. **Visual algae screening** using a MobileNetV2 image classifier when the supplied image dataset/model is available.
3. A React/Vite frontend and Flask REST API.
4. Reproducible model-training, validation, and EDA scripts.
5. Explicit scientific limitations so a water-quality label is never incorrectly presented as a HAB label.

## 1. Important project limitation

The supplied tabular datasets do **not** contain a validated historical `HAB / non-HAB` target. Therefore, the current system must not claim a HAB probability or a 48–72 hour HAB forecast.

The deployed tabular model predicts the dataset's real `Quality` target (`Good` / `Bad`) and calls this a **water-quality screening result**. The image component, when trained, reports **visible algae screening** and does not confirm a harmful algal bloom.

This distinction is intentional and should be explained during the project demonstration.

## 2. Project structure

```text
BloomWatch/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── services/assessment.py
│   └── tests/test_api.py
├── client/
│   ├── src/main.jsx
│   ├── src/styles.css
│   ├── package.json
│   └── index.html
├── ml/
│   ├── training/train_water_quality_models.py
│   ├── training/validate_environmental_data.py
│   ├── evaluation/generate_eda.py
│   └── saved_models/
├── dl/
│   └── training/train_image_model.py
└── docs/
    ├── dataset_analysis.md
    ├── model_documentation.md
    └── api_documentation.md
```

## 3. Run the application

### Backend

From the project root:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r backend\requirements.txt
python -m flask --app backend.app run --port 5000
```

### Frontend

Open a second terminal:

```bash
cd client
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally `http://localhost:5173`.

The frontend uses `http://localhost:5000/api` by default. If the backend is hosted elsewhere, create `client/.env`:

```text
VITE_API_URL=http://YOUR_BACKEND_HOST:5000/api
```

## 4. Train the water-quality models

Place the CSV containing these columns in a local dataset directory:

```text
Temperature, pH, Dissolved_Oxygen, Salinity, Turbidity, Chlorophyll, Nitrate, Quality
```

Then run:

```bash
python ml/training/train_water_quality_models.py "path/to/synthetic_ocean_quality_realistic.csv"
```

Five classifiers are evaluated:

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost
- KNN

The selected deployment model is saved to `ml/saved_models/water_quality_model.joblib` and its metrics to `water_quality_metadata.json`.

## 5. Validate a potential HAB dataset before training

```bash
python ml/training/validate_environmental_data.py "path/to/dataset.csv"
```

The validation script only accepts a genuine HAB target name. It does **not** manufacture labels from thresholds.

A proper future HAB dataset should contain environmental observations plus a verified HAB outcome, with date/time and location or station information.

## 6. Image model

The MobileNetV2 training script expects a directory-style image dataset or the supplied paddy-algae archive. Example:

```bash
python dl/training/train_image_model.py --archive "path/to/paddy algae.zip"
```

The image model's classes are retained from the dataset (`algae`, `early_stage`, `not_algae`). It is a visual algae screen, not a HAB confirmation model.

## 7. EDA

```bash
python ml/evaluation/generate_eda.py "path/to/dataset/folder"
```

The script generates:

- feature histograms
- correlation matrix
- Quality class distribution
- beach chlorophyll time series when `Beach_Clean.csv` is present

## 8. API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Backend health and model readiness |
| GET | `/api/model-performance` | Saved model metrics and limitations |
| POST | `/api/predict/manual` | Water-quality screening from seven measurements |
| POST | `/api/predict/image` | Visual algae screening |
| POST | `/api/predict/combined` | Independent water and image assessments |

## 9. Demonstration flow

1. Start backend and frontend.
2. Open **Assessment**.
3. Select **Water data**.
4. Enter the seven environmental values.
5. Click **Analyze water data**.
6. Explain that the result is a prediction of the dataset's `Quality` label, not a HAB prediction.
7. If the trained image model is installed, select **Image**, upload an image, and demonstrate visual algae screening.
8. Explain the limitation panel: a verified HAB dataset is required before HAB probability or forecasting can be claimed.

## 10. Academic disclaimer

BloomWatch is an academic decision-support prototype. Its outputs are not a substitute for laboratory testing, public-health advice, or official environmental monitoring.
