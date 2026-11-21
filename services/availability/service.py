import logging
import repository
from fastapi import HTTPException
from models import VehicleAvailability
from schemas import AvailabilityRegister
from sqlalchemy.orm import Session

logger = logging.getLogger("availability")


class AvailabilityService:
    def register(self, db: Session, data: AvailabilityRegister, correlation_id: str) -> VehicleAvailability:
        record = repository.save_availability(db, data)
        logger.info(f'"Registered availability {record.vehicle_id}", "correlation_id": "{correlation_id}"')
        return record

    def lock(self, db: Session, vehicle_id: str, correlation_id: str) -> VehicleAvailability:
        record = self._get_or_404(db, vehicle_id)
        if not record.is_available:
            raise HTTPException(status_code=409, detail="Vehicle already locked")
        logger.info(f'"Locked {vehicle_id}", "correlation_id": "{correlation_id}"')
        return repository.update_status(db, record, False)

    def release(self, db: Session, vehicle_id: str, correlation_id: str) -> VehicleAvailability:
        record = self._get_or_404(db, vehicle_id)
        logger.info(f'"Released {vehicle_id}", "correlation_id": "{correlation_id}"')
        return repository.update_status(db, record, True)

    def _get_or_404(self, db: Session, vehicle_id: str) -> VehicleAvailability:
        record = repository.find_by_id(db, vehicle_id)
        if not record:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        return record