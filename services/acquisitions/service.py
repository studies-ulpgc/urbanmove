import logging
import repository
from gateway import InventoryGateway
from models import Acquisition
from schemas import AcquisitionCreate
from shared.events import EventPublisher
from sqlalchemy.orm import Session

logger = logging.getLogger("acquisitions")


class AcquisitionService:
    def __init__(self, inventory: InventoryGateway, publisher: EventPublisher):
        self.inventory = inventory
        self.publisher = publisher

    def register(self, db: Session, data: AcquisitionCreate, correlation_id: str) -> Acquisition:
        record = repository.create_acquisition(db, data)
        self.inventory.register_vehicles(data, correlation_id)
        self.publisher.publish("VehiclePurchased", self._to_event_payload(record), correlation_id)
        logger.info(f'"Acquisition {record.id} registered", "correlation_id": "{correlation_id}"')
        return record

    def _to_event_payload(self, record: Acquisition) -> dict:
        return {
            "acquisition_id": record.id,
            "vehicle_type": record.vehicle_type,
            "model": record.model,
            "zone_id": record.zone_id,
            "quantity": record.quantity,
            "total_cost": record.quantity * record.unit_cost,
        }