import uuid

import repository
from fastapi import Depends, Header
from models import OrderStatus
from schemas import MaintenanceCreate, MaintenanceResponse
from service import MaintenanceService
from sqlalchemy.orm import Session

from shared.app_factory import create_service_app
from shared.database import Base, engine, get_db
from shared.events import SnsEventPublisher

Base.metadata.create_all(bind=engine)
app = create_service_app("maintenance", "UrbanMove - Maintenance Service")


def get_service() -> MaintenanceService:
    return MaintenanceService(SnsEventPublisher("maintenance-service"))


@app.post("/maintenance-orders", response_model=MaintenanceResponse, status_code=201)
def create_maintenance_order(
        payload: MaintenanceCreate,
        db: Session = Depends(get_db),
        service: MaintenanceService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.create(db, payload, x_correlation_id or str(uuid.uuid4()))


@app.get("/maintenance-orders", response_model=list[MaintenanceResponse])
def list_maintenance_orders(status: OrderStatus | None = None, db: Session = Depends(get_db)):
    return repository.find_orders(db, status)


@app.patch("/maintenance-orders/{order_id}/complete", response_model=MaintenanceResponse)
def complete_maintenance_order(
        order_id: str,
        db: Session = Depends(get_db),
        service: MaintenanceService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.complete(db, order_id, x_correlation_id or str(uuid.uuid4()))