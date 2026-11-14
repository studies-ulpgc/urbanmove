from datetime import UTC, datetime
from enum import Enum

from database import Base
from sqlalchemy import Column, DateTime, String


class RelocationStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class RelocationOrder(Base):
    __tablename__ = "relocation_orders"
    id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    from_zone = Column(String, nullable=False)
    to_zone = Column(String, nullable=False)
    status = Column(String, default=RelocationStatus.PENDING.value, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    completed_at = Column(DateTime, nullable=True)