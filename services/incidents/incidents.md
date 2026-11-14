# [Incidents Service](http://localhost:8004/docs)

Microservicio encargado de registrar y gestionar averías, vandalismo o incidencias reportadas sobre bicicletas y patinetes.
- **Base de datos:** `incidents_db` (Tabla `incidents`)
- **Puerto local:** `8004`

## Estructura (Clean Architecture)
- `database.py`: Configuración de conexión y sesión SQLAlchemy.
- `models.py`: Entidad `Incident` y enumerados `IncidentSeverity` y `IncidentStatus`.
- `schemas.py`: Esquemas Pydantic de validación de entrada/salida.
- `repository.py`: Operaciones de persistencia en PostgreSQL.
- `events.py`: Construcción y publicación de eventos en AWS SNS.
- `main.py`: Definición de endpoints REST FastAPI.

## Endpoints
| Método | Ruta | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Comprobación de estado del contenedor | `200 OK` |
| `POST` | `/incidents` | Reporta una incidencia y publica `IncidentReported` | `201 Created` |
| `GET` | `/incidents` | Lista incidencias (filtro opcional: `status`) | `200 OK` |
| `PATCH` | `/incidents/{incident_id}/resolve` | Marca una incidencia como resuelta | `200 OK` / `404` |

## Eventos emitidos
- **`IncidentReported`** -> Tópico SNS `urbanmove-events`
  ```json
  {
    "incident_id": "inc-12345678",
    "vehicle_id": "veh-05",
    "description": "Rueda pinchada",
    "severity": "HIGH"
  }
  ```