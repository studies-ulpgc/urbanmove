import json
import logging
import urllib.request
from abc import ABC, abstractmethod

logger = logging.getLogger("lambda-shared")
PROCESSED_IDS: set[str] = set()


class OrderClient(ABC):
    @abstractmethod
    def post_order(self, url: str, payload: dict, correlation_id: str) -> int:
        pass


class UrllibOrderClient(OrderClient):
    def post_order(self, url: str, payload: dict, correlation_id: str) -> int:
        req = self._build_request(url, payload, correlation_id)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status

    def _build_request(self, url: str, payload: dict, correlation_id: str) -> urllib.request.Request:
        headers = {"Content-Type": "application/json", "x-correlation-id": correlation_id}
        return urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")


def parse_sqs_record(record: dict) -> dict:
    body = json.loads(record["body"])
    return json.loads(body["Message"]) if "Message" in body else body


def is_duplicate_event(event_id: str | None) -> bool:
    if not event_id or event_id not in PROCESSED_IDS:
        return False
    logger.warning(f'"Duplicate event skipped: {event_id}"')
    return True


def mark_event_processed(event_id: str | None) -> None:
    if event_id:
        PROCESSED_IDS.add(event_id)