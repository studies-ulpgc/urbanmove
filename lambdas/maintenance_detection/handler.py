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
logger = logging.getLogger("maintenance-lambda")

MAINTENANCE_URL = os.getenv("MAINTENANCE_URL", "http://maintenance-service:8005")
MAX_USES_THRESHOLD = 50


def lambda_handler(event: dict, context=None, client: OrderClient | None = None) -> dict:
    http_client = client or UrllibOrderClient()
    processed = sum(_process_record(record, http_client) for record in event.get("Records", []))
    return {"statusCode": 200, "processed": processed}


def _process_record(record: dict, client: OrderClient) -> int:
    envelope = parse_sqs_record(record)
    if is_duplicate_event(envelope.get("event_id")) or not _requires_maintenance(envelope):
        return 0
    _send_order(envelope, client)
    mark_event_processed(envelope.get("event_id"))
    return 1


def _requires_maintenance(envelope: dict) -> bool:
    event_type = envelope.get("event_type", "")
    uses = envelope.get("payload", {}).get("uses_since_review", 0)
    return event_type in {"VehicleBatteryLow", "IncidentReported"} or uses >= MAX_USES_THRESHOLD


def _send_order(envelope: dict, client: OrderClient) -> None:
    order_data = _build_order_payload(envelope.get("event_type", ""), envelope.get("payload", {}))
    corr_id = envelope.get("correlation_id", "auto")
    status = client.post_order(f"{MAINTENANCE_URL}/maintenance-orders", order_data, corr_id)
    logger.info(f'"Maintenance order created: status={status}", "correlation_id": "{corr_id}"')


def _build_order_payload(event_type: str, payload: dict) -> dict:
    if event_type == "VehicleBatteryLow":
        reason = f"Low battery: {payload.get('battery_level')}%"
        return {"vehicle_id": payload["vehicle_id"], "order_type": "RECHARGE", "reason": reason}
    reason = payload.get("description", "Excessive usage")
    return {"vehicle_id": payload["vehicle_id"], "order_type": "REPAIR", "reason": reason}