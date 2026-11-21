import uuid
import repository
from fastapi import Depends, Header
from models import IncidentStatus
from schemas import IncidentCreate, IncidentResponse
from service import IncidentService
from shared.app_factory import create_service_app
from shared.database import Base, engine, get_db
from shared.events import SnsEventPublisher
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)
app = create_service_app("incidents", "UrbanMove - Incidents Service")


def get_service() -> IncidentService:
    return IncidentService(SnsEventPublisher("incidents-service"))


@app.post("/incidents", response_model=IncidentResponse, status_code=201)
def report_incident(
        payload: IncidentCreate,
        db: Session = Depends(get_db),
        service: IncidentService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.report(db, payload, x_correlation_id or str(uuid.uuid4()))


@app.get("/incidents", response_model=list[IncidentResponse])
def list_incidents(status: IncidentStatus | None = None, db: Session = Depends(get_db)):
    return repository.find_incidents(db, status)


@app.patch("/incidents/{incident_id}/resolve", response_model=IncidentResponse)
def resolve_incident(
        incident_id: str,
        db: Session = Depends(get_db),
        service: IncidentService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.resolve(db, incident_id, x_correlation_id or str(uuid.uuid4()))