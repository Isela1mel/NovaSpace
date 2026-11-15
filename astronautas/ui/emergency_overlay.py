"""Pantalla roja de emergencia: cubre toda la ventana mientras la alerta está activa."""
from __future__ import annotations

import time

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from .theme import make_font
from .widgets.common import button, label


class EmergencyOverlay(QFrame):
    dismissed = Signal(str)      # "ok" | "error"

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("emergency")
        self.hide()
        self._t0 = 0.0
        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._tick)

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner = QWidget()
        inner.setFixedWidth(460)
        inner.setStyleSheet("background: transparent;")
        col = QVBoxLayout(inner)
        col.setSpacing(14)
        W = "#ffffff"
        self._title = label("Alerta de emergencia enviada", 24, True, W, heading=True, wrap=True)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg = label("Tu tripulación y control de misión fueron avisados (simulado).", 11, False, W, wrap=True)
        self._msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time = label("Tiempo desde la alerta: 0:00", 11, True, W)
        self._time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bpm = label("76", 52, True, W, heading=True)
        self._bpm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        unit = label("bpm", 12, False, W)
        unit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for w in (self._title, self._msg, self._time, self._bpm, unit):
            col.addWidget(w)
        for i, t in enumerate(("Quédate donde estás o fíjate a un punto seguro.",
                               "Respira despacio y avisa a un compañero.",
                               "Sigue las instrucciones del protocolo médico de tu misión.")):
            col.addWidget(label(f"{i + 1}.  {t}", 11, False, W, wrap=True))
        ok = button("Ya estoy bien", "btnw")
        err = button("Fue un error", "btnwg")
        ok.clicked.connect(lambda: self.dismissed.emit("ok"))
        err.clicked.connect(lambda: self.dismissed.emit("error"))
        col.addSpacing(6)
        col.addWidget(ok)
        col.addWidget(err)
        outer.addWidget(inner)

    def start(self, message: str = "") -> None:
        if message:
            self._msg.setText(message)
        self._t0 = time.time()
        self._tick()
        self._timer.start()
        self.setGeometry(self.parentWidget().rect())
        self.show()
        self.raise_()

    def stop(self) -> None:
        self._timer.stop()
        self.hide()

    def set_bpm(self, bpm: int) -> None:
        self._bpm.setText(str(bpm))

    def _tick(self) -> None:
        d = int(time.time() - self._t0)
        self._time.setText(f"Tiempo desde la alerta: {d // 60}:{d % 60:02d}")
