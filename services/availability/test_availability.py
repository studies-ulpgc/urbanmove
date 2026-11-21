import unittest

from fastapi.testclient import TestClient
from main import app


class TestAvailabilityService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_register_list_lock_and_release(self):
        payload = {"vehicle_id": "veh-001", "vehicle_type": "SCOOTER", "zone_id": "ZONA-1"}
        self.assertEqual(self.client.post("/availability", json=payload).status_code, 201)

        avail = self.client.get("/availability?zone_id=ZONA-1&vehicle_type=SCOOTER")
        self.assertTrue(any(v["vehicle_id"] == "veh-001" for v in avail.json()))

        lock = self.client.post("/availability/veh-001/lock")
        self.assertEqual(lock.status_code, 200)
        self.assertFalse(lock.json()["is_available"])
        self.assertEqual(self.client.post("/availability/veh-001/lock").status_code, 409)

        release = self.client.post("/availability/veh-001/release")
        self.assertEqual(release.status_code, 200)
        self.assertTrue(release.json()["is_available"])

    def test_lock_or_release_unknown_vehicle_returns_404(self):
        self.assertEqual(self.client.post("/availability/unknown/lock").status_code, 404)
        self.assertEqual(self.client.post("/availability/unknown/release").status_code, 404)


if __name__ == "__main__":
    unittest.main()