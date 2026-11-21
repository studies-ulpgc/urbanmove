import logging

import repository
from fastapi import HTTPException
from models import Vehicle, VehicleStatus
from schemas import VehicleCreate
from sqlalchemy.orm import Session

from shared.events import EventPublisher

logger = logging.getLogger("inventory")


class InventoryService:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher

    def register(self, db: Session, data: VehicleCreate, correlation_id: str) -> Vehicle:
        vehicle = repository.create_vehicle(db, data)
        self.publisher.publish("VehiclePurchased", self._to_event_payload(vehicle), correlation_id)
        logger.info(f'"Created {vehicle.id}", "correlation_id": "{correlation_id}"')
        return vehicle

    def update_status(self, db: Session, vehicle_id: str, status: VehicleStatus, correlation_id: str) -> Vehicle:
        vehicle = repository.find_vehicle_by_id(db, vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        logger.info(f'"Updated {vehicle_id} -> {status.value}", "correlation_id": "{correlation_id}"')
        return repository.save_status(db, vehicle, status)

    def _to_event_payload(self, vehicle: Vehicle) -> dict:
        return {
            "vehicle_id": vehicle.id,
            "vehicle_type": vehicle.vehicle_type,
            "model": vehicle.model,
            "zone_id": vehicle.zone_id,
            "status": vehicle.status,
        }