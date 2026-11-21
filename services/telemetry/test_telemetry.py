import unittest
from fastapi.testclient import TestClient
from main import app, get_service
from service import TelemetryService
from shared.testing import FakeEventPublisher


class TestTelemetryService(unittest.TestCase):
    def setUp(self):
        self.fake_publisher = FakeEventPublisher()
        app.dependency_overrides[get_service] = lambda: TelemetryService(self.fake_publisher)
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_low_battery_publishes_event(self):
        payload = {"vehicle_id": "veh-10", "battery_level": 15.0, "latitude": 28.1, "longitude": -15.4}
        res = self.client.post("/telemetry", json=payload)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.fake_publisher.published[0][0], "VehicleBatteryLow")

        latest = self.client.get("/telemetry/veh-10")
        self.assertEqual(latest.status_code, 200)
        self.assertEqual(latest.json()["battery_level"], 15.0)

    def test_healthy_battery_does_not_publish_event(self):
        payload = {"vehicle_id": "veh-11", "battery_level": 85.0, "latitude": 28.1, "longitude": -15.4}
        self.assertEqual(self.client.post("/telemetry", json=payload).status_code, 201)
        self.assertEqual(len(self.fake_publisher.published), 0)

    def test_unknown_vehicle_returns_404(self):
        self.assertEqual(self.client.get("/telemetry/unknown").status_code, 404)


if __name__ == "__main__":
    unittest.main()