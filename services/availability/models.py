from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, String

from shared.database import Base


class VehicleAvailability(Base):
    __tablename__ = "vehicle_availability"
    vehicle_id = Column(String, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)
    zone_id = Column(String, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC))