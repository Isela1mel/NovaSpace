"""Configuración central. Aquí se decide qué ve el médico y de dónde vienen los datos."""
from __future__ import annotations

from pathlib import Path
from typing import List

from .data.mock_repository import MockHealthRepository
from .data.repository import HealthRepository

APP_ROOT = Path(__file__).resolve().parent          # carpeta de esta app
BODY_IMAGE = APP_ROOT / "assets" / "body.png"

APP_NAME = "Vita Orbital"

# --- Opciones del menú que se muestran (el médico decide). Orden = orden en la barra.
# Disponibles: resumen, indicadores, psicologico, prediccion, alertas, contexto, reportes
ENABLED_SECTIONS: List[str] = ["resumen", "indicadores", "psicologico", "prediccion", "alertas", "contexto", "reportes"]
DEFAULT_SECTION = "resumen"        # opción desplegada al abrir la app
PANEL_OPEN_ON_START = True


def build_repository() -> HealthRepository:
    """>>> PUNTO ÚNICO PARA CONECTAR EL BACKEND <<<
    Cambia el mock por tu repositorio real, por ejemplo:
        from .data.api_repository import ApiHealthRepository
        return ApiHealthRepository(base_url="https://tu-api", token="...")
    """
    return MockHealthRepository()
