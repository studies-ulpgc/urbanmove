import os
import json
import boto3
import uuid
import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "service": "inventory", "level": "%(levelname)s", "message": %(message)s}'
)
logger = logging.getLogger("inventory")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:adminpassword@localhost:5432/inventory_db"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

class VehicleDB(Base):
    __tablename__ = "vehicles"
    id = Column(String, primary_key=True, index=True)
    vehicle_type = Column(String, nullable=False)
    model = Column(String, nullable=False)
    zone_id = Column(String, nullable=False)
    status = Column(String, default=VehicleStatus.AVAILABLE.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class VehicleCreate(BaseModel):
    vehicle_type: VehicleType
    model: str
    zone_id: str

class VehicleStatusUpdate(BaseModel):
    status: VehicleStatus

class VehicleResponse(BaseModel):
    id: str
    vehicle_type: str
    model: str
    zone_id: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

app = FastAPI(title="UrbanMove - Inventory Service", version="1.0.0")

AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:000000000000:urbanmove-events")

sns_client = boto3.client(
    "sns",
    endpoint_url=AWS_ENDPOINT,
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)

def publish_event(event_type: str, payload: dict, correlation_id: str):
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "inventory-service",
        "event_type": event_type,
        "schema_version": "1.0",
        "correlation_id": correlation_id,
        "payload": payload
    }
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(event),
            MessageAttributes={
                "event_type": {"DataType": "String", "StringValue": event_type}
            }
        )
        logger.info(f'"Published event {event_type}", "correlation_id": "{correlation_id}"')
    except Exception as e:
        logger.error(f'"Failed to publish event {event_type}: {str(e)}", "correlation_id": "{correlation_id}"')

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "inventory"}

@app.post("/vehicles", response_model=VehicleResponse, status_code=201)
def register_vehicle(
        vehicle: VehicleCreate,
        x_correlation_id: Optional[str] = Header(default=None)
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    db = SessionLocal()
    try:
        new_vehicle = VehicleDB(
            id=f"veh-{uuid.uuid4().hex[:8]}",
            vehicle_type=vehicle.vehicle_type.value,
            model=vehicle.model,
            zone_id=vehicle.zone_id,
            status=VehicleStatus.AVAILABLE.value
        )
        db.add(new_vehicle)
        db.commit()
        db.refresh(new_vehicle)
        publish_event(
            event_type="VehiclePurchased",
            payload={
                "vehicle_id": new_vehicle.id,
                "vehicle_type": new_vehicle.vehicle_type,
                "model": new_vehicle.model,
                "zone_id": new_vehicle.zone_id,
                "status": new_vehicle.status
            },
            correlation_id=corr_id
        )
        logger.info(f'"Vehicle created: {new_vehicle.id}", "correlation_id": "{corr_id}"')
        return new_vehicle
    finally:
        db.close()

@app.get("/vehicles", response_model=List[VehicleResponse])
def list_vehicles(zone_id: Optional[str] = None, status: Optional[VehicleStatus] = None):
    db = SessionLocal()
    try:
        query = db.query(VehicleDB)
        if zone_id:
            query = query.filter(VehicleDB.zone_id == zone_id)
        if status:
            query = query.filter(VehicleDB.status == status.value)
        return query.all()
    finally:
        db.close()

@app.patch("/vehicles/{vehicle_id}/status", response_model=VehicleResponse)
def update_vehicle_status(
        vehicle_id: str,
        payload: VehicleStatusUpdate,
        x_correlation_id: Optional[str] = Header(default=None)
):
    corr_id = x_correlation_id or str(uuid.uuid4())
    db = SessionLocal()
    try:
        vehicle = db.query(VehicleDB).filter(VehicleDB.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        old_status = vehicle.status
        vehicle.status = payload.status.value
        db.commit()
        db.refresh(vehicle)
        logger.info(f'"Vehicle {vehicle_id} status: {old_status} -> {vehicle.status}", "correlation_id": "{corr_id}"')
        return vehicle
    finally:
        db.close()