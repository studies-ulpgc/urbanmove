import uuid

import repository
from fastapi import Depends, Header
from schemas import AvailabilityRegister, AvailabilityResponse
from service import AvailabilityService
from sqlalchemy.orm import Session

from shared.app_factory import create_service_app
from shared.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)
app = create_service_app("availability", "UrbanMove - Availability Service")
service = AvailabilityService()


@app.post("/availability", response_model=AvailabilityResponse, status_code=201)
def register_availability(
        payload: AvailabilityRegister,
        db: Session = Depends(get_db),
        x_correlation_id: str | None = Header(default=None),
):
    return service.register(db, payload, x_correlation_id or str(uuid.uuid4()))


@app.get("/availability", response_model=list[AvailabilityResponse])
def list_available(zone_id: str | None = None, vehicle_type: str | None = None, db: Session = Depends(get_db)):
    return repository.find_available(db, zone_id, vehicle_type)


@app.post("/availability/{vehicle_id}/lock", response_model=AvailabilityResponse)
def lock_vehicle(vehicle_id: str, db: Session = Depends(get_db), x_correlation_id: str | None = Header(default=None)):
    return service.lock(db, vehicle_id, x_correlation_id or str(uuid.uuid4()))


@app.post("/availability/{vehicle_id}/release", response_model=AvailabilityResponse)
def release_vehicle(
        vehicle_id: str, db: Session = Depends(get_db), x_correlation_id: str | None = Header(default=None)
):
    return service.release(db, vehicle_id, x_correlation_id or str(uuid.uuid4()))