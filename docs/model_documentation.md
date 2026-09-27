# Model documentation

## Environmental HAB model

Status: intentionally unavailable. The supplied environmental datasets have algae population and water-quality outcomes, but no historical verified HAB occurrence. The API never fabricates a HAB probability, HAB risk level, feature importance, or forecast.

## Water-quality model

`ml/training/train_water_quality_models.py` uses the genuine `Quality` target in `synthetic_ocean_quality_realistic.csv`: Good (90,754) and Bad (9,246). It trains Logistic Regression, Decision Tree, Random Forest, XGBoost, and KNN using a reproducible stratified held-out test set. It selects by Bad-class recall, then F1 and ROC-AUC, saves the model and its actual metrics, and exposes only an estimated **bad-water-quality probability**. The dataset is synthetic and this target is not a proxy for HAB.

When a proper HAB-labelled dataset is added, train Logistic Regression, Decision Tree, Random Forest, XGBoost, and KNN in leakage-safe pipelines; use a chronological split when timestamps exist, calibrate the selected classifier, and save real test metrics plus the preprocessing pipeline. `ml/training/validate_environmental_data.py` prevents an unsupported training run.

## Image model

`dl/training/train_image_model.py` creates a three-class MobileNetV2 transfer-learning model from the paddy archive. It uses a stratified-directory validation split, horizontal flip/small rotation/zoom augmentation, early stopping, a checkpoint, and saves actual metrics. Output wording is intentionally limited to visual algae screening.
