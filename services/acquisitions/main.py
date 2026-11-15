import logging
import os
import uuid

import httpx
import repository
from database import Base, engine, get_db
from events import publish_event
from fastapi import Depends, FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from schemas import AcquisitionCreate, AcquisitionResponse
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "service": "acquisitions", "level": "%(levelname)s", "message": %(message)s}',
)
logger = logging.getLogger("acquisitions")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="UrbanMove - Acquisitions Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory-service:8001")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "acquisitions"}


@app.post("/acquisitions", response_model=AcquisitionResponse, status_code=201)
def register_acquisition(
    payload: AcquisitionCreate,
    db: Session = Depends(get_db),
    x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    record = repository.create_acquisition(db, payload)
    _notify_inventory(payload, corr_id)
    publish_event("VehiclePurchased", _acquisition_payload(record), corr_id)
    logger.info(f'"Acquisition {record.id} registered", "correlation_id": "{corr_id}"')
    return record


@app.get("/acquisitions", response_model=list[AcquisitionResponse])
def list_acquisitions(db: Session = Depends(get_db)):
    return repository.find_acquisitions(db)


def _notify_inventory(payload: AcquisitionCreate, corr_id: str) -> None:
    vehicle_data = {"vehicle_type": payload.vehicle_type, "model": payload.model, "zone_id": payload.zone_id}
    try:
        for _ in range(payload.quantity):
            httpx.post(
                f"{INVENTORY_URL}/vehicles", json=vehicle_data, headers={"x-correlation-id": corr_id}, timeout=2.0
            )
    except Exception as error:
        logger.warning(f'"Inventory sync skipped: {error}", "correlation_id": "{corr_id}"')


def _acquisition_payload(record) -> dict:
    return {
        "acquisition_id": record.id,
        "vehicle_type": record.vehicle_type,
        "model": record.model,
        "zone_id": record.zone_id,
        "quantity": record.quantity,
        "total_cost": record.quantity * record.unit_cost,
    }
