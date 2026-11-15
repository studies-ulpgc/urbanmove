import json
import logging
import os
import urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("maintenance-lambda")

MAINTENANCE_URL = os.getenv("MAINTENANCE_URL", "http://localhost:8005")
MAX_USES_THRESHOLD = 50


def lambda_handler(event: dict, context=None) -> dict:
    processed = 0
    for record in event.get("Records", []):
        envelope = _parse_record(record)
        if _requires_maintenance(envelope):
            _create_maintenance_order(envelope)
            processed += 1
    return {"statusCode": 200, "processed": processed}


def _parse_record(record: dict) -> dict:
    body = json.loads(record["body"])
    if "Message" in body:
        return json.loads(body["Message"])
    return body


def _requires_maintenance(envelope: dict) -> bool:
    event_type = envelope.get("event_type", "")
    payload = envelope.get("payload", {})
    if event_type in {"VehicleBatteryLow", "IncidentReported"}:
        return True
    return payload.get("uses_since_review", 0) >= MAX_USES_THRESHOLD


def _create_maintenance_order(envelope: dict) -> None:
    payload = envelope.get("payload", {})
    order_data = _build_order_payload(envelope.get("event_type", ""), payload)
    req = urllib.request.Request(
        f"{MAINTENANCE_URL}/maintenance-orders",
        data=json.dumps(order_data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-correlation-id": envelope.get("correlation_id", "lambda-auto"),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        logger.info(f"Maintenance order created: status={resp.status}")


def _build_order_payload(event_type: str, payload: dict) -> dict:
    if event_type == "VehicleBatteryLow":
        return {
            "vehicle_id": payload["vehicle_id"],
            "order_type": "RECHARGE",
            "reason": f"Low battery detected: {payload.get('battery_level')}%",
        }
    return {
        "vehicle_id": payload["vehicle_id"],
        "order_type": "REPAIR",
        "reason": payload.get("description", "Excessive usage threshold reached"),
    }