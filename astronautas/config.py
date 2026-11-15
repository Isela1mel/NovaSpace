"""Configuración central de la app. Aquí se decide de dónde vienen los datos."""
from __future__ import annotations

from pathlib import Path

from .data.mock_repository import MockBodyRepository
from .data.repository import BodyRepository

APP_ROOT = Path(__file__).resolve().parent          # carpeta de esta app
BODY_IMAGE = APP_ROOT / "assets" / "body.png"

APP_NAME = "Vita Orbital"
WINDOW_TITLE = "Vita Orbital · Astronautas · Mi cuerpo"

SOS_HOLD_MS = 1200          # tiempo que hay que mantener presionado el botón de emergencia
BPM_POLL_MS = 1000          # cada cuánto se consultan los latidos en vivo


def build_repository() -> BodyRepository:
    """>>> PUNTO ÚNICO PARA CONECTAR EL BACKEND <<<
    Cambia el mock por tu repositorio real, por ejemplo:
        from .data.api_repository import ApiBodyRepository
        return ApiBodyRepository(base_url="https://tu-api", token="...")
    """
    return MockBodyRepository()
