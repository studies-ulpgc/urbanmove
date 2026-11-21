import uuid
from fastapi import Depends, Header
from schemas import TelemetryCreate, TelemetryResponse
from service import TelemetryService
from shared.app_factory import create_service_app
from shared.database import Base, engine, get_db
from shared.events import SnsEventPublisher
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)
app = create_service_app("telemetry", "UrbanMove - Telemetry Service")


def get_service() -> TelemetryService:
    return TelemetryService(SnsEventPublisher("telemetry-service"))


@app.post("/telemetry", response_model=TelemetryResponse, status_code=201)
def record_telemetry(
        payload: TelemetryCreate,
        db: Session = Depends(get_db),
        service: TelemetryService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.record(db, payload, x_correlation_id or str(uuid.uuid4()))


@app.get("/telemetry/{vehicle_id}", response_model=TelemetryResponse)
def get_vehicle_telemetry(
        vehicle_id: str, db: Session = Depends(get_db), service: TelemetryService = Depends(get_service)
):
    return service.get_latest(db, vehicle_id)