from datetime import UTC, datetime

from models import VehicleAvailability
from schemas import AvailabilityRegister
from sqlalchemy.orm import Session


def upsert_availability(db: Session, data: AvailabilityRegister) -> VehicleAvailability:
    record = db.query(VehicleAvailability).filter(VehicleAvailability.vehicle_id == data.vehicle_id).first()
    if record:
        record.zone_id = data.zone_id
        record.is_available = True
        record.updated_at = datetime.now(UTC)
    else:
        record = VehicleAvailability(
            vehicle_id=data.vehicle_id,
            vehicle_type=data.vehicle_type,
            zone_id=data.zone_id,
            is_available=True,
        )
        db.add(record)
    db.commit()
    db.refresh(record)
    return record


def find_available(db: Session, zone_id: str | None, vehicle_type: str | None) -> list[VehicleAvailability]:
    query = db.query(VehicleAvailability).filter(VehicleAvailability.is_available.is_(True))
    if zone_id:
        query = query.filter(VehicleAvailability.zone_id == zone_id)
    if vehicle_type:
        query = query.filter(VehicleAvailability.vehicle_type == vehicle_type)
    return query.all()


def set_availability(db: Session, vehicle_id: str, available: bool) -> VehicleAvailability | None:
    record = db.query(VehicleAvailability).filter(VehicleAvailability.vehicle_id == vehicle_id).first()
    if not record:
        return None
    record.is_available = available
    record.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(record)
    return record