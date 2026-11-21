import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime

import boto3
from botocore.config import Config


class EventPublisher(ABC):
    @abstractmethod
    def publish(self, event_type: str, payload: dict, correlation_id: str) -> None:
        pass

class SnsEventPublisher(EventPublisher):
    def __init__(self, source: str):
        self.source = source
        self.topic_arn = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:000000000000:urbanmove-events")
        self.client = boto3.client(
            "sns",
            endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
            config=Config(connect_timeout=1, read_timeout=1, retries={"max_attempts": 1}),
        )
        self.logger = logging.getLogger(source)

    def publish(self, event_type: str, payload: dict, correlation_id: str) -> None:
        event = self._build_envelope(event_type, payload, correlation_id)
        self._send_to_sns(event_type, event, correlation_id)

    def _build_envelope(self, event_type: str, payload: dict, correlation_id: str) -> dict:
        return {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "source": self.source,
            "event_type": event_type,
            "schema_version": "1.0",
            "correlation_id": correlation_id,
            "payload": payload,
        }

    def _send_to_sns(self, event_type: str, event: dict, correlation_id: str) -> None:
        try:
            self.client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(event),
                MessageAttributes={"event_type": {"DataType": "String", "StringValue": event_type}},
            )
            self.logger.info(f'"Published {event_type}", "correlation_id": "{correlation_id}"')
        except Exception as error:
            self.logger.error(f'"Failed {event_type}: {error}", "correlation_id": "{correlation_id}"')