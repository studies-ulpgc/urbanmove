import unittest
from fastapi.testclient import TestClient
from main import app, get_service
from service import MaintenanceService
from shared.testing import FakeEventPublisher


class TestMaintenanceService(unittest.TestCase):
    def setUp(self):
        self.fake_publisher = FakeEventPublisher()
        app.dependency_overrides[get_service] = lambda: MaintenanceService(self.fake_publisher)
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_create_and_complete_maintenance_order(self):
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
        self.assertEqual(self.fake_publisher.published[0][0], "VehicleWithdrawnForMaintenance")
        self.assertEqual(self.fake_publisher.published[1][0], "VehicleReturnedToService")

    def test_complete_unknown_order_returns_404(self):
        self.assertEqual(self.client.patch("/maintenance-orders/mnt-unknown/complete").status_code, 404)


if __name__ == "__main__":
    unittest.main()