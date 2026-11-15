"""Composición de la app de MÉDICOS: repositorio → servicio → controlador → ventana.
Lo usan tanto el menú principal como `python -m medicos`."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from . import config
from .controllers.main_controller import MainController
from .services.health_service import HealthService
from .ui.main_window import MainWindow
from .ui.theme import build_stylesheet, make_font


def build_window(allow_back: bool = False) -> QMainWindow:
    """Crea la ventana lista para mostrar.
    allow_back=True agrega el botón «← Menú principal» (cuando se abre desde el menú)."""
    service = HealthService(config.build_repository())
    service.load()                      # primera carga síncrona; las siguientes son en segundo plano
    controller = MainController(service, config.DEFAULT_SECTION, config.PANEL_OPEN_ON_START)

    window = MainWindow(controller, allow_back=allow_back)
    # El estilo se aplica SOLO a esta ventana (no a toda la aplicación), así no choca
    # con el menú ni con la app de astronautas, que usan otros estilos.
    window.setFont(make_font(10))
    window.setStyleSheet(build_stylesheet())
    return window


def run() -> int:
    """Modo independiente: abre solo la app de médicos."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = build_window()
    window.show()
    return app.exec()
