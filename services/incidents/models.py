from datetime import UTC, datetime
from enum import Enum

from shared.database import Base
from sqlalchemy import Column, DateTime, String


class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class Incident(Base):
    __tablename__ = "incidents"
    id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    severity = Column(String, default=IncidentSeverity.MEDIUM.value, nullable=False)
    status = Column(String, default=IncidentStatus.OPEN.value, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))