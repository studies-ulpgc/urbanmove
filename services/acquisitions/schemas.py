from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AcquisitionCreate(BaseModel):
    vehicle_type: str
    model: str
    zone_id: str
    quantity: int = Field(ge=1)
    unit_cost: float = Field(gt=0)


class AcquisitionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    vehicle_type: str
    model: str
    zone_id: str
    quantity: int
    unit_cost: float
    created_at: datetime
