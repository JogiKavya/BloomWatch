# API documentation

Run `py -m flask --app backend.app run --port 5000` after installing `backend/requirements.txt`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Service status and environmental-model availability |
| `/api/model-performance` | GET | Real model availability and limitation status |
| `/api/predict/manual` | POST | Validates seven environmental source fields; returns unsupported status until HAB labels are supplied |
| `/api/predict/image` | POST multipart `image` | Runs saved MobileNetV2 visual screening once trained |
| `/api/predict/combined` | POST multipart | Returns independent results without an invented combined score |

Manual JSON fields are `temperature`, `ph`, `dissolved_oxygen`, `salinity`, `turbidity`, `chlorophyll`, and `nitrate`.
