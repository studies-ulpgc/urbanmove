import logging
import uuid

import repository
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, Header, HTTPException
from schemas import AvailabilityRegister, AvailabilityResponse
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "service": "availability", "level": "%(levelname)s", "message": %(message)s}',
)
logger = logging.getLogger("availability")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="UrbanMove - Availability Service", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "availability"}


@app.post("/availability", response_model=AvailabilityResponse, status_code=201)
def register_availability(
    payload: AvailabilityRegister,
    db: Session = Depends(get_db),
    x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    record = repository.upsert_availability(db, payload)
    logger.info(f'"Registered availability {record.vehicle_id}", "correlation_id": "{corr_id}"')
    return record


@app.get("/availability", response_model=list[AvailabilityResponse])
def list_available(
    zone_id: str | None = None,
    vehicle_type: str | None = None,
    db: Session = Depends(get_db),
):
    return repository.find_available(db, zone_id, vehicle_type)


@app.post("/availability/{vehicle_id}/lock", response_model=AvailabilityResponse)
def lock_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    record = repository.set_availability(db, vehicle_id, False)
    if not record:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    logger.info(f'"Locked {vehicle_id}", "correlation_id": "{corr_id}"')
    return record


@app.post("/availability/{vehicle_id}/release", response_model=AvailabilityResponse)
def release_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    record = repository.set_availability(db, vehicle_id, True)
    if not record:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    logger.info(f'"Released {vehicle_id}", "correlation_id": "{corr_id}"')
    return record
