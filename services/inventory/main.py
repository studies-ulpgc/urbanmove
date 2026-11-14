import logging
import uuid
from typing import List, Optional
from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.orm import Session
import repository
from database import Base, engine, get_db
from events import publish_event
from models import VehicleStatus
from schemas import VehicleCreate, VehicleResponse, VehicleStatusUpdate

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "service": "inventory", "level": "%(levelname)s", "message": %(message)s}'
)
logger = logging.getLogger("inventory")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="UrbanMove - Inventory Service", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "inventory"}

@app.post("/vehicles", response_model=VehicleResponse, status_code=201)
def register_vehicle(
        payload: VehicleCreate,
        db: Session = Depends(get_db),
        x_correlation_id: Optional[str] = Header(default=None)
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    vehicle = repository.create_vehicle(db, payload)
    publish_event("VehiclePurchased", _vehicle_payload(vehicle), corr_id)
    logger.info(f'"Created {vehicle.id}", "correlation_id": "{corr_id}"')
    return vehicle

@app.get("/vehicles", response_model=List[VehicleResponse])
def list_vehicles(
        zone_id: Optional[str] = None,
        status: Optional[VehicleStatus] = None,
        db: Session = Depends(get_db)
):
    return repository.find_vehicles(db, zone_id, status)

@app.patch("/vehicles/{vehicle_id}/status", response_model=VehicleResponse)
def update_status(
        vehicle_id: str,
        payload: VehicleStatusUpdate,
        db: Session = Depends(get_db),
        x_correlation_id: Optional[str] = Header(default=None)
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    vehicle = repository.find_vehicle_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    updated = repository.save_status(db, vehicle, payload.status)
    logger.info(f'"Updated {vehicle_id} -> {updated.status}", "correlation_id": "{corr_id}"')
    return updated

def _vehicle_payload(vehicle) -> dict:
    return {
        "vehicle_id": vehicle.id,
        "vehicle_type": vehicle.vehicle_type,
        "model": vehicle.model,
        "zone_id": vehicle.zone_id,
        "status": vehicle.status
    }