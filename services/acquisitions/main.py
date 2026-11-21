import uuid
import repository
from fastapi import Depends, Header
from gateway import HttpInventoryGateway
from schemas import AcquisitionCreate, AcquisitionResponse
from service import AcquisitionService
from shared.app_factory import create_service_app
from shared.database import Base, engine, get_db
from shared.events import SnsEventPublisher
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)
app = create_service_app("acquisitions", "UrbanMove - Acquisitions Service")


def get_service() -> AcquisitionService:
    return AcquisitionService(HttpInventoryGateway(), SnsEventPublisher("acquisitions-service"))


@app.post("/acquisitions", response_model=AcquisitionResponse, status_code=201)
def register_acquisition(
        payload: AcquisitionCreate,
        db: Session = Depends(get_db),
        service: AcquisitionService = Depends(get_service),
        x_correlation_id: str | None = Header(default=None),
):
    return service.register(db, payload, x_correlation_id or str(uuid.uuid4()))


@app.get("/acquisitions", response_model=list[AcquisitionResponse])
def list_acquisitions(db: Session = Depends(get_db)):
    return repository.find_acquisitions(db)