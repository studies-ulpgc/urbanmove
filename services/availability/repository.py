from datetime import UTC, datetime

from models import VehicleAvailability
from schemas import AvailabilityRegister
from sqlalchemy.orm import Session


def find_by_id(db: Session, vehicle_id: str) -> VehicleAvailability | None:
    return db.query(VehicleAvailability).filter(VehicleAvailability.vehicle_id == vehicle_id).first()


def find_available(db: Session, zone_id: str | None, vehicle_type: str | None) -> list[VehicleAvailability]:
    query = db.query(VehicleAvailability).filter(VehicleAvailability.is_available.is_(True))
    query = query.filter(VehicleAvailability.zone_id == zone_id) if zone_id else query
    return query.filter(VehicleAvailability.vehicle_type == vehicle_type).all() if vehicle_type else query.all()


def save_availability(db: Session, data: AvailabilityRegister) -> VehicleAvailability:
    existing = find_by_id(db, data.vehicle_id)
    record = _update_entity(existing, data) if existing else _build_entity(data)
    return _persist(db, record)


def update_status(db: Session, record: VehicleAvailability, available: bool) -> VehicleAvailability:
    record.is_available = available
    record.updated_at = datetime.now(UTC)
    return _persist(db, record)


def _update_entity(record: VehicleAvailability, data: AvailabilityRegister) -> VehicleAvailability:
    record.zone_id = data.zone_id
    record.is_available = True
    record.updated_at = datetime.now(UTC)
    return record


def _build_entity(data: AvailabilityRegister) -> VehicleAvailability:
    return VehicleAvailability(
        vehicle_id=data.vehicle_id, vehicle_type=data.vehicle_type, zone_id=data.zone_id, is_available=True
    )


def _persist(db: Session, record: VehicleAvailability) -> VehicleAvailability:
    db.add(record)
    db.commit()
    db.refresh(record)
    return record