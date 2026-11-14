from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AvailabilityRegister(BaseModel):
    vehicle_id: str
    vehicle_type: str
    zone_id: str


class AvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vehicle_id: str
    vehicle_type: str
    zone_id: str
    is_available: bool
    updated_at: datetime