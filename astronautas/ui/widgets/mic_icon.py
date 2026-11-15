"""Ícono de micrófono dibujado (círculo azul con micrófono blanco)."""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..theme import Colors, qcolor


class MicIcon(QWidget):
    def __init__(self, size: int = 44, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = float(self.width())
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qcolor(Colors.primary))
        p.drawEllipse(QRectF(0, 0, s, s))
        pen = QPen(qcolor("#ffffff"), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRoundedRect(QRectF(s * .4, s * .22, s * .2, s * .32), s * .1, s * .1)
        p.drawArc(QRectF(s * .29, s * .30, s * .42, s * .36), 180 * 16, 180 * 16)
        p.drawLine(QPointF(s * .5, s * .66), QPointF(s * .5, s * .78))
