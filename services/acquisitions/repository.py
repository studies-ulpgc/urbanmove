import uuid

from models import Acquisition
from schemas import AcquisitionCreate
from sqlalchemy.orm import Session


def create_acquisition(db: Session, data: AcquisitionCreate) -> Acquisition:
    record = Acquisition(
        id=f"acq-{uuid.uuid4().hex[:8]}",
        vehicle_type=data.vehicle_type,
        model=data.model,
        zone_id=data.zone_id,
        quantity=data.quantity,
        unit_cost=data.unit_cost,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def find_acquisitions(db: Session) -> list[Acquisition]:
    return db.query(Acquisition).all()
