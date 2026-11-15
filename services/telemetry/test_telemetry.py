import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


class TestTelemetryService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok", "service": "telemetry"})

    @patch("main.publish_event")
    def test_low_battery_publishes_event(self, mock_publish):
        payload = {"vehicle_id": "veh-10", "battery_level": 15.0, "latitude": 28.1, "longitude": -15.4}
        res = self.client.post("/telemetry", json=payload)
        self.assertEqual(res.status_code, 201)
        mock_publish.assert_called_once()

        latest = self.client.get("/telemetry/veh-10")
        self.assertEqual(latest.status_code, 200)
        self.assertEqual(latest.json()["battery_level"], 15.0)

    def test_unknown_vehicle_returns_404(self):
        self.assertEqual(self.client.get("/telemetry/unknown").status_code, 404)


if __name__ == "__main__":
    unittest.main()
