import uuid

from models import TelemetryRecord
from schemas import TelemetryCreate
from sqlalchemy.orm import Session


def save_telemetry(db: Session, data: TelemetryCreate) -> TelemetryRecord:
    record = TelemetryRecord(
        id=f"tel-{uuid.uuid4().hex[:8]}",
        vehicle_id=data.vehicle_id,
        battery_level=data.battery_level,
        latitude=data.latitude,
        longitude=data.longitude,
        uses_since_review=data.uses_since_review,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def find_latest_by_vehicle(db: Session, vehicle_id: str) -> TelemetryRecord | None:
    return (
        db.query(TelemetryRecord)
        .filter(TelemetryRecord.vehicle_id == vehicle_id)
        .order_by(TelemetryRecord.recorded_at.desc())
        .first()
    )