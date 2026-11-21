import unittest
from fastapi.testclient import TestClient
from main import app, get_service
from service import IncidentService
from shared.testing import FakeEventPublisher


class TestIncidentsService(unittest.TestCase):
    def setUp(self):
        self.fake_publisher = FakeEventPublisher()
        app.dependency_overrides[get_service] = lambda: IncidentService(self.fake_publisher)
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_report_list_and_resolve_incident(self):
        payload = {"vehicle_id": "veh-05", "description": "Rueda pinchada", "severity": "HIGH"}
        create = self.client.post("/incidents", json=payload)
        self.assertEqual(create.status_code, 201)
        inc_id = create.json()["id"]
        self.assertEqual(self.fake_publisher.published[0][0], "IncidentReported")

        listing = self.client.get("/incidents?status=OPEN")
        self.assertEqual(listing.status_code, 200)
        self.assertGreaterEqual(len(listing.json()), 1)

        resolved = self.client.patch(f"/incidents/{inc_id}/resolve")
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(resolved.json()["status"], "RESOLVED")

    def test_resolve_unknown_incident_returns_404(self):
        self.assertEqual(self.client.patch("/incidents/inc-unknown/resolve").status_code, 404)


if __name__ == "__main__":
    unittest.main()