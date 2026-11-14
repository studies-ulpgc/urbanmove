from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, String
from database import Base

class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    IN_USE = "IN_USE"
    LOW_BATTERY = "LOW_BATTERY"
    WITHDRAWN = "WITHDRAWN"
    CHARGING = "CHARGING"
    REPAIRING = "REPAIRING"
    READY_FOR_SERVICE = "READY_FOR_SERVICE"
    RETIRED = "RETIRED"

class VehicleType(str, Enum):
    BIKE = "BIKE"
    SCOOTER = "SCOOTER"

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(String, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)
    model = Column(String, nullable=False)
    zone_id = Column(String, nullable=False)
    status = Column(String, default=VehicleStatus.AVAILABLE.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)