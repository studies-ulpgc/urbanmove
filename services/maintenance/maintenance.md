# [Maintenance Service](http://localhost:8005/docs)

Microservicio encargado de gestionar las órdenes de retirada, recarga, reparación y reincorporación de vehículos al servicio.
- **Base de datos:** `maintenance_db` (Tabla `maintenance_orders`)
- **Puerto local:** `8005`

## Estructura (Clean Architecture)
- `database.py`: Configuración de conexión y sesión SQLAlchemy.
- `models.py`: Entidad `MaintenanceOrder` y enumerados `MaintenanceType` y `OrderStatus`.
- `schemas.py`: Esquemas Pydantic de validación de entrada/salida.
- `repository.py`: Operaciones de persistencia en PostgreSQL.
- `events.py`: Construcción y publicación de eventos en AWS SNS.
- `main.py`: Definición de endpoints REST FastAPI.

## Endpoints
| Método | Ruta | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Comprobación de estado del contenedor | `200 OK` |
| `POST` | `/maintenance-orders` | Abre orden de mantenimiento y publica `VehicleWithdrawnForMaintenance` | `201 Created` |
| `GET` | `/maintenance-orders` | Lista órdenes de mantenimiento (filtro opcional: `status`) | `200 OK` |
| `PATCH` | `/maintenance-orders/{order_id}/complete` | Completa la orden y publica `VehicleReturnedToService` | `200 OK` / `404` |

## Eventos emitidos
- **`VehicleWithdrawnForMaintenance`** -> Tópico SNS `urbanmove-events` (al abrir orden)
- **`VehicleReturnedToService`** -> Tópico SNS `urbanmove-events` (al completar orden)