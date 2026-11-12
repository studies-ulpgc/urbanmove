@echo off
echo Eliminando contenedores y volumenes (datos locales)...
docker compose -f infrastructure/docker-compose.yml down -v
pause