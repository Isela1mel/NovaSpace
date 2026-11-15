"""Composición de la app de ASTRONAUTAS: repositorio → servicio → controlador → ventana.
Lo usan tanto el menú principal como `python -m astronautas`."""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from . import config
from .controllers.app_controller import AppController
from .services.body_service import BodyService
from .ui.main_window import MainWindow
from .ui.theme import build_stylesheet, make_font


def build_window(allow_back: bool = False) -> QMainWindow:
    """Crea la ventana lista para mostrar.
    allow_back=True agrega el botón «← Menú principal» (cuando se abre desde el menú)."""
    service = BodyService(config.build_repository())
    service.load()
    controller = AppController(service, config.BPM_POLL_MS)

    window = MainWindow(controller, allow_back=allow_back)
    # El estilo se aplica SOLO a esta ventana (no a toda la aplicación), así no choca
    # con el menú ni con la app de médicos, que usan otros estilos.
    window.setFont(make_font(10))
    window.setStyleSheet(build_stylesheet())
    controller.start()
    return window


def run() -> int:
    """Modo independiente: abre solo la app de astronautas."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = build_window()
    window.show()
    return app.exec()
