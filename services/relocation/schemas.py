from datetime import datetime

from models import RelocationStatus
from pydantic import BaseModel, ConfigDict


class RelocationCreate(BaseModel):
    vehicle_id: str
    from_zone: str
    to_zone: str


class RelocationStatusUpdate(BaseModel):
    status: RelocationStatus


class RelocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_id: str
    from_zone: str
    to_zone: str
    status: str
    created_at: datetime
    completed_at: datetime | None