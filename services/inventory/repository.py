import uuid

from models import Vehicle, VehicleStatus
from schemas import VehicleCreate
from sqlalchemy.orm import Session


def create_vehicle(db: Session, data: VehicleCreate) -> Vehicle:
    return _persist(db, _build_entity(data))


def find_vehicles(db: Session, zone_id: str | None, status: VehicleStatus | None) -> list[Vehicle]:
    query = db.query(Vehicle)
    query = query.filter(Vehicle.zone_id == zone_id) if zone_id else query
    return query.filter(Vehicle.status == status.value).all() if status else query.all()


def find_vehicle_by_id(db: Session, vehicle_id: str) -> Vehicle | None:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def save_status(db: Session, vehicle: Vehicle, new_status: VehicleStatus) -> Vehicle:
    vehicle.status = new_status.value
    return _persist(db, vehicle)


def _build_entity(data: VehicleCreate) -> Vehicle:
    return Vehicle(
        id=f"veh-{uuid.uuid4().hex[:8]}",
        vehicle_type=data.vehicle_type.value,
        model=data.model,
        zone_id=data.zone_id,
        status=VehicleStatus.AVAILABLE.value,
    )


def _persist(db: Session, vehicle: Vehicle) -> Vehicle:
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle