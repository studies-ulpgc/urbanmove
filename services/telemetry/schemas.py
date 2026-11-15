from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryCreate(BaseModel):
    vehicle_id: str
    battery_level: float = Field(ge=0, le=100)
    latitude: float
    longitude: float
    uses_since_review: int = Field(default=0, ge=0)


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_id: str
    battery_level: float
    latitude: float
    longitude: float
    uses_since_review: int
    recorded_at: datetime
