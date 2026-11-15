import json
import unittest
from unittest.mock import MagicMock, patch

from handler import lambda_handler


class TestMaintenanceLambda(unittest.TestCase):
    @patch("handler.urllib.request.urlopen")
    def test_low_battery_event_creates_recharge_order(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        sns_message = {
            "event_type": "VehicleBatteryLow",
            "correlation_id": "corr-123",
            "payload": {"vehicle_id": "veh-01", "battery_level": 12.0},
        }
        sqs_event = {"Records": [{"body": json.dumps({"Message": json.dumps(sns_message)})}]}

        result = lambda_handler(sqs_event)
        self.assertEqual(result["processed"], 1)
        mock_urlopen.assert_called_once()

    @patch("handler.urllib.request.urlopen")
    def test_unrelated_event_is_ignored(self, mock_urlopen):
        sns_message = {"event_type": "VehiclePurchased", "payload": {"vehicle_id": "veh-02"}}
        sqs_event = {"Records": [{"body": json.dumps({"Message": json.dumps(sns_message)})}]}

        result = lambda_handler(sqs_event)
        self.assertEqual(result["processed"], 0)
        mock_urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()