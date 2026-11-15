import uuid
from datetime import UTC, datetime

from models import RelocationOrder, RelocationStatus
from schemas import RelocationCreate
from sqlalchemy.orm import Session


def create_order(db: Session, data: RelocationCreate) -> RelocationOrder:
    order = RelocationOrder(
        id=f"rel-{uuid.uuid4().hex[:8]}",
        vehicle_id=data.vehicle_id,
        from_zone=data.from_zone,
        to_zone=data.to_zone,
        status=RelocationStatus.PENDING.value,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def find_orders(db: Session, status: RelocationStatus | None) -> list[RelocationOrder]:
    query = db.query(RelocationOrder)
    if status:
        query = query.filter(RelocationOrder.status == status.value)
    return query.all()


def update_status(db: Session, order_id: str, status: RelocationStatus) -> RelocationOrder | None:
    order = db.query(RelocationOrder).filter(RelocationOrder.id == order_id).first()
    if not order:
        return None
    order.status = status.value
    if status == RelocationStatus.COMPLETED:
        order.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(order)
    return order
