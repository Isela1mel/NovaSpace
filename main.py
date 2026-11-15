"""PUNTO DE ENTRADA DE VITA ORBITAL.  Ejecuta:  python main.py
Abre el MENÚ PRINCIPAL; desde ahí se entra a «Astronautas» o a «Médicos»."""
import sys

from PySide6.QtWidgets import QApplication

from menu.launcher import Launcher
from menu.registry import APPS


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")                       # estilo neutro: cada ventana trae su propio QSS
    app.setApplicationName("Vita Orbital")
    app.setQuitOnLastWindowClosed(False)         # el menú reaparece al cerrar una app; él decide cuándo salir

    launcher = Launcher(APPS)
    launcher.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
