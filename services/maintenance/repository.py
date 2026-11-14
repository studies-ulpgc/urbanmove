import uuid
from datetime import UTC, datetime

from models import MaintenanceOrder, OrderStatus
from schemas import MaintenanceCreate
from sqlalchemy.orm import Session


def create_order(db: Session, data: MaintenanceCreate) -> MaintenanceOrder:
    order = MaintenanceOrder(
        id=f"mnt-{uuid.uuid4().hex[:8]}",
        vehicle_id=data.vehicle_id,
        order_type=data.order_type.value,
        reason=data.reason,
        status=OrderStatus.OPEN.value,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def find_orders(db: Session, status: OrderStatus | None) -> list[MaintenanceOrder]:
    query = db.query(MaintenanceOrder)
    if status:
        query = query.filter(MaintenanceOrder.status == status.value)
    return query.all()


def complete_order(db: Session, order_id: str) -> MaintenanceOrder | None:
    order = db.query(MaintenanceOrder).filter(MaintenanceOrder.id == order_id).first()
    if not order:
        return None
    order.status = OrderStatus.COMPLETED.value
    order.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(order)
    return order