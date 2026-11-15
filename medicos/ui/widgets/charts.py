"""Gráficas dibujadas con QPainter (sin dependencias externas)."""
from __future__ import annotations

from typing import List, Optional

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QSizePolicy, QWidget

from ...domain.models import IndicatorAnalysis
from ..theme import Colors, make_font, qcolor


class Sparkline(QWidget):
    def __init__(self, values: Optional[List[float]] = None, color: str = Colors.accent, parent=None):
        super().__init__(parent)
        self._values = list(values or [])
        self._color = color
        self.setMinimumSize(80, 28)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(32)

    def set_values(self, values: List[float], color: Optional[str] = None) -> None:
        self._values = list(values)
        if color:
            self._color = color
        self.update()

    def paintEvent(self, _event) -> None:
        if len(self._values) < 2:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        lo, hi = min(self._values), max(self._values)
        span = (hi - lo) or 1.0
        w, h, n = self.width() - 4, self.height() - 8, len(self._values)
        pts = [QPointF(2 + i * w / (n - 1), 4 + h - (v - lo) / span * h) for i, v in enumerate(self._values)]
        poly = QPolygonF(pts)
        p.setPen(QPen(qcolor(self._color), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.drawPolyline(poly)
        p.setBrush(qcolor(self._color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(pts[-1], 3.0, 3.0)


class TrendChart(QWidget):
    """Serie de 30 días + banda personal (±2 DE) + umbral + proyección a 7 días."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._a: Optional[IndicatorAnalysis] = None
        self.setMinimumHeight(190)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_analysis(self, a: IndicatorAnalysis) -> None:
        self._a = a
        self.update()

    def paintEvent(self, _event) -> None:
        a = self._a
        if a is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        left, right, top, bottom = 44, 14, 12, 26
        proj = [(a.projection(i), a.residual * 1.96 * (1 + i / 5)) for i in range(1, 8)]
        vals = a.values + [a.spec.threshold, a.mean + 2 * a.sd, a.mean - 2 * a.sd]
        for v, e in proj:
            vals += [v + e, v - e]
        lo, hi = min(vals), max(vals)
        span = (hi - lo) or 1.0
        X = lambda k: left + k * (W - left - right) / 36
        Y = lambda v: H - bottom - (v - lo) / span * (H - bottom - top)
        dec = a.spec.decimals

        p.setFont(make_font(7.5))
        for i in range(5):
            t = lo + span * i / 4
            p.setPen(QPen(qcolor(Colors.line), 1))
            p.drawLine(QPointF(left, Y(t)), QPointF(W - right, Y(t)))
            p.setPen(qcolor(Colors.muted))
            p.drawText(QRectF(0, Y(t) - 8, left - 6, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f"{t:.{dec}f}")

        # rango personal
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qcolor(Colors.ok, 26))
        p.drawRect(QRectF(left, Y(a.mean + 2 * a.sd), W - left - right, Y(a.mean - 2 * a.sd) - Y(a.mean + 2 * a.sd)))
        p.setPen(QPen(qcolor(Colors.ok), 1, Qt.PenStyle.DashLine))
        p.drawLine(QPointF(left, Y(a.mean)), QPointF(W - right, Y(a.mean)))
        p.setPen(qcolor(Colors.ok))
        p.drawText(QPointF(left + 4, Y(a.mean) - 4), f"Línea base {a.mean:.{dec}f}")
        # umbral
        p.setPen(QPen(qcolor(Colors.pri), 1.2, Qt.PenStyle.DashLine))
        p.drawLine(QPointF(left, Y(a.spec.threshold)), QPointF(W - right, Y(a.spec.threshold)))
        p.setPen(qcolor(Colors.pri))
        p.drawText(QRectF(0, Y(a.spec.threshold) - 18, W - right, 14), Qt.AlignmentFlag.AlignRight,
                   f"Umbral de riesgo {a.spec.threshold:g}")
        # banda de proyección
        band = [QPointF(X(30 + i), Y(v + e)) for i, (v, e) in enumerate(proj)]
        band += [QPointF(X(36 - i), Y(proj[6 - i][0] - proj[6 - i][1])) for i in range(7)]
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qcolor(Colors.accent, 38))
        p.drawPolygon(QPolygonF(band))
        # serie
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(qcolor(Colors.accent), 2.2))
        p.drawPolyline(QPolygonF([QPointF(X(i), Y(v)) for i, v in enumerate(a.values)]))
        p.setPen(QPen(qcolor(Colors.accent), 2, Qt.PenStyle.DashLine))
        p.drawPolyline(QPolygonF([QPointF(X(29), Y(a.last))] + [QPointF(X(30 + i), Y(v)) for i, (v, _) in enumerate(proj)]))
        # anomalías
        p.setPen(QPen(qcolor(Colors.att), 2.5))
        p.setBrush(qcolor(Colors.card))
        for i in a.anomalies:
            p.drawEllipse(QPointF(X(i), Y(a.values[i])), 4.5, 4.5)
        # eje x
        p.setPen(qcolor(Colors.muted))
        for i in (0, 5, 10, 15, 20, 25, 29):
            p.drawText(QRectF(X(i) - 24, H - bottom + 6, 48, 14), Qt.AlignmentFlag.AlignCenter, f"día {i + 1}")
        p.drawText(QRectF(X(33) - 36, H - bottom + 6, 72, 14), Qt.AlignmentFlag.AlignCenter, "proyección")
