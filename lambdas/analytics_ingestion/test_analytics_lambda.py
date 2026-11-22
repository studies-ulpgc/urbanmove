import json
import unittest

from botocore.exceptions import ClientError
from handler import DATALAKE_BUCKET, lambda_handler

EVENT_ID = "3f2b8c1e-5d4a-4b7e-9a1c-0d2e6f8a1b11"
EVENT_ID_2 = "7a9d4e22-1c3b-4f55-8e60-2b9c7d1e3f22"
EVENT_ID_3 = "c1e5a7b3-9d2f-4a68-b0c4-5e8f1a2d3c33"


class FakeS3Client:
    """Cliente S3 en memoria. `fail_on` simula errores transitorios de S3 por clave."""

    def __init__(self, fail_on=()):
        self.objects = {}
        self.fail_on = fail_on

    def put_object(self, Bucket, Key, Body, ContentType=None):
        if any(fragment in Key for fragment in self.fail_on):
            raise ClientError(
                {"Error": {"Code": "SlowDown", "Message": "Please reduce your request rate"}},
                "PutObject",
            )
        self.objects[Key] = {
            "bucket": Bucket,
            "content_type": ContentType,
            "body": json.loads(Body.decode("utf-8")),
        }

    def keys(self, prefix):
        return [key for key in self.objects if key.startswith(prefix)]


def build_event(**overrides):
    event = {
        "event_id": EVENT_ID,
        "timestamp": "2026-11-22T10:15:30Z",
        "source": "vehicle-service",
        "event_type": "VehicleBatteryLow",
        "schema_version": "1.0",
        "correlation_id": "corr-123",
        "payload": {"vehicle_id": "veh-01", "battery_level": 12.0},
    }
    event.update(overrides)
    return event


def sqs_record(message, message_id="msg-001"):
    return {
        "messageId": message_id,
        "eventSourceARN": "arn:aws:sqs:eu-west-1:123456789012:analytics-queue",
        "body": json.dumps({"Message": json.dumps(message)}),
    }


