import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


class TestIncidentsService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok", "service": "incidents"})

    @patch("main.publish_event")
    def test_report_list_and_resolve_incident(self, mock_publish):
        payload = {"vehicle_id": "veh-05", "description": "Rueda pinchada", "severity": "HIGH"}
        create = self.client.post("/incidents", json=payload)
        self.assertEqual(create.status_code, 201)
        inc_id = create.json()["id"]
        mock_publish.assert_called_once()

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
