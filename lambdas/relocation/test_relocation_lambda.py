import json
import unittest
from unittest.mock import MagicMock, patch

from handler import lambda_handler


class TestRelocationLambda(unittest.TestCase):
    @patch("handler.urllib.request.urlopen")
    def test_demand_hotspot_creates_relocation_order(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 201
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        sns_message = {
            "event_type": "DemandHotspotDetected",
            "correlation_id": "corr-456",
            "payload": {"vehicle_id": "veh-04", "excess_zone": "ZONA-2", "deficit_zone": "ZONA-1"},
        }
        sqs_event = {"Records": [{"body": json.dumps({"Message": json.dumps(sns_message)})}]}

        result = lambda_handler(sqs_event)
        self.assertEqual(result["created"], 1)
        mock_urlopen.assert_called_once()

    @patch("handler.urllib.request.urlopen")
    def test_other_event_is_ignored(self, mock_urlopen):
        sns_message = {"event_type": "RideFinished", "payload": {"vehicle_id": "veh-04"}}
        sqs_event = {"Records": [{"body": json.dumps({"Message": json.dumps(sns_message)})}]}

        result = lambda_handler(sqs_event)
        self.assertEqual(result["created"], 0)
        mock_urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()