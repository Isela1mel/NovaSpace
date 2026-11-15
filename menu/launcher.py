"""Abre la app elegida y vuelve al menú cuando se cierra.
   Menú ──clic──▶ app (el menú se oculta) ──cerrar o «← Menú principal»──▶ Menú"""
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

from .registry import AppEntry
from .window import MenuWindow


class _Menu(MenuWindow):
    """El menú es la ventana raíz: al cerrarlo se termina toda la aplicación."""

    def closeEvent(self, e) -> None:
        QApplication.quit()
        super().closeEvent(e)


class Launcher:
    def __init__(self, apps: List[AppEntry]):
        self._apps = {a.key: a for a in apps}
        self._child: Optional[QMainWindow] = None
        self.menu = _Menu(apps)
        self.menu.app_chosen.connect(self.open_app)

    def show(self) -> None:
        self.menu.show()

    def open_app(self, key: str) -> None:
        if self._child is not None:                      # ya hay una app abierta
            return
        entry = self._apps[key]
        try:
            window = entry.factory()
        except Exception as exc:                         # noqa: BLE001
            QMessageBox.critical(self.menu, "No se pudo abrir", f"{entry.title}: {exc}")
            return

        window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        window.destroyed.connect(self._on_child_closed)
        self._child = window
        self._place_like_menu(window)
        self.menu.hide()
        window.show()
        window.raise_()
        window.activateWindow()

    def _on_child_closed(self, *_args) -> None:
        self._child = None
        self.menu.show()
        self.menu.raise_()
        self.menu.activateWindow()

    def _place_like_menu(self, window: QMainWindow) -> None:
        """Centra la app sobre el menú y evita que sea más grande que la pantalla."""
        screen = (self.menu.screen() or QApplication.primaryScreen()).availableGeometry()
        w = min(window.width(), screen.width())
        h = min(window.height(), screen.height())
        window.resize(w, h)
        center = self.menu.frameGeometry().center()
        x = min(max(center.x() - w // 2, screen.left()), screen.right() - w)
        y = min(max(center.y() - h // 2, screen.top()), screen.bottom() - h)
        window.move(x, y)
