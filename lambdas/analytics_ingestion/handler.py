import logging
import boto3
import uuid
import json
import os
from shared.lambda_utils import parse_sqs_record
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import quote



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analytics-ingestion")
logger.setLevel(logging.INFO)

DATALAKE_BUCKET = os.getenv("DATALAKE_BUCKET", "urbanmove-datalake")
REQUIRED_STRING_FIELDS = (
    "event_id",
    "timestamp",
    "source",
    "event_type",
    "schema_version",
    "correlation_id",
)


def lambda_handler(event: dict, context=None, client=None) -> dict:
    s3 = client or _get_s3_client()
    processed = 0
    failures = []
    for record in event.get("Records", []):
        try:
            processed += _process_record(record, s3)
        except Exception:
            logger.exception("Transient error processing message %s", record.get("messageId"))
            failures.append({"itemIdentifier": record["messageId"]})
    logger.info("Raw events stored: %s, failed: %s", processed, len(failures))
    return {"statusCode": 200, "processed": processed, "batchItemFailures": failures}


def _process_record(record: dict, s3) -> int:
    try:
        envelope = parse_sqs_record(record)
        _validate_event(envelope)
    except (ValueError, KeyError, TypeError) as exc:
        _save_rejected(record, str(exc), s3)
        return 0
    _save_to_raw(record, envelope, s3)
    return 1


@lru_cache(maxsize=1)
def _get_s3_client():
    endpoint = os.getenv("AWS_ENDPOINT_URL")
    return boto3.client("s3", endpoint_url=endpoint) if endpoint else boto3.client("s3")


def _validate_event(envelope: dict) -> None:
    if not isinstance(envelope, dict):
        raise ValueError("El evento debe ser un objeto JSON")

    errors = [
        f"{field}: obligatorio y debe ser texto no vacío"
        for field in REQUIRED_STRING_FIELDS
        if not isinstance(envelope.get(field), str) or not envelope[field].strip()
    ]
    if not isinstance(envelope.get("payload"), dict):
        errors.append("payload: obligatorio y debe ser un objeto JSON")

    if not errors:
        errors.extend(_validate_formats(envelope))
    if errors:
        raise ValueError("; ".join(errors))


def _validate_formats(envelope: dict) -> list[str]:
    errors = []
    try:
        uuid.UUID(envelope["event_id"])
    except ValueError:
        errors.append("event_id: debe ser un UUID")
    try:
        ts = datetime.fromisoformat(envelope["timestamp"].replace("Z", "+00:00"))
        if ts.tzinfo is None:
            errors.append("timestamp: debe incluir zona horaria")
    except ValueError:
        errors.append("timestamp: no es ISO 8601 válido")
    return errors


def _safe_path(value) -> str:
    return quote(str(value), safe="-_.")


def _put_json(s3, key: str, body: dict) -> None:
    s3.put_object(
        Bucket=DATALAKE_BUCKET,
        Key=key,
        Body=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )


def _save_to_raw(record: dict, envelope: dict, s3) -> None:
    now = datetime.now(timezone.utc)
    key = (
        f"raw/year={now:%Y}/month={now:%m}/day={now:%d}/"
        f"event_type={_safe_path(envelope['event_type'])}/"
        f"source={_safe_path(envelope['source'])}/"
        f"{_safe_path(envelope['event_id'])}.json"
    )
    _put_json(s3, key, {
        "metadata": {
            "sqs_message_id": record["messageId"],
            "ingested_at": now.isoformat(),
            "source_queue": record["eventSourceARN"].split(":")[-1],
        },
        "data": envelope,
    })
    logger.info("Event stored in raw: %s, correlation_id=%s", key, envelope["correlation_id"])


def _save_rejected(record: dict, reason: str, s3) -> None:
    now = datetime.now(timezone.utc)
    key = (
        f"rejected/year={now:%Y}/month={now:%m}/day={now:%d}/"
        f"{_safe_path(record['messageId'])}.json"
    )
    _put_json(s3, key, {
        "message_id": record["messageId"],
        "rejected_at": now.isoformat(),
        "reason": reason,
        "original_body": record["body"],
    })
    logger.warning("Event rejected: %s (%s)", key, reason)