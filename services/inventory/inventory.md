# Inventory Service

Microservicio encargado del registro y control administrativo de bicicletas y patinetes eléctricos.
* **Base de datos:** `inventory_db` (Tabla `vehicles`)
* **Puerto local:** `8001`

## Estructura (Clean Architecture)
* `database.py`: Configuración de conexión y sesión SQLAlchemy.
* `models.py`: Entidad `Vehicle` y enumerados `VehicleStatus` y `VehicleType`.
* `schemas.py`: Esquemas Pydantic de validación de entrada/salida.
* `repository.py`: Operaciones de persistencia en PostgreSQL.
* `events.py`: Construcción y publicación de eventos en AWS SNS.
* `main.py`: Definición de endpoints REST FastAPI.

## Endpoints
| Método | Ruta | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Comprobación de estado del contenedor | `200 OK` |
| `POST` | `/vehicles` | Registra un vehículo nuevo y publica `VehiclePurchased` | `201 Created` |
| `GET` | `/vehicles` | Lista vehículos (filtros opcionales: `zone_id`, `status`) | `200 OK` |
| `PATCH` | `/vehicles/{vehicle_id}/status` | Actualiza el estado del ciclo de vida del vehículo | `200 OK` / `404` |

## Eventos emitidos
* **`VehiclePurchased`** -> Tópico SNS `urbanmove-events`
  ```json
  {
    "vehicle_id": "veh-12345678",
    "vehicle_type": "SCOOTER",
    "model": "Xiaomi Pro 2",
    "zone_id": "ZONA-1",
    "status": "AVAILABLE"
  }