import uuid
from models import Incident, IncidentStatus
from schemas import IncidentCreate
from sqlalchemy.orm import Session


def create_incident(db: Session, data: IncidentCreate) -> Incident:
    return _persist(db, _build_entity(data))


def find_incidents(db: Session, status: IncidentStatus | None) -> list[Incident]:
    query = db.query(Incident)
    return query.filter(Incident.status == status.value).all() if status else query.all()


def find_by_id(db: Session, incident_id: str) -> Incident | None:
    return db.query(Incident).filter(Incident.id == incident_id).first()


def mark_resolved(db: Session, incident: Incident) -> Incident:
    incident.status = IncidentStatus.RESOLVED.value
    return _persist(db, incident)


def _build_entity(data: IncidentCreate) -> Incident:
    return Incident(
        id=f"inc-{uuid.uuid4().hex[:8]}",
        vehicle_id=data.vehicle_id,
        description=data.description,
        severity=data.severity.value,
        status=IncidentStatus.OPEN.value,
    )


def _persist(db: Session, incident: Incident) -> Incident:
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident