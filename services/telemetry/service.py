import logging

import repository
from fastapi import HTTPException
from models import TelemetryRecord
from schemas import TelemetryCreate
from sqlalchemy.orm import Session

from shared.events import EventPublisher

logger = logging.getLogger("telemetry")
LOW_BATTERY_THRESHOLD = 20.0


class TelemetryService:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher

    def record(self, db: Session, data: TelemetryCreate, correlation_id: str) -> TelemetryRecord:
        record = repository.save_telemetry(db, data)
        self._notify_if_low_battery(record, correlation_id)
        logger.info(f'"Telemetry recorded for {record.vehicle_id}", "correlation_id": "{correlation_id}"')
        return record

    def get_latest(self, db: Session, vehicle_id: str) -> TelemetryRecord:
        record = repository.find_latest_by_vehicle(db, vehicle_id)
        if not record:
            raise HTTPException(status_code=404, detail="Telemetry not found")
        return record

    def _notify_if_low_battery(self, record: TelemetryRecord, correlation_id: str) -> None:
        if record.battery_level < LOW_BATTERY_THRESHOLD:
            self.publisher.publish("VehicleBatteryLow", self._to_event_payload(record), correlation_id)

    def _to_event_payload(self, record: TelemetryRecord) -> dict:
        return {
            "vehicle_id": record.vehicle_id,
            "battery_level": record.battery_level,
            "uses_since_review": record.uses_since_review,
        }