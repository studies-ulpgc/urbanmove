import uuid

import repository
from fastapi import Depends, Header
from models import RelocationStatus
from schemas import RelocationCreate, RelocationResponse, RelocationStatusUpdate
from service import RelocationService
from sqlalchemy.orm import Session

from shared.app_factory import create_service_app
from shared.database import Base, engine, get_db
from shared.events import SnsEventPublisher

Base.metadata.create_all(bind=engine)
app = create_service_app("relocation", "UrbanMove - Relocation Service")


def get_service() -> RelocationService:
    return RelocationService(SnsEventPublisher("relocation-service"))


@app.post("/relocation-orders", response_model=RelocationResponse, status_code=201)
def create_relocation_order(
        payload: RelocationCreate,
        db: Session = Depends(get_db),
        service: RelocationService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.create(db, payload, x_correlation_id or str(uuid.uuid4()))


@app.get("/relocation-orders", response_model=list[RelocationResponse])
def list_relocation_orders(status: RelocationStatus | None = None, db: Session = Depends(get_db)):
    return repository.find_orders(db, status)


@app.patch("/relocation-orders/{order_id}/status", response_model=RelocationResponse)
def update_relocation_status(
        order_id: str,
        payload: RelocationStatusUpdate,
        db: Session = Depends(get_db),
        service: RelocationService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.update_status(db, order_id, payload.status, x_correlation_id or str(uuid.uuid4()))