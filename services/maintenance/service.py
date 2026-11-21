import logging
import repository
from fastapi import HTTPException
from models import MaintenanceOrder
from schemas import MaintenanceCreate
from shared.events import EventPublisher
from sqlalchemy.orm import Session

logger = logging.getLogger("maintenance")


class MaintenanceService:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher

    def create(self, db: Session, data: MaintenanceCreate, correlation_id: str) -> MaintenanceOrder:
        order = repository.create_order(db, data)
        self.publisher.publish("VehicleWithdrawnForMaintenance", self._to_event_payload(order), correlation_id)
        logger.info(f'"Maintenance order {order.id} created", "correlation_id": "{correlation_id}"')
        return order

    def complete(self, db: Session, order_id: str, correlation_id: str) -> MaintenanceOrder:
        order = repository.find_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Maintenance order not found")
        updated = repository.mark_completed(db, order)
        self.publisher.publish("VehicleReturnedToService", self._to_event_payload(updated), correlation_id)
        logger.info(f'"Maintenance order {order_id} completed", "correlation_id": "{correlation_id}"')
        return updated

    def _to_event_payload(self, order: MaintenanceOrder) -> dict:
        return {
            "order_id": order.id,
            "vehicle_id": order.vehicle_id,
            "order_type": order.order_type,
            "reason": order.reason,
            "status": order.status,
        }