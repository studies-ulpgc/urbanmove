import uuid
import repository
from fastapi import Depends, Header
from models import VehicleStatus
from schemas import VehicleCreate, VehicleResponse, VehicleStatusUpdate
from service import InventoryService
from shared.app_factory import create_service_app
from shared.database import Base, engine, get_db
from shared.events import SnsEventPublisher
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)
app = create_service_app("inventory", "UrbanMove - Inventory Service")


def get_service() -> InventoryService:
    return InventoryService(SnsEventPublisher("inventory-service"))


@app.post("/vehicles", response_model=VehicleResponse, status_code=201)
def register_vehicle(
        payload: VehicleCreate,
        db: Session = Depends(get_db),
        service: InventoryService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.register(db, payload, x_correlation_id or str(uuid.uuid4()))


@app.get("/vehicles", response_model=list[VehicleResponse])
def list_vehicles(zone_id: str | None = None, status: VehicleStatus | None = None, db: Session = Depends(get_db)):
    return repository.find_vehicles(db, zone_id, status)


@app.patch("/vehicles/{vehicle_id}/status", response_model=VehicleResponse)
def update_status(
        vehicle_id: str,
        payload: VehicleStatusUpdate,
        db: Session = Depends(get_db),
        service: InventoryService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.update_status(db, vehicle_id, payload.status, x_correlation_id or str(uuid.uuid4()))