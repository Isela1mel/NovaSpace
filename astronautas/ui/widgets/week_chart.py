"""Gráfica de los últimos 7 días con línea 'tu normal' y trazo animado."""
from __future__ import annotations

from typing import List

from PySide6.QtCore import QPointF, QRectF, QTimer, Qt, QVariantAnimation
from PySide6.QtGui import QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...domain.enums import Status
from ..theme import STATUS_COLOR, Colors, make_font, qcolor


class WeekChart(QWidget):
    def __init__(self, values: List[float], baseline: float, status: Status, parent=None):
        super().__init__(parent)
        self._v, self._b, self._status = list(values), baseline, status
        self._progress = 0.0
        self.setFixedHeight(130)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(1400)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.valueChanged.connect(self._on_anim)
        QTimer.singleShot(500, self._anim.start)       # igual que la versión web: arranca con un pequeño retraso

    def _on_anim(self, v) -> None:
        self._progress = float(v)
        self.update()

    def paintEvent(self, _event) -> None:
        if len(self._v) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H, pad = float(self.width()), float(self.height()), 22.0
        mn, mx = min(min(self._v), self._b) - 2, max(max(self._v), self._b) + 2
        n = len(self._v)
        X = lambda i: pad + i * (W - 2 * pad) / (n - 1)
        Y = lambda v: H - 24 - (v - mn) / (mx - mn) * (H - 40)
        color = STATUS_COLOR[self._status]

        p.setPen(QPen(qcolor(Colors.muted), 1, Qt.PenStyle.DashLine))
        p.drawLine(QPointF(pad, Y(self._b)), QPointF(W - pad, Y(self._b)))
        p.setFont(make_font(8))
        p.setPen(qcolor(Colors.muted))
        p.drawText(QRectF(0, Y(self._b) - 16, W - pad, 14), Qt.AlignmentFlag.AlignRight, "tu normal")

        # trazo parcial (animación)
        pts = [QPointF(X(i), Y(v)) for i, v in enumerate(self._v)]
        reach = self._progress * (n - 1)
        shown = [pts[0]]
        for i in range(1, n):
            if reach >= i:
                shown.append(pts[i])
            else:
                f = max(0.0, reach - (i - 1))
                a, b = pts[i - 1], pts[i]
                shown.append(QPointF(a.x() + (b.x() - a.x()) * f, a.y() + (b.y() - a.y()) * f))
                break
        p.setPen(QPen(qcolor(color), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.drawPolyline(QPolygonF(shown))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qcolor(color))
        for i, pt in enumerate(pts):
            if reach >= i:
                p.drawEllipse(pt, 5.0 if i == n - 1 else 2.5, 5.0 if i == n - 1 else 2.5)

        p.setPen(qcolor(Colors.muted))
        p.setFont(make_font(8))
        p.drawText(QRectF(pad - 4, H - 18, 80, 14), Qt.AlignmentFlag.AlignLeft, "hace 6 d")
        p.drawText(QRectF(W - pad - 76, H - 18, 80, 14), Qt.AlignmentFlag.AlignRight, "hoy")
