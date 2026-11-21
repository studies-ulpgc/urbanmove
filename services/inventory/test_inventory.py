import unittest

from fastapi.testclient import TestClient
from main import app, get_service
from service import InventoryService

from shared.testing import FakeEventPublisher


class TestInventoryService(unittest.TestCase):
    def setUp(self):
        self.fake_publisher = FakeEventPublisher()
        app.dependency_overrides[get_service] = lambda: InventoryService(self.fake_publisher)
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_full_vehicle_lifecycle(self):
        payload = {"vehicle_type": "SCOOTER", "model": "Xiaomi Pro 2", "zone_id": "ZONA-1"}
        create_res = self.client.post("/vehicles", json=payload)
        self.assertEqual(create_res.status_code, 201)
        vehicle_id = create_res.json()["id"]
        self.assertEqual(self.fake_publisher.published[0][0], "VehiclePurchased")

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