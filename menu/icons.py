"""Iconos del menú dibujados con código (no hacen falta imágenes)."""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from .theme import Colors


class IconBadge(QWidget):
    """Círculo con degradado azul y un dibujo adentro. kind: 'astronaut' | 'doctor'."""

    def __init__(self, kind: str, size: int = 64, parent=None):
        super().__init__(parent)
        self._kind = kind
        self.setFixedSize(size, size)

    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = float(self.width())
        # base circular
        g = QLinearGradient(0, 0, s, s)
        g.setColorAt(0, QColor(Colors.accent))
        g.setColorAt(1, QColor(Colors.primary))
        p.setPen(QPen(QColor(255, 255, 255, 90), 1.5))
        p.setBrush(QBrush(g))
        p.drawEllipse(QRectF(1, 1, s - 2, s - 2))
        if self._kind == "astronaut":
            self._helmet(p, s)
        else:
            self._cross(p, s)

    @staticmethod
    def _helmet(p: QPainter, s: float) -> None:
        # casco
        p.setPen(QPen(QColor(255, 255, 255, 230), 1.2))
        p.setBrush(QColor("#eaf2ff"))
        p.drawEllipse(QRectF(s * 0.18, s * 0.17, s * 0.64, s * 0.64))
        # visor
        vg = QLinearGradient(0, s * 0.33, 0, s * 0.68)
        vg.setColorAt(0, QColor("#2b5fc0"))
        vg.setColorAt(1, QColor("#071f4d"))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(vg))
        p.drawRoundedRect(QRectF(s * 0.28, s * 0.33, s * 0.44, s * 0.32), s * 0.14, s * 0.14)
        # reflejo del visor
        p.setBrush(QColor(255, 255, 255, 120))
        refl = QPainterPath()
        refl.moveTo(s * 0.35, s * 0.42)
        refl.quadTo(s * 0.40, s * 0.37, s * 0.50, s * 0.38)
        refl.quadTo(s * 0.43, s * 0.42, s * 0.40, s * 0.48)
        refl.closeSubpath()
        p.drawPath(refl)
        # entradas de aire a los lados
        p.setBrush(QColor("#9db8e6"))
        p.drawEllipse(QPointF(s * 0.20, s * 0.50), s * 0.035, s * 0.035)
        p.drawEllipse(QPointF(s * 0.80, s * 0.50), s * 0.035, s * 0.035)

    @staticmethod
    def _cross(p: QPainter, s: float) -> None:
        # cruz médica
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#ffffff"))
        arm, thick = s * 0.44, s * 0.15
        cx, cy = s / 2, s * 0.43
        p.drawRoundedRect(QRectF(cx - arm / 2, cy - thick / 2, arm, thick), thick * 0.3, thick * 0.3)
        p.drawRoundedRect(QRectF(cx - thick / 2, cy - arm / 2, thick, arm), thick * 0.3, thick * 0.3)
        # línea de latido
        pen = QPen(QColor(Colors.ok), max(1.6, s * 0.035))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        y = s * 0.76
        path = QPainterPath(QPointF(s * 0.20, y))
        for x, dy in [(0.36, 0), (0.42, -0.09), (0.48, 0.08), (0.54, -0.04), (0.60, 0), (0.80, 0)]:
            path.lineTo(QPointF(s * x, y + s * dy))
        p.drawPath(path)
