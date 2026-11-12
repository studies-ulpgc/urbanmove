#!/bin/bash
echo "Levantando infraestructura de UrbanMove (PostgreSQL + LocalStack)..."
docker compose -f infrastructure/docker-compose.yml up -d --build
echo "Listo. Contenedores activos:"
docker compose -f infrastructure/docker-compose.yml ps