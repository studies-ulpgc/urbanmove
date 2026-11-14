import unittest

from fastapi.testclient import TestClient
from main import app


class TestAvailabilityService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "availability"})

    def test_register_lock_and_release_vehicle(self):
        payload = {"vehicle_id": "veh-001", "vehicle_type": "SCOOTER", "zone_id": "ZONA-1"}
        reg = self.client.post("/availability", json=payload)
        self.assertEqual(reg.status_code, 201)
        self.assertTrue(reg.json()["is_available"])

        lock = self.client.post("/availability/veh-001/lock")
        self.assertEqual(lock.status_code, 200)
        self.assertFalse(lock.json()["is_available"])

        release = self.client.post("/availability/veh-001/release")
        self.assertEqual(release.status_code, 200)
        self.assertTrue(release.json()["is_available"])


if __name__ == "__main__":
    unittest.main()