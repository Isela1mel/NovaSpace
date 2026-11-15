"""Controlador: único puente entre la interfaz y el servicio.
La UI emite acciones (select_region, trigger_emergency...) y se suscribe a señales."""
from __future__ import annotations

from typing import Optional, Union

from PySide6.QtCore import QObject, QTimer, Signal

from ..domain.enums import Region
from ..services.body_service import BodyService
from .workers import run_async

VOICE = "voice"
View = Union[None, Region, str]     # None = resumen · Region = detalle · "voice" = asistente por voz


class AppController(QObject):
    view_changed = Signal(object)           # None | Region | "voice"
    bpm_changed = Signal(int)
    measure_started = Signal()
    measure_finished = Signal(str)
    emergency_started = Signal()
    emergency_ended = Signal(str)           # "ok" | "error"
    error = Signal(str)

    def __init__(self, service: BodyService, poll_ms: int = 1000):
        super().__init__()
        self.service = service
        self._view: View = None
        self._bpm = service.initial_bpm
        self._polling = False
        self._emergency = False
        self._timer = QTimer(self)
        self._timer.setInterval(poll_ms)
        self._timer.timeout.connect(self._poll)

    # ---- estado ----
    @property
    def view(self) -> View:
        return self._view

    @property
    def bpm(self) -> int:
        return self._bpm

    @property
    def region(self) -> Optional[Region]:
        return self._view if isinstance(self._view, Region) else None

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        """Detiene el sondeo y silencia las señales. Se llama al cerrar la ventana."""
        self._timer.stop()
        self.blockSignals(True)

    # ---- navegación ----
    def select_region(self, region: Region) -> None:
        self._set_view(region)

    def open_voice(self) -> None:
        self._set_view(VOICE)

    def close_detail(self) -> None:
        self._set_view(None)

    def _set_view(self, view: View) -> None:
        if view == self._view:
            return
        self._view = view
        self.view_changed.emit(view)

    # ---- latidos en vivo ----
    def _poll(self) -> None:
        if self._polling:
            return
        self._polling = True
        run_async(self.service.read_live_bpm, self._on_bpm, self._on_poll_error)

    def _on_bpm(self, bpm: int) -> None:
        self._polling = False
        self._bpm = int(bpm)
        self.bpm_changed.emit(self._bpm)

    def _on_poll_error(self, _msg: str) -> None:
        self._polling = False       # el reloj no respondió: se reintenta en el siguiente ciclo

    # ---- medición en reposo ----
    def measure(self) -> None:
        self.measure_started.emit()
        run_async(self.service.measure_resting_bpm,
                  lambda r: self.measure_finished.emit(r.message),
                  lambda m: (self.measure_finished.emit("No se pudo medir. Intenta de nuevo."), self.error.emit(m)))

    # ---- emergencia ----
    @property
    def emergency_active(self) -> bool:
        return self._emergency

    def trigger_emergency(self) -> None:
        if self._emergency:
            return
        self._emergency = True
        self.emergency_started.emit()
        bpm = self._bpm
        run_async(lambda: self.service.send_emergency(bpm), None, self.error.emit)

    def end_emergency(self, reason: str) -> None:
        if not self._emergency:
            return
        self._emergency = False
        self.emergency_ended.emit(reason)
        run_async(lambda: self.service.cancel_emergency(reason), None, self.error.emit)
