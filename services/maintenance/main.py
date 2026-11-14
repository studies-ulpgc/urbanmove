import logging
import uuid

import repository
from database import Base, engine, get_db
from events import publish_event
from fastapi import Depends, FastAPI, Header, HTTPException
from models import OrderStatus
from schemas import MaintenanceCreate, MaintenanceResponse
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "service": "maintenance", "level": "%(levelname)s", "message": %(message)s}',
)
logger = logging.getLogger("maintenance")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="UrbanMove - Maintenance Service", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "maintenance"}


@app.post("/maintenance-orders", response_model=MaintenanceResponse, status_code=201)
def create_maintenance_order(
        payload: MaintenanceCreate,
        db: Session = Depends(get_db),
        x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    order = repository.create_order(db, payload)
    publish_event("VehicleWithdrawnForMaintenance", _order_payload(order), corr_id)
    logger.info(f'"Maintenance order {order.id} created", "correlation_id": "{corr_id}"')
    return order


@app.get("/maintenance-orders", response_model=list[MaintenanceResponse])
def list_maintenance_orders(status: OrderStatus | None = None, db: Session = Depends(get_db)):
    return repository.find_orders(db, status)


@app.patch("/maintenance-orders/{order_id}/complete", response_model=MaintenanceResponse)
def complete_maintenance_order(
        order_id: str,
        db: Session = Depends(get_db),
        x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    order = repository.complete_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Maintenance order not found")
    publish_event("VehicleReturnedToService", _order_payload(order), corr_id)
    logger.info(f'"Maintenance order {order_id} completed", "correlation_id": "{corr_id}"')
    return order


def _order_payload(order) -> dict:
    return {
        "order_id": order.id,
        "vehicle_id": order.vehicle_id,
        "order_type": order.order_type,
        "reason": order.reason,
        "status": order.status,
    }