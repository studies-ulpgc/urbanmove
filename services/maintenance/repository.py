import uuid
from datetime import UTC, datetime

from models import MaintenanceOrder, OrderStatus
from schemas import MaintenanceCreate
from sqlalchemy.orm import Session


def create_order(db: Session, data: MaintenanceCreate) -> MaintenanceOrder:
    return _persist(db, _build_entity(data))


def find_orders(db: Session, status: OrderStatus | None) -> list[MaintenanceOrder]:
    query = db.query(MaintenanceOrder)
    return query.filter(MaintenanceOrder.status == status.value).all() if status else query.all()


def find_by_id(db: Session, order_id: str) -> MaintenanceOrder | None:
    return db.query(MaintenanceOrder).filter(MaintenanceOrder.id == order_id).first()


def mark_completed(db: Session, order: MaintenanceOrder) -> MaintenanceOrder:
    order.status = OrderStatus.COMPLETED.value
    order.completed_at = datetime.now(UTC)
    return _persist(db, order)


def _build_entity(data: MaintenanceCreate) -> MaintenanceOrder:
    return MaintenanceOrder(
        id=f"mnt-{uuid.uuid4().hex[:8]}",
        vehicle_id=data.vehicle_id,
        order_type=data.order_type.value,
        reason=data.reason,
        status=OrderStatus.OPEN.value,
    )


def _persist(db: Session, order: MaintenanceOrder) -> MaintenanceOrder:
    db.add(order)
    db.commit()
    db.refresh(order)
    return order