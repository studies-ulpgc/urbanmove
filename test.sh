#!/bin/bash
set -e

export AWS_ENDPOINT_URL=http://localhost:4566

echo "Preparando entorno virtual e instalando dependencias..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip -q
.venv/bin/python -m pip install fastapi uvicorn sqlalchemy psycopg2-binary boto3 httpx pydantic -q

for req in services/*/requirements.txt; do
    [ -f "$req" ] && .venv/bin/python -m pip install -r "$req" -q
done

echo "Ejecutando TODOS los tests de UrbanMove..."
for service_dir in services/*/; do
    service_name=$(basename "$service_dir")
    echo ""
    echo "=== Probando servicio: $service_name ==="
    export DATABASE_URL="postgresql://admin:adminpassword@localhost:5432/${service_name}_db"
    (cd "$service_dir" && ../../.venv/bin/python -m unittest discover -p "test_*.py")
done
