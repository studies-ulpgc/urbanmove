import unittest
from fastapi.testclient import TestClient
from gateway import InventoryGateway
from main import app, get_service
from service import AcquisitionService
from shared.testing import FakeEventPublisher


class FakeInventoryGateway(InventoryGateway):
    def __init__(self):
        self.calls = 0

    def register_vehicles(self, data, correlation_id: str) -> None:
        self.calls += 1


class TestAcquisitionsService(unittest.TestCase):
    def setUp(self):
        self.fake_inventory = FakeInventoryGateway()
        self.fake_publisher = FakeEventPublisher()
        app.dependency_overrides[get_service] = lambda: AcquisitionService(
            self.fake_inventory, self.fake_publisher
        )
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_register_and_list_acquisition(self):
        payload = {"vehicle_type": "BIKE", "model": "UrbanBike E1", "zone_id": "ZONA-2", "quantity": 3, "unit_cost": 450.0}
        created = self.client.post("/acquisitions", json=payload)
        self.assertEqual(created.status_code, 201)
        self.assertEqual(self.fake_inventory.calls, 1)
        self.assertEqual(self.fake_publisher.published[0][0], "VehiclePurchased")

        listing = self.client.get("/acquisitions")
        self.assertEqual(listing.status_code, 200)
        self.assertGreaterEqual(len(listing.json()), 1)

    def test_rejects_invalid_quantity_or_cost(self):
        payload = {"vehicle_type": "BIKE", "model": "UrbanBike E1", "zone_id": "ZONA-2", "quantity": 0, "unit_cost": -10.0}
        response = self.client.post("/acquisitions", json=payload)
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()