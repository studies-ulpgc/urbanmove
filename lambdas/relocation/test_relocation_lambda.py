import json
import unittest

from handler import lambda_handler

from shared.lambda_utils import PROCESSED_IDS
from shared.testing import FakeOrderClient


class TestRelocationLambda(unittest.TestCase):
    def setUp(self):
        PROCESSED_IDS.clear()
        self.client = FakeOrderClient()

    def test_demand_hotspot_creates_relocation_order_only_once(self):
        sns_message = {
            "event_id": "evt-101",
            "event_type": "DemandHotspotDetected",
            "correlation_id": "corr-456",
            "payload": {"vehicle_id": "veh-04", "excess_zone": "ZONA-2", "deficit_zone": "ZONA-1"},
        }
        sqs_event = {"Records": [{"body": json.dumps({"Message": json.dumps(sns_message)})}]}

        self.assertEqual(lambda_handler(sqs_event, client=self.client)["created"], 1)
        self.assertEqual(lambda_handler(sqs_event, client=self.client)["created"], 0)
        self.assertEqual(len(self.client.requests), 1)
        self.assertEqual(self.client.requests[0][1]["to_zone"], "ZONA-1")

    def test_other_event_is_ignored(self):
        sns_message = {"event_id": "evt-102", "event_type": "RideFinished", "payload": {"vehicle_id": "veh-04"}}
        sqs_event = {"Records": [{"body": json.dumps({"Message": json.dumps(sns_message)})}]}

        result = lambda_handler(sqs_event, client=self.client)
        self.assertEqual(result["created"], 0)
        self.assertEqual(len(self.client.requests), 0)


if __name__ == "__main__":
    unittest.main()