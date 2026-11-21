import uuid
from datetime import UTC, datetime
from models import RelocationOrder, RelocationStatus
from schemas import RelocationCreate
from sqlalchemy.orm import Session


def create_order(db: Session, data: RelocationCreate) -> RelocationOrder:
    return _persist(db, _build_entity(data))


def find_orders(db: Session, status: RelocationStatus | None) -> list[RelocationOrder]:
    query = db.query(RelocationOrder)
    return query.filter(RelocationOrder.status == status.value).all() if status else query.all()


def find_by_id(db: Session, order_id: str) -> RelocationOrder | None:
    return db.query(RelocationOrder).filter(RelocationOrder.id == order_id).first()


def save_status(db: Session, order: RelocationOrder, status: RelocationStatus) -> RelocationOrder:
    order.status = status.value
    order.completed_at = datetime.now(UTC) if status == RelocationStatus.COMPLETED else order.completed_at
    return _persist(db, order)


def _build_entity(data: RelocationCreate) -> RelocationOrder:
    return RelocationOrder(
        id=f"rel-{uuid.uuid4().hex[:8]}",
        vehicle_id=data.vehicle_id,
        from_zone=data.from_zone,
        to_zone=data.to_zone,
        status=RelocationStatus.PENDING.value,
    )


def _persist(db: Session, order: RelocationOrder) -> RelocationOrder:
    db.add(order)
    db.commit()
    db.refresh(order)
    return order