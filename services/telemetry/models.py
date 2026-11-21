from datetime import UTC, datetime
from shared.database import Base
from sqlalchemy import Column, DateTime, Float, Integer, String


class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"
    id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    battery_level = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    uses_since_review = Column(Integer, default=0, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(UTC))