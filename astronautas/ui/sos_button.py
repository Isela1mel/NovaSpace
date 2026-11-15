"""Botón de EMERGENCIA: hay que mantenerlo presionado para evitar activarlo sin querer."""
from __future__ import annotations

from PySide6.QtCore import QElapsedTimer, QRectF, QTimer, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from .theme import Colors, make_font, qcolor


class SosButton(QWidget):
    fired = Signal()

    SIZE = 96

    def __init__(self, hold_ms: int = 1200, parent=None):
        super().__init__(parent)
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Emergencia · mantén presionado")
        self.setAccessibleName("Emergencia. Mantén presionado para activar")
        self._hold = max(200, hold_ms)
        self._progress = 0.0
        self._active = False
        self._clock = QElapsedTimer()
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)

    def _start(self) -> None:
        if self._active:
            return
        self._active = True
        self._clock.start()
        self._timer.start()

    def _cancel(self) -> None:
        self._active = False
        self._timer.stop()
        self._progress = 0.0
        self.update()

    def _tick(self) -> None:
        self._progress = min(1.0, self._clock.elapsed() / self._hold)
        self.update()
        if self._progress >= 1.0:
            self._cancel()
            self.fired.emit()

    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self._start()

    def mouseReleaseEvent(self, _e) -> None:
        self._cancel()

    def leaveEvent(self, e) -> None:
        self._cancel()
        super().leaveEvent(e)

    def keyPressEvent(self, e) -> None:
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space) and not e.isAutoRepeat():
            self._start()
        else:
            super().keyPressEvent(e)

    def keyReleaseEvent(self, e) -> None:
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space) and not e.isAutoRepeat():
            self._cancel()
        else:
            super().keyReleaseEvent(e)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        s = float(self.SIZE)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(qcolor("#ffffff", 51))
        p.drawEllipse(QRectF(0, 0, s, s))
        if self._progress > 0:
            p.setBrush(qcolor("#ffffff"))
            p.drawPie(QRectF(0, 0, s, s), 90 * 16, -int(self._progress * 360 * 16))
        p.setBrush(qcolor(Colors.red))
        p.drawEllipse(QRectF(6, 6, s - 12, s - 12))
        p.setPen(qcolor("#ffffff"))
        p.setFont(make_font(8.5, True))
        p.drawText(QRectF(6, 6, s - 12, s - 12), Qt.AlignmentFlag.AlignCenter, "EMERGENCIA")
