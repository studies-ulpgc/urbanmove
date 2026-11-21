@echo off
set PYTHONPATH=%CD%

echo Instalando dependencias base...
if not exist .venv python -m venv .venv
.venv\Scripts\python.exe -m pip install fastapi uvicorn sqlalchemy boto3 httpx pydantic ruff -q

.venv\Scripts\ruff.exe check --fix shared/ services/ lambdas/

echo Ejecutando tests compartidos...
.venv\Scripts\python.exe -m unittest discover -s shared -p "test_*.py"

echo Ejecutando TODOS los tests de Microservicios...
for /D %%S in (services\*) do (
    echo.
    echo === Probando servicio: %%~nxS ===
    pushd "%%S"
    ..\..\.venv\Scripts\python.exe -m unittest discover -p "test_*.py"
    popd
)

echo Ejecutando TODOS los tests de Lambdas...
for /D %%L in (lambdas\*) do (
    echo.
    echo === Probando Lambda: %%~nxL ===
    pushd "%%L"
    ..\..\.venv\Scripts\python.exe -m unittest discover -p "test_*.py"
    popd
)
pause