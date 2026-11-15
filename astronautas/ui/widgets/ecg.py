"""Electrocardiograma animado que late al ritmo de los bpm."""
from __future__ import annotations

import math
import time
from typing import List

from PySide6.QtCore import QPointF, QTimer, Qt
from PySide6.QtGui import QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QSizePolicy, QWidget

from ..theme import Colors, qcolor


def _g(p: float, c: float, w: float, a: float) -> float:
    return a * math.exp(-((p - c) ** 2) / (2 * w * w))


def ecg_wave(p: float) -> float:
    """Forma de un latido (p entre 0 y 1)."""
    return (_g(p, .18, .03, .12) - _g(p, .285, .008, .15) + _g(p, .31, .012, 1)
            - _g(p, .335, .01, .25) + _g(p, .55, .05, .22))


class EcgWidget(QWidget):
    SAMPLES = 120

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buf: List[float] = [0.0] * self.SAMPLES
        self._phase = 0.0
        self._bpm = 76
        self._last = time.perf_counter()
        self.setMinimumHeight(64)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(64)
        self._timer = QTimer(self)
        self._timer.setInterval(30)
        self._timer.timeout.connect(self._step)
        self._timer.start()

    def set_bpm(self, bpm: int) -> None:
        self._bpm = max(30, int(bpm))

    def _step(self) -> None:
        now = time.perf_counter()
        dt, self._last = now - self._last, now
        self._phase = (self._phase + dt * self._bpm / 60.0) % 1.0
        self._buf.pop(0)
        self._buf.append(ecg_wave(self._phase))
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        sx, sy = self.width() / 240.0, self.height() / 64.0
        poly = QPolygonF([QPointF(i * 2 * sx, (52 - v * 44) * sy) for i, v in enumerate(self._buf)])
        p.setPen(QPen(qcolor(Colors.accent), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.drawPolyline(poly)
