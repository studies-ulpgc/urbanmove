from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from shared.database import Base


class Acquisition(Base):
    __tablename__ = "acquisitions"
    id = Column(String, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)
    model = Column(String, nullable=False)
    zone_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
