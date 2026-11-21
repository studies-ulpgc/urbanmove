import unittest

from fastapi.testclient import TestClient
from main import app, get_service
from service import RelocationService

from shared.testing import FakeEventPublisher


class TestRelocationService(unittest.TestCase):
    def setUp(self):
        self.fake_publisher = FakeEventPublisher()
        app.dependency_overrides[get_service] = lambda: RelocationService(self.fake_publisher)
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_create_and_complete_relocation(self):
        payload = {"vehicle_id": "veh-03", "from_zone": "ZONA-2", "to_zone": "ZONA-1"}
        created = self.client.post("/relocation-orders", json=payload)
        self.assertEqual(created.status_code, 201)
        order_id = created.json()["id"]

        listing = self.client.get("/relocation-orders?status=PENDING")
        self.assertEqual(listing.status_code, 200)
        self.assertGreaterEqual(len(listing.json()), 1)

        completed = self.client.patch(f"/relocation-orders/{order_id}/status", json={"status": "COMPLETED"})
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.json()["status"], "COMPLETED")
        self.assertEqual(self.fake_publisher.published[0][0], "RelocationOrderCreated")
        self.assertEqual(self.fake_publisher.published[1][0], "RelocationOrderCompleted")

    def test_unknown_order_returns_404(self):
        res = self.client.patch("/relocation-orders/rel-unknown/status", json={"status": "ASSIGNED"})
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()