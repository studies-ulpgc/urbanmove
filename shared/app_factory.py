import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_service_app(service_name: str, title: str) -> FastAPI:
    _configure_logging(service_name)
    app = FastAPI(title=title, version="1.0.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    _register_health_route(app, service_name)
    return app

def _configure_logging(service_name: str) -> None:
    fmt = (
        f'{{"timestamp": "%(asctime)s", "service": "{service_name}", '
        f'"level": "%(levelname)s", "message": %(message)s}}'
    )
    logging.basicConfig(level=logging.INFO, format=fmt)

def _register_health_route(app: FastAPI, service_name: str) -> None:
    @app.get("/health")
    def health_check():
        return {"status": "ok", "service": service_name}