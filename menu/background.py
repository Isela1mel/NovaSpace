"""Fondo del menú: la imagen se ajusta SIEMPRE a toda la ventana (sin deformarse) y lleva
un degradado oscuro para que los textos se lean bien."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from .theme import Colors


class SpaceBackground(QWidget):
    def __init__(self, image_path: Path, parent=None):
        super().__init__(parent)
        self._source = QPixmap(str(image_path))
        self._scaled: Optional[QPixmap] = None
        self._scaled_for = QSize()

    def _cover(self) -> QPixmap:
        """Escala la imagen para cubrir todo el widget (recorta lo que sobre)."""
        if self._scaled is None or self._scaled_for != self.size():
            self._scaled = self._source.scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self._scaled_for = self.size()
        return self._scaled

    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        r = self.rect()
        if self._source.isNull():                       # si falta la imagen: fondo azul marino liso
            p.fillRect(r, QColor(Colors.navy_dark))
        else:
            pm = self._cover()
            p.drawPixmap((r.width() - pm.width()) // 2, (r.height() - pm.height()) // 2, pm)
        g = QLinearGradient(0, 0, 0, r.height())
        g.setColorAt(0.0, QColor(4, 12, 32, 170))
        g.setColorAt(0.30, QColor(4, 12, 32, 45))
        g.setColorAt(0.68, QColor(4, 12, 32, 55))
        g.setColorAt(1.0, QColor(4, 12, 32, 200))
        p.fillRect(r, g)
