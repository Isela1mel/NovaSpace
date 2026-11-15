"""LISTA DE APPS DEL MENÚ. Para agregar otra opción, añade un AppEntry a APPS.
Cada app se importa solo cuando se abre (el menú arranca rápido)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Tuple

from PySide6.QtWidgets import QMainWindow


@dataclass(frozen=True)
class AppEntry:
    key: str                          # identificador interno
    title: str                        # título de la tarjeta
    tagline: str                      # subtítulo
    features: Tuple[str, ...]         # 3 puntos que se muestran en la tarjeta
    factory: Callable[[], QMainWindow]  # crea la ventana de la app


def _open_astronautas() -> QMainWindow:
    from astronautas.app import build_window
    return build_window(allow_back=True)


def _open_medicos() -> QMainWindow:
    from medicos.app import build_window
    return build_window(allow_back=True)


APPS = [
    AppEntry(
        key="astronautas",
        title="Astronautas",
        tagline="Mi cuerpo",
        features=(),
        factory=_open_astronautas,
    ),
    
    AppEntry(
        key="medicos",
        title="Médicos",
        tagline="Panel de monitoreo",
        features=(),
        factory=_open_medicos,
    ),
]
