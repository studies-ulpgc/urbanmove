import logging

import repository
from fastapi import HTTPException
from models import Incident
from schemas import IncidentCreate
from sqlalchemy.orm import Session

from shared.events import EventPublisher

logger = logging.getLogger("incidents")


class IncidentService:
    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher

    def report(self, db: Session, data: IncidentCreate, correlation_id: str) -> Incident:
        incident = repository.create_incident(db, data)
        self.publisher.publish("IncidentReported", self._to_event_payload(incident), correlation_id)
        logger.info(f'"Incident {incident.id} reported", "correlation_id": "{correlation_id}"')
        return incident

    def resolve(self, db: Session, incident_id: str, correlation_id: str) -> Incident:
        incident = repository.find_by_id(db, incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        logger.info(f'"Incident {incident_id} resolved", "correlation_id": "{correlation_id}"')
        return repository.mark_resolved(db, incident)

    def _to_event_payload(self, incident: Incident) -> dict:
        return {
            "incident_id": incident.id,
            "vehicle_id": incident.vehicle_id,
            "description": incident.description,
            "severity": incident.severity,
        }