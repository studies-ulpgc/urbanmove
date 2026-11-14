@echo off
set AWS_ENDPOINT_URL=http://localhost:4566

echo Instalando dependencias base...
if not exist .venv python -m venv .venv
.venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy pg8000 boto3 httpx pydantic ruff -q

echo Ejecutando TODOS los tests de UrbanMove...
for /D %%S in (services\*) do (
    echo.
    echo === Probando servicio: %%~nxS ===
    pushd "%%S"
    cmd /c "set DATABASE_URL=postgresql+pg8000://admin:adminpassword@localhost:5432/%%~nxS_db && ..\..\.venv\Scripts\python.exe -m unittest discover -p test_*.py"
    popd
)
pause