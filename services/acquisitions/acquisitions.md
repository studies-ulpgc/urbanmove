# [Acquisitions Service](http://localhost:8007/docs)

Microservicio encargado de registrar la compra de nuevos lotes de bicicletas y patinetes e incorporarlos al inventario.
- **Base de datos:** `acquisitions_db` (Tabla `acquisitions`)
- **Puerto local:** `8007`

## Estructura (Clean Architecture)
- `database.py`: Configuración de conexión y sesión SQLAlchemy.
- `models.py`: Entidad `Acquisition`.
- `schemas.py`: Esquemas Pydantic de validación de entrada/salida.
- `repository.py`: Operaciones de persistencia en PostgreSQL.
- `events.py`: Construcción y publicación de eventos en AWS SNS.
- `main.py`: Definición de endpoints REST FastAPI y sincronización con `inventory-service`.

## Endpoints
| Método | Ruta | Descripción | Respuesta |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Comprobación de estado del contenedor | `200 OK` |
| `POST` | `/acquisitions` | Registra una compra de flota, crea vehículos en Inventory y publica `VehiclePurchased` | `201 Created` |
| `GET` | `/acquisitions` | Lista todas las adquisiciones registradas | `200 OK` |

## Eventos emitidos
- **`VehiclePurchased`** -> Tópico SNS `urbanmove-events`