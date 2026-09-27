import unittest
from backend.app import app


VALID_INPUT = {
    "temperature": 25, "ph": 7.5, "dissolved_oxygen": 5,
    "salinity": 33, "turbidity": 3, "chlorophyll": 2, "nitrate": 0.4,
}


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json["environmental_model_ready"])

    def test_manual_input_returns_real_water_quality_estimate_not_hab(self):
        response = self.client.post("/api/predict/manual", json=VALID_INPUT)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["available"])
        self.assertIn("bad_quality_probability", response.json)
        self.assertIn("hab_limitation", response.json)

    def test_manual_rejects_missing_fields(self):
        response = self.client.post("/api/predict/manual", json={})
        self.assertEqual(response.status_code, 200)
        self.assertIn("validation_errors", response.json)

    def test_image_requires_file(self):
        response = self.client.post("/api/predict/image")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
