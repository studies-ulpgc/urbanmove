import unittest

from fastapi.testclient import TestClient

from shared.app_factory import create_service_app
from shared.events import SnsEventPublisher


class TestSharedComponents(unittest.TestCase):
    def test_create_service_app_exposes_health_endpoint(self):
        app = create_service_app("demo", "Demo Service")
        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "service": "demo"})

    def test_event_envelope_contains_required_metadata(self):
        publisher = SnsEventPublisher("demo-service")
        event = publisher._build_envelope("TestEvent", {"key": "value"}, "corr-123")
        self.assertEqual(event["source"], "demo-service")
        self.assertEqual(event["event_type"], "TestEvent")
        self.assertEqual(event["correlation_id"], "corr-123")
        self.assertIn("event_id", event)
        self.assertIn("timestamp", event)