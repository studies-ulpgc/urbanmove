# [Telemetry Service](http://localhost:8003/docs)

Microservicio encargado de registrar la telemetría de bicicletas y patinetes (batería, ubicación GPS y usos) y alertar cuando la batería es baja.
- **Base de datos:** `telemetry_db` (Tabla `telemetry_records`)
- **Puerto local:** `8003`

## Estructura (Clean Architecture)
- `database.py`: Configuración de conexión y sesión SQLAlchemy.
- `models.py`: Entidad `TelemetryRecord`.
- `schemas.py`: Esquemas Pydantic de validación de entrada/salida.
- `repository.py`: Operaciones de persistencia y consulta del último estado en PostgreSQL.
- `events.py`: Construcción y publicación de eventos en AWS SNS.
- `main.py`: Definición de endpoints REST FastAPI.

## Endpoints
| Método | Ruta | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Comprobación de estado del contenedor | `200 OK` |
| `POST` | `/telemetry` | Registra telemetría y publica `VehicleBatteryLow` si batería < 20% | `201 Created` |
| `GET` | `/telemetry/{vehicle_id}` | Obtiene la última lectura de telemetría de un vehículo | `200 OK` / `404` |

## Eventos emitidos
- **`VehicleBatteryLow`** -> Tópico SNS `urbanmove-events` (cuando `battery_level < 20.0`)
  ```json
  {
    "vehicle_id": "veh-10",
    "battery_level": 15.0,
    "uses_since_review": 12
  }
  ```