from datetime import datetime

from models import VehicleStatus, VehicleType
from pydantic import BaseModel, ConfigDict


class VehicleCreate(BaseModel):
    vehicle_type: VehicleType
    model: str
    zone_id: str

class VehicleStatusUpdate(BaseModel):
    status: VehicleStatus

class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_type: str
    model: str
    zone_id: str
    status: str
    created_at: datetime