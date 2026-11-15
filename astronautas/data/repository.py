"""Contrato de acceso a datos. La interfaz y los servicios SOLO conocen esta clase.
Para conectar el backend real, crea una subclase (ver api_repository.py) y cámbiala
en astronautas/config.py::build_repository(). Nada más cambia."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from ..domain.enums import Region
from ..domain.models import BodySnapshot, EmergencyAck, MeasureResult, RegionReport, VoiceInfo, WatchStatus


class BodyRepository(ABC):
    # --- lectura (carga inicial) ---
    @abstractmethod
    def get_reports(self) -> Dict[Region, RegionReport]: ...

    @abstractmethod
    def get_watch_status(self) -> WatchStatus: ...

    @abstractmethod
    def get_voice_info(self) -> VoiceInfo: ...

    # --- acciones en vivo (se ejecutan en un hilo secundario) ---
    @abstractmethod
    def read_live_bpm(self) -> int:
        """Latidos actuales del reloj."""

    @abstractmethod
    def measure_resting_bpm(self) -> MeasureResult:
        """Pide una medición en reposo (puede tardar unos segundos)."""

    @abstractmethod
    def send_emergency(self, bpm: int) -> EmergencyAck:
        """Avisa a la tripulación y al control de misión."""

    @abstractmethod
    def cancel_emergency(self, reason: str) -> None:
        """reason: 'ok' (ya estoy bien) o 'error' (fue un error)."""

    def load_snapshot(self) -> BodySnapshot:
        return BodySnapshot(self.get_reports(), self.get_watch_status(), self.get_voice_info(), self.read_live_bpm())
