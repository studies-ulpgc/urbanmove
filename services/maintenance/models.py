from datetime import UTC, datetime
from enum import Enum

from database import Base
from sqlalchemy import Column, DateTime, String


class MaintenanceType(str, Enum):
    RECHARGE = "RECHARGE"
    REPAIR = "REPAIR"
    INSPECTION = "INSPECTION"


class OrderStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class MaintenanceOrder(Base):
    __tablename__ = "maintenance_orders"
    id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    order_type = Column(String, default=MaintenanceType.REPAIR.value, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(String, default=OrderStatus.OPEN.value, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    completed_at = Column(DateTime, nullable=True)