@echo off
echo Parando contenedores de UrbanMove...
docker compose -f infrastructure/docker-compose.yml stop
pause