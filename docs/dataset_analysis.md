# Dataset analysis report

Analysis was performed on 14 September 2026. No files were merged: there is no shared location/station key across the CSVs, `Beach_Clean.csv` is a dated sensor series (2017-10-27 to 2021-01-01), while the other two tabular files have no date or location columns.

| Dataset | Rows × columns | Target / labels | Key fields | Missing / duplicates |
|---|---:|---|---|---|
| `algeas.csv` | 9,784 × 8 | `Population` (numeric algae population, not HAB occurrence) | Light, Nitrate, Iron, Phosphate, Temperature, pH, CO2 | 0 / 0 |
| `Beach_Clean.csv` | 109,891 × 56 | None | timestamp in `Unnamed: 0`, temperature °C, specific conductivity µS/cm, pH, chlorophyll µg/L and rolling summaries | 0 / 0 |
| `synthetic_ocean_quality_realistic.csv` | 100,000 × 8 | `Quality`: Good 90,754; Bad 9,246 | Temperature, pH, dissolved oxygen, salinity, turbidity, chlorophyll, nitrate | 0 / 0 |

## Image archives

| Archive | Classes / layout | Images | Dimensions | Interpretation |
|---|---|---:|---|---|
| `paddy algae.zip` | algae 645; not_algae 280; early_stage 120 | 1,045 JPG | 640 × 640 RGB | Suitable for three-class visual algae screening; imbalanced. |
| `algae images.zip` | object-detection layout with train/validation image copies and YOLO labels | 32 PNG files (16 train, 16 validation) | variable RGBA | Labels need a detection workflow; too small for a general classifier. |
| `archive.zip` | paired `leftImg8bit` and `gtFine` PNG masks | 2,610 PNG files | not inspected as algae labels | Appears to be semantic-segmentation data, not an algae-label archive. |

All sampled image files opened successfully. The paddy archive is the valid candidate for the requested MobileNetV2 classifier. It does **not** provide validated harmful-algal-bloom labels, so “visible algae detected” must not be presented as HAB confirmation.

## Standard schema and units

The application input schema uses only fields actually present in `synthetic_ocean_quality_realistic.csv`: `temperature`, `ph`, `dissolved_oxygen`, `salinity`, `turbidity`, `chlorophyll`, and `nitrate`. Units are not documented in that source, so the UI marks them as source units/unspecified instead of inventing conversions. `Beach_Clean.csv` explicitly identifies temperature as °C, conductivity as µS/cm and chlorophyll as µg/L.

## Critical limitation

None of the provided tabular datasets contains a validated historical HAB/non-HAB label, spatial key, or time-linked future HAB outcome. Accordingly, this project does not train the required five HAB classifiers, does not display HAB probabilities, and does not claim 48–72-hour forecasts. Training them against `Quality` or a threshold-generated label would be scientifically invalid. To enable the manual HAB model, add date/time, latitude/longitude or station ID, the listed environmental measurements, and a verified HAB occurrence/outcome column.
