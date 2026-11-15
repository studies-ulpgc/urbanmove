import logging
import uuid

import repository
from database import Base, engine, get_db
from events import publish_event
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import IncidentStatus
from schemas import IncidentCreate, IncidentResponse
from sqlalchemy.orm import Session

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "service": "incidents", "level": "%(levelname)s", "message": %(message)s}',
)
logger = logging.getLogger("incidents")

Base.metadata.create_all(bind=engine)
app = FastAPI(title="UrbanMove - Incidents Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "incidents"}


@app.post("/incidents", response_model=IncidentResponse, status_code=201)
def report_incident(
    payload: IncidentCreate,
    db: Session = Depends(get_db),
    x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    incident = repository.create_incident(db, payload)
    publish_event("IncidentReported", _incident_payload(incident), corr_id)
    logger.info(f'"Incident {incident.id} reported", "correlation_id": "{corr_id}"')
    return incident


@app.get("/incidents", response_model=list[IncidentResponse])
def list_incidents(status: IncidentStatus | None = None, db: Session = Depends(get_db)):
    return repository.find_incidents(db, status)


@app.patch("/incidents/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    x_correlation_id: str | None = Header(default=None),
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    incident = repository.resolve_incident(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    logger.info(f'"Incident {incident_id} resolved", "correlation_id": "{corr_id}"')
    return incident


def _incident_payload(incident) -> dict:
    return {
        "incident_id": incident.id,
        "vehicle_id": incident.vehicle_id,
        "description": incident.description,
        "severity": incident.severity,
    }