class TestAnalyticsIngestionLambda(unittest.TestCase):
    def setUp(self):
        self.s3 = FakeS3Client()

    def test_valid_event_is_stored_in_raw_with_ingestion_metadata(self):
        sqs_event = {"Records": [sqs_record(build_event())]}

        result = lambda_handler(sqs_event, client=self.s3)

        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["batchItemFailures"], [])
        keys = self.s3.keys("raw/")
        self.assertEqual(len(keys), 1)
        self.assertIn("event_type=VehicleBatteryLow/", keys[0])
        self.assertIn("source=vehicle-service/", keys[0])
        self.assertTrue(keys[0].endswith(f"{EVENT_ID}.json"))

        stored = self.s3.objects[keys[0]]
        self.assertEqual(stored["bucket"], DATALAKE_BUCKET)
        self.assertEqual(stored["content_type"], "application/json")
        self.assertEqual(stored["body"]["data"], build_event())
        self.assertEqual(stored["body"]["metadata"]["sqs_message_id"], "msg-001")
        self.assertEqual(stored["body"]["metadata"]["source_queue"], "analytics-queue")
        self.assertIn("ingested_at", stored["body"]["metadata"])

    def test_duplicate_event_overwrites_same_object(self):
        sqs_event = {"Records": [sqs_record(build_event())]}

        lambda_handler(sqs_event, client=self.s3)
        lambda_handler(sqs_event, client=self.s3)

        self.assertEqual(len(self.s3.keys("raw/")), 1)

    def test_unsafe_characters_are_sanitized_in_s3_key(self):
        event = build_event(event_type="../evil/type", source="a b/c")
        sqs_event = {"Records": [sqs_record(event)]}

        lambda_handler(sqs_event, client=self.s3)

        key = self.s3.keys("raw/")[0]
        self.assertIn("event_type=..%2Fevil%2Ftype/", key)
        self.assertIn("source=a%20b%2Fc/", key)

    def test_invalid_json_is_sent_to_rejected(self):
        record = {
            "messageId": "msg-bad",
            "eventSourceARN": "arn:aws:sqs:eu-west-1:123456789012:analytics-queue",
            "body": "{esto no es json",
        }

        result = lambda_handler({"Records": [record]}, client=self.s3)

        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["batchItemFailures"], [])
        self.assertEqual(len(self.s3.keys("raw/")), 0)
        rejected = self.s3.objects[self.s3.keys("rejected/")[0]]["body"]
        self.assertEqual(rejected["message_id"], "msg-bad")
        self.assertEqual(rejected["original_body"], "{esto no es json")

    def test_missing_required_field_is_rejected_with_reason(self):
        event = build_event()
        del event["correlation_id"]
        sqs_event = {"Records": [sqs_record(event)]}

        result = lambda_handler(sqs_event, client=self.s3)

        self.assertEqual(result["processed"], 0)
        self.assertEqual(len(self.s3.keys("raw/")), 0)
        rejected = self.s3.objects[self.s3.keys("rejected/")[0]]["body"]
        self.assertIn("correlation_id", rejected["reason"])

    def test_payload_must_be_an_object(self):
        sqs_event = {"Records": [sqs_record(build_event(payload=[1, 2, 3]))]}

        result = lambda_handler(sqs_event, client=self.s3)

        self.assertEqual(result["processed"], 0)
        rejected = self.s3.objects[self.s3.keys("rejected/")[0]]["body"]
        self.assertIn("payload", rejected["reason"])

    def test_event_id_must_be_a_uuid(self):
        sqs_event = {"Records": [sqs_record(build_event(event_id="evt-001"))]}

        result = lambda_handler(sqs_event, client=self.s3)

        self.assertEqual(result["processed"], 0)
        rejected = self.s3.objects[self.s3.keys("rejected/")[0]]["body"]
        self.assertIn("event_id", rejected["reason"])

    def test_timestamp_must_be_iso_8601_with_timezone(self):
        for invalid in ("ayer por la tarde", "2026-11-22T10:15:30"):
            with self.subTest(timestamp=invalid):
                self.s3 = FakeS3Client()
                sqs_event = {"Records": [sqs_record(build_event(timestamp=invalid))]}

                result = lambda_handler(sqs_event, client=self.s3)

                self.assertEqual(result["processed"], 0)
                rejected = self.s3.objects[self.s3.keys("rejected/")[0]]["body"]
                self.assertIn("timestamp", rejected["reason"])

    def test_s3_failure_is_reported_as_batch_item_failure(self):
        self.s3 = FakeS3Client(fail_on=(EVENT_ID,))
        sqs_event = {"Records": [sqs_record(build_event(), message_id="msg-s3")]}

        result = lambda_handler(sqs_event, client=self.s3)

        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["batchItemFailures"], [{"itemIdentifier": "msg-s3"}])
        self.assertEqual(len(self.s3.objects), 0)

    def test_bad_message_does_not_affect_the_rest_of_the_batch(self):
        self.s3 = FakeS3Client(fail_on=(EVENT_ID_3,))
        invalid = build_event(event_id=EVENT_ID_2)
        del invalid["source"]
        sqs_event = {
            "Records": [
                sqs_record(build_event(), message_id="msg-ok"),
                sqs_record(invalid, message_id="msg-invalid"),
                sqs_record(build_event(event_id=EVENT_ID_3), message_id="msg-s3"),
            ]
        }

        result = lambda_handler(sqs_event, client=self.s3)

        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["batchItemFailures"], [{"itemIdentifier": "msg-s3"}])
        self.assertEqual(len(self.s3.keys("raw/")), 1)
        self.assertEqual(len(self.s3.keys("rejected/")), 1)

    def test_empty_batch_does_nothing(self):
        result = lambda_handler({"Records": []}, client=self.s3)

        self.assertEqual(result["processed"], 0)
        self.assertEqual(result["batchItemFailures"], [])
        self.assertEqual(len(self.s3.objects), 0)


if __name__ == "__main__":
    unittest.main()