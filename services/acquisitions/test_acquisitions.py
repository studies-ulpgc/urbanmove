import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


class TestAcquisitionsService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok", "service": "acquisitions"})

    @patch("main.publish_event")
    @patch("main._notify_inventory")
    def test_register_and_list_acquisition(self, mock_sync, mock_publish):
        payload = {
            "vehicle_type": "BIKE",
            "model": "UrbanBike E1",
            "zone_id": "ZONA-2",
            "quantity": 3,
            "unit_cost": 450.0,
        }
        created = self.client.post("/acquisitions", json=payload)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["quantity"], 3)
        mock_sync.assert_called_once()
        mock_publish.assert_called_once()

        listing = self.client.get("/acquisitions")
        self.assertEqual(listing.status_code, 200)
        self.assertGreaterEqual(len(listing.json()), 1)


if __name__ == "__main__":
    unittest.main()
