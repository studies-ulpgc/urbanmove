@echo off
echo Instalando dependencias base...
if not exist .venv python -m venv .venv
.venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy boto3 httpx pydantic ruff -q

echo Ejecutando TODOS los tests de UrbanMove...
for /D %%S in (services\*) do (
    echo.
    echo === Probando servicio: %%~nxS ===
    pushd "%%S"
    ..\..\.venv\Scripts\python.exe -m unittest discover -p "test_*.py"
    popd
)
pause