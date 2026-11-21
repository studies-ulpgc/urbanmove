import logging
import os

from shared.lambda_utils import (
    OrderClient,
    UrllibOrderClient,
    is_duplicate_event,
    mark_event_processed,
    parse_sqs_record,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("relocation-lambda")

RELOCATION_URL = os.getenv("RELOCATION_URL", "http://relocation-service:8006")


def lambda_handler(event: dict, context=None, client: OrderClient | None = None) -> dict:
    http_client = client or UrllibOrderClient()
    created = sum(_process_record(record, http_client) for record in event.get("Records", []))
    return {"statusCode": 200, "created": created}


def _process_record(record: dict, client: OrderClient) -> int:
    envelope = parse_sqs_record(record)
    if is_duplicate_event(envelope.get("event_id")) or envelope.get("event_type") != "DemandHotspotDetected":
        return 0
    _send_order(envelope, client)
    mark_event_processed(envelope.get("event_id"))
    return 1

def _send_order(envelope: dict, client: OrderClient) -> None:
    payload = envelope.get("payload", {})
    corr_id = envelope.get("correlation_id", "auto")
    order_data = {
        "vehicle_id": payload["vehicle_id"],
        "from_zone": payload["excess_zone"],
        "to_zone": payload["deficit_zone"],
    }
    status = client.post_order(f"{RELOCATION_URL}/relocation-orders", order_data, corr_id)
    logger.info(f'"Relocation order created: status={status}", "correlation_id": "{corr_id}"')