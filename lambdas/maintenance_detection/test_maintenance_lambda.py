import json
import unittest

from handler import lambda_handler

from shared.lambda_utils import PROCESSED_IDS
from shared.testing import FakeOrderClient


class TestMaintenanceLambda(unittest.TestCase):
    def setUp(self):
        PROCESSED_IDS.clear()
        self.client = FakeOrderClient()

    def test_low_battery_creates_recharge_order_only_once(self):
        sns_message = {
            "event_id": "evt-001",
            "event_type": "VehicleBatteryLow",
            "correlation_id": "corr-123",
            "payload": {"vehicle_id": "veh-01", "battery_level": 12.0},
        }
        sqs_event = {"Records": [{"body": json.dumps({"Message": json.dumps(sns_message)})}]}

        self.assertEqual(lambda_handler(sqs_event, client=self.client)["processed"], 1)
        self.assertEqual(lambda_handler(sqs_event, client=self.client)["processed"], 0)
        self.assertEqual(len(self.client.requests), 1)
        self.assertEqual(self.client.requests[0][1]["order_type"], "RECHARGE")

    def test_unrelated_event_is_ignored(self):
        sns_message = {"event_id": "evt-002", "event_type": "VehiclePurchased", "payload": {"vehicle_id": "veh-02"}}
        sqs_event = {"Records": [{"body": json.dumps({"Message": json.dumps(sns_message)})}]}

        result = lambda_handler(sqs_event, client=self.client)
        self.assertEqual(result["processed"], 0)
        self.assertEqual(len(self.client.requests), 0)


if __name__ == "__main__":
    unittest.main()