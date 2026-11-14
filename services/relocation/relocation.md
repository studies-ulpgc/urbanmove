# [Relocation Service](http://localhost:8006/docs)

Microservicio encargado de gestionar las órdenes de redistribución de vehículos entre zonas con exceso y zonas con déficit.
- **Base de datos:** `relocation_db` (Tabla `relocation_orders`)
- **Puerto local:** `8006`

## Estructura (Clean Architecture)
- `database.py`: Configuración de conexión y sesión SQLAlchemy.
- `models.py`: Entidad `RelocationOrder` y enumerado `RelocationStatus`.
- `schemas.py`: Esquemas Pydantic de validación de entrada/salida.
- `repository.py`: Operaciones de persistencia en PostgreSQL.
- `events.py`: Construcción y publicación de eventos en AWS SNS.
- `main.py`: Definición de endpoints REST FastAPI.

## Endpoints
| Método | Ruta | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Comprobación de estado del contenedor | `200 OK` |
| `POST` | `/relocation-orders` | Crea una orden de recolocación y publica `RelocationOrderCreated` | `201 Created` |
| `GET` | `/relocation-orders` | Lista órdenes de recolocación (filtro opcional: `status`) | `200 OK` |
| `PATCH` | `/relocation-orders/{order_id}/status` | Actualiza estado (`ASSIGNED`, `IN_PROGRESS`, `COMPLETED`) | `200 OK` / `404` |

## Eventos emitidos
- **`RelocationOrderCreated`** -> Tópico SNS `urbanmove-events` (al crear orden)
- **`RelocationOrderCompleted`** -> Tópico SNS `urbanmove-events` (al marcar como `COMPLETED`)