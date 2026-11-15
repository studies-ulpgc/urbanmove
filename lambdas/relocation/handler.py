import json
import logging
import os
import urllib.request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("relocation-lambda")

RELOCATION_URL = os.getenv("RELOCATION_URL", "http://localhost:8006")


def lambda_handler(event: dict, context=None) -> dict:
    created = 0
    for record in event.get("Records", []):
        envelope = _parse_record(record)
        if envelope.get("event_type") == "DemandHotspotDetected":
            _create_relocation_order(envelope)
            created += 1
    return {"statusCode": 200, "created": created}


def _parse_record(record: dict) -> dict:
    body = json.loads(record["body"])
    if "Message" in body:
        return json.loads(body["Message"])
    return body


def _create_relocation_order(envelope: dict) -> None:
    payload = envelope.get("payload", {})
    order_data = {
        "vehicle_id": payload["vehicle_id"],
        "from_zone": payload["excess_zone"],
        "to_zone": payload["deficit_zone"],
    }
    req = urllib.request.Request(
        f"{RELOCATION_URL}/relocation-orders",
        data=json.dumps(order_data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-correlation-id": envelope.get("correlation_id", "relocation-auto"),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        logger.info(f"Relocation order created: status={resp.status}")