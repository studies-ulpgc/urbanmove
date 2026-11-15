# Maintenance Detection Lambda

Función serverless encargada de consumir eventos desde SQS (`VehicleBatteryLow`, `IncidentReported` o exceso de usos) y generar automáticamente una orden en `maintenance-service`.

- **Cola origen:** `maintenance-queue` (suscrita al tópico SNS `urbanmove-events`)
- **Cola de respaldo (DLQ):** `maintenance-dlq` (tras 3 reintentos fallidos)
- **Servicio destino:** `POST /maintenance-orders` (`http://maintenance-service:8005`)