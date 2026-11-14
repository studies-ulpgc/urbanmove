from datetime import datetime

from models import MaintenanceType
from pydantic import BaseModel, ConfigDict


class MaintenanceCreate(BaseModel):
    vehicle_id: str
    order_type: MaintenanceType = MaintenanceType.REPAIR
    reason: str


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_id: str
    order_type: str
    reason: str
    status: str
    created_at: datetime
    completed_at: datetime | None