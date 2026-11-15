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
    def test_full_vehicle_lifecycle(self, mock_publish):
        payload = {"vehicle_type": "SCOOTER", "model": "Xiaomi Pro 2", "zone_id": "ZONA-1"}
        create_res = self.client.post("/vehicles", json=payload)
        self.assertEqual(create_res.status_code, 201)
        vehicle_id = create_res.json()["id"]
        mock_publish.assert_called_once()

        list_res = self.client.get("/vehicles?zone_id=ZONA-1&status=AVAILABLE")
        self.assertEqual(list_res.status_code, 200)
        self.assertGreaterEqual(len(list_res.json()), 1)

        patch_res = self.client.patch(f"/vehicles/{vehicle_id}/status", json={"status": "WITHDRAWN"})
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["status"], "WITHDRAWN")

    def test_update_nonexistent_vehicle_returns_404(self):
        res = self.client.patch("/vehicles/veh-inexistente/status", json={"status": "RETIRED"})
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
