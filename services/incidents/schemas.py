from datetime import datetime

from models import IncidentSeverity
from pydantic import BaseModel, ConfigDict


class IncidentCreate(BaseModel):
    vehicle_id: str
    description: str
    severity: IncidentSeverity = IncidentSeverity.MEDIUM


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_id: str
    description: str
    severity: str
    status: str
    created_at: datetime