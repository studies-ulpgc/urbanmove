# Availability Service

Microservicio encargado de gestionar qué vehículos pueden reservarse en cada momento y evitar reservas simultáneas.
- **Base de datos:** `availability_db` (Tabla `vehicle_availability`)
- **Puerto local:** `8002`

## Estructura (Clean Architecture)
- `database.py`: Configuración de conexión y sesión SQLAlchemy.
- `models.py`: Entidad `VehicleAvailability`.
- `schemas.py`: Esquemas Pydantic de validación de entrada/salida.
- `repository.py`: Operaciones de consulta, bloqueo y liberación en PostgreSQL.
- `main.py`: Definición de endpoints REST FastAPI.

## Endpoints
| Método | Ruta | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Comprobación de estado del contenedor | `200 OK` |
| `POST` | `/availability` | Registra o actualiza la disponibilidad de un vehículo | `201 Created` |
| `GET` | `/availability` | Lista vehículos disponibles (filtros: `zone_id`, `vehicle_type`) | `200 OK` |
| `POST` | `/availability/{vehicle_id}/lock` | Bloquea un vehículo como no disponible | `200 OK` / `404` |
| `POST` | `/availability/{vehicle_id}/release` | Libera un vehículo volviéndolo disponible | `200 OK` / `404` |