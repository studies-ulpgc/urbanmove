import logging
import os
from abc import ABC, abstractmethod
import httpx
from schemas import AcquisitionCreate

logger = logging.getLogger("acquisitions")


class InventoryGateway(ABC):
    @abstractmethod
    def register_vehicles(self, data: AcquisitionCreate, correlation_id: str) -> None:
        pass


class HttpInventoryGateway(InventoryGateway):
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("INVENTORY_URL", "http://inventory-service:8001")

    def register_vehicles(self, data: AcquisitionCreate, correlation_id: str) -> None:
        payload = {"vehicle_type": data.vehicle_type, "model": data.model, "zone_id": data.zone_id}
        try:
            self._send_batch(payload, data.quantity, correlation_id)
        except Exception as error:
            logger.warning(f'"Inventory sync skipped: {error}", "correlation_id": "{correlation_id}"')

    def _send_batch(self, payload: dict, quantity: int, correlation_id: str) -> None:
        headers = {"x-correlation-id": correlation_id}
        for _ in range(quantity):
            httpx.post(f"{self.base_url}/vehicles", json=payload, headers=headers, timeout=2.0)