import logging
import uuid

import repository
from database import Base, engine, get_db
from events import publish_event
from fastapi import Depends, FastAPI, Header, HTTPException
from models import RelocationStatus
from schemas import RelocationCreate, RelocationResponse, RelocationStatusUpdate
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "service": "relocation", "level": "%(levelname)s", "message": %(message)s}',
)
logger = logging.getLogger("relocation")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="UrbanMove - Relocation Service", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "relocation"}


@app.post("/relocation-orders", response_model=RelocationResponse, status_code=201)
def create_relocation_order(
    payload: RelocationCreate,
    db: Session = Depends(get_db),
    x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    order = repository.create_order(db, payload)
    publish_event("RelocationOrderCreated", _order_payload(order), corr_id)
    logger.info(f'"Relocation order {order.id} created", "correlation_id": "{corr_id}"')
    return order


@app.get("/relocation-orders", response_model=list[RelocationResponse])
def list_relocation_orders(status: RelocationStatus | None = None, db: Session = Depends(get_db)):
    return repository.find_orders(db, status)


@app.patch("/relocation-orders/{order_id}/status", response_model=RelocationResponse)
def update_relocation_status(
    order_id: str,
    payload: RelocationStatusUpdate,
    db: Session = Depends(get_db),
    x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    order = repository.update_status(db, order_id, payload.status)
    if not order:
        raise HTTPException(status_code=404, detail="Relocation order not found")
    if order.status == RelocationStatus.COMPLETED.value:
        publish_event("RelocationOrderCompleted", _order_payload(order), corr_id)
    logger.info(f'"Relocation {order_id} -> {order.status}", "correlation_id": "{corr_id}"')
    return order


def _order_payload(order) -> dict:
    return {
        "order_id": order.id,
        "vehicle_id": order.vehicle_id,
        "from_zone": order.from_zone,
        "to_zone": order.to_zone,
        "status": order.status,
    }
