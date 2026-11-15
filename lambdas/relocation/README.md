# Relocation Lambda

Función serverless encargada de consumir eventos `DemandHotspotDetected` desde SQS y crear automáticamente órdenes de redistribución en `relocation-service`.

- **Cola origen:** `relocation-queue` (suscrita al tópico SNS `urbanmove-events`)
- **Servicio destino:** `POST /relocation-orders` (`http://relocation-service:8006`)