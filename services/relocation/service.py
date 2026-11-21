import logging
import repository
from fastapi import HTTPException
from models import RelocationOrder, RelocationStatus
from schemas import RelocationCreate
from shared.events import EventPublisher
from sqlalchemy.orm import Session

logger = logging.getLogger("relocation")


class RelocationService:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher

    def create(self, db: Session, data: RelocationCreate, correlation_id: str) -> RelocationOrder:
        order = repository.create_order(db, data)
        self.publisher.publish("RelocationOrderCreated", self._to_event_payload(order), correlation_id)
        logger.info(f'"Relocation order {order.id} created", "correlation_id": "{correlation_id}"')
        return order

    def update_status(
            self, db: Session, order_id: str, status: RelocationStatus, correlation_id: str
    ) -> RelocationOrder:
        order = repository.find_by_id(db, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Relocation order not found")
        updated = repository.save_status(db, order, status)
        self._notify_if_completed(updated, correlation_id)
        return updated

    def _notify_if_completed(self, order: RelocationOrder, correlation_id: str) -> None:
        if order.status == RelocationStatus.COMPLETED.value:
            self.publisher.publish("RelocationOrderCompleted", self._to_event_payload(order), correlation_id)
        logger.info(f'"Relocation {order.id} -> {order.status}", "correlation_id": "{correlation_id}"')

    def _to_event_payload(self, order: RelocationOrder) -> dict:
        return {
            "order_id": order.id,
            "vehicle_id": order.vehicle_id,
            "from_zone": order.from_zone,
            "to_zone": order.to_zone,
            "status": order.status,
        }