# Analytics Ingestion Lambda

Función serverless encargada de consumir eventos desde SQS, validar su estructura según el contrato de eventos de UrbanMove y almacenarlos en el Data Lake, dentro de la zona Raw de Amazon S3.

- **Cola origen:** `datalake-ingestion-queue` (suscrita al tópico SNS `urbanmove-events`)

- **Cola de respaldo (DLQ):** `datalake-ingestion-dlq` (tras 3 reintentos fallidos)

- **Servicio destino:** `Amazon S3` (`urbanmove-datalake`)

Los eventos se almacenan en formato JSON, conservando su contenido original y añadiendo metadata de ingesta. Se organizan por fecha de ingesta, tipo de evento y servicio de origen: `raw/year=YYYY/month=MM/day=DD/event_type/service/event_id.json`

Los errores de procesamiento y mensajes que no puedan deserializarse se almacenan en la zona rejected para su posterior revisión.

## Configuración
Variables de entorno:

- **AWS_ENDPOINT_URL:** endpoint de AWS/LocalStack (http://localstack:4566).

- **DATALAKE_BUCKET:** bucket de destino (`urbanmove-datalake`).

