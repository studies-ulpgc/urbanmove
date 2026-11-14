import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

class TestInventoryService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "inventory"})

    @patch("main.publish_event")
    def test_register_and_list_vehicle(self, mock_publish):
        payload = {"vehicle_type": "SCOOTER", "model": "Xiaomi Pro 2", "zone_id": "ZONA-1"}
        create_res = self.client.post("/vehicles", json=payload)
        self.assertEqual(create_res.status_code, 201)
        self.assertEqual(create_res.json()["status"], "AVAILABLE")
        mock_publish.assert_called_once()

        list_res = self.client.get("/vehicles")
        self.assertEqual(list_res.status_code, 200)
        self.assertGreaterEqual(len(list_res.json()), 1)

if __name__ == "__main__":
    unittest.main()