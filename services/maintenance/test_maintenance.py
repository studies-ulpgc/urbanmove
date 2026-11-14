import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


class TestMaintenanceService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok", "service": "maintenance"})

    @patch("main.publish_event")
    def test_create_and_complete_maintenance_order(self, mock_publish):
        payload = {"vehicle_id": "veh-08", "order_type": "RECHARGE", "reason": "Batería al 12%"}
        created = self.client.post("/maintenance-orders", json=payload)
        self.assertEqual(created.status_code, 201)
        order_id = created.json()["id"]

        listing = self.client.get("/maintenance-orders?status=OPEN")
        self.assertEqual(listing.status_code, 200)
        self.assertGreaterEqual(len(listing.json()), 1)

        completed = self.client.patch(f"/maintenance-orders/{order_id}/complete")
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.json()["status"], "COMPLETED")
        self.assertEqual(mock_publish.call_count, 2)

    def test_complete_unknown_order_returns_404(self):
        self.assertEqual(self.client.patch("/maintenance-orders/mnt-unknown/complete").status_code, 404)


if __name__ == "__main__":
    unittest.main()