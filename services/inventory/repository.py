import uuid

from models import Vehicle, VehicleStatus
from schemas import VehicleCreate
from sqlalchemy.orm import Session


def create_vehicle(db: Session, data: VehicleCreate) -> Vehicle:
    vehicle = Vehicle(
        id=f"veh-{uuid.uuid4().hex[:8]}",
        vehicle_type=data.vehicle_type.value,
        model=data.model,
        zone_id=data.zone_id,
        status=VehicleStatus.AVAILABLE.value
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

def find_vehicles(db: Session, zone_id: str | None, status: VehicleStatus | None) -> list[Vehicle]:
    query = db.query(Vehicle)
    if zone_id:
        query = query.filter(Vehicle.zone_id == zone_id)
    if status:
        query = query.filter(Vehicle.status == status.value)
    return query.all()

def find_vehicle_by_id(db: Session, vehicle_id: str) -> Vehicle | None:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def save_status(db: Session, vehicle: Vehicle, new_status: VehicleStatus) -> Vehicle:
    vehicle.status = new_status.value
    db.commit()
    db.refresh(vehicle)
    return vehicle