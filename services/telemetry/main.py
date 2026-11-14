import logging
import uuid

import repository
from database import Base, engine, get_db
from events import publish_event
from fastapi import Depends, FastAPI, Header, HTTPException
from schemas import TelemetryCreate, TelemetryResponse
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "service": "telemetry", "level": "%(levelname)s", "message": %(message)s}',
)
logger = logging.getLogger("telemetry")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="UrbanMove - Telemetry Service", version="1.0.0")
LOW_BATTERY_THRESHOLD = 20.0


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "telemetry"}


@app.post("/telemetry", response_model=TelemetryResponse, status_code=201)
def record_telemetry(
        payload: TelemetryCreate,
        db: Session = Depends(get_db),
        x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    record = repository.save_telemetry(db, payload)
    if record.battery_level < LOW_BATTERY_THRESHOLD:
        publish_event("VehicleBatteryLow", _battery_payload(record), corr_id)
    logger.info(f'"Telemetry recorded for {record.vehicle_id}", "correlation_id": "{corr_id}"')
    return record


@app.get("/telemetry/{vehicle_id}", response_model=TelemetryResponse)
def get_vehicle_telemetry(vehicle_id: str, db: Session = Depends(get_db)):
    record = repository.find_latest_by_vehicle(db, vehicle_id)
    if not record:
        raise HTTPException(status_code=404, detail="Telemetry not found")
    return record


def _battery_payload(record) -> dict:
    return {
        "vehicle_id": record.vehicle_id,
        "battery_level": record.battery_level,
        "uses_since_review": record.uses_since_review,
    }