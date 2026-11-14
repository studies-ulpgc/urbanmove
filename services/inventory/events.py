import json
import logging
import os
import uuid
from datetime import datetime, timezone
import boto3

logger = logging.getLogger("inventory")
AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:000000000000:urbanmove-events")

sns_client = boto3.client(
    "sns",
    endpoint_url=AWS_ENDPOINT,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

def build_event(event_type: str, payload: dict, correlation_id: str) -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "inventory-service",
        "event_type": event_type,
        "schema_version": "1.0",
        "correlation_id": correlation_id,
        "payload": payload
    }

def publish_event(event_type: str, payload: dict, correlation_id: str) -> None:
    event = build_event(event_type, payload, correlation_id)
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(event),
            MessageAttributes={"event_type": {"DataType": "String", "StringValue": event_type}}
        )
        logger.info(f'"Published {event_type}", "correlation_id": "{correlation_id}"')
    except Exception as error:
        logger.error(f'"Failed {event_type}: {error}", "correlation_id": "{correlation_id}"')