import uuid

from models import Incident, IncidentStatus
from schemas import IncidentCreate
from sqlalchemy.orm import Session


def create_incident(db: Session, data: IncidentCreate) -> Incident:
    incident = Incident(
        id=f"inc-{uuid.uuid4().hex[:8]}",
        vehicle_id=data.vehicle_id,
        description=data.description,
        severity=data.severity.value,
        status=IncidentStatus.OPEN.value,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def find_incidents(db: Session, status: IncidentStatus | None) -> list[Incident]:
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status.value)
    return query.all()


def resolve_incident(db: Session, incident_id: str) -> Incident | None:
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        return None
    incident.status = IncidentStatus.RESOLVED.value
    db.commit()
    db.refresh(incident)
    return incident