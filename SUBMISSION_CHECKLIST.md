# BloomWatch — Final Submission Checklist

## Files to submit

- [ ] `backend/`
- [ ] `client/src/`
- [ ] `client/package.json`
- [ ] `client/package-lock.json`
- [ ] `ml/`
- [ ] `dl/`
- [ ] `docs/`
- [ ] `README.md`

## Do NOT submit

- [ ] `.venv/`
- [ ] `client/node_modules/`
- [ ] Python `__pycache__/` folders
- [ ] personal Windows dataset paths
- [ ] API keys or `.env` files containing secrets

## Before demonstration

1. Run the backend on port 5000.
2. Run the frontend with `npm run dev`.
3. Open `/api/health` and verify the API responds.
4. Demonstrate the water-quality form.
5. Demonstrate image screening only if the trained image model exists.
6. Explain that the current data does not provide a validated HAB target.
7. Do not state that `Quality = Bad` means HAB.
8. Do not claim a 48–72 hour HAB forecast.

## What to say if the examiner asks why HAB probability is unavailable

“The supplied environmental datasets contain water-quality labels but no validated historical HAB occurrence label linked to the environmental measurements. Training a HAB classifier from those labels would create scientifically unsupported labels. Therefore, the implemented system reports water-quality screening and visual algae screening separately, and the HAB forecasting component is designed to accept a validated HAB dataset when it becomes available.”
