"""Lógica de negocio de la pantalla 'Mi cuerpo'. No depende de Qt."""
from __future__ import annotations

from typing import List, Optional, Tuple

from ..data.repository import BodyRepository
from ..domain.enums import Region, Status
from ..domain.models import BodySnapshot, EmergencyAck, MeasureResult, RegionReport, VoiceInfo, WatchStatus


class BodyService:
    def __init__(self, repository: BodyRepository):
        self._repo = repository
        self._snap: Optional[BodySnapshot] = None

    # ---- carga ----
    def load(self) -> None:
        self._snap = self._repo.load_snapshot()

    # ---- consultas ----
    def reports(self) -> List[RegionReport]:
        return list(self._snap.reports.values())

    def report(self, region: Region) -> RegionReport:
        return self._snap.reports[region]

    @property
    def watch(self) -> WatchStatus:
        return self._snap.watch

    @property
    def voice_info(self) -> VoiceInfo:
        return self._snap.voice

    @property
    def initial_bpm(self) -> int:
        return self._snap.live_bpm

    def overall_status(self) -> Status:
        return Status.worst(r.status for r in self.reports())

    def headline(self) -> Tuple[Status, Optional[RegionReport]]:
        """Zona que más necesita atención (None si todo está normal)."""
        worst = None
        for r in self.reports():
            if r.status is Status.ATTENTION and worst is None:
                worst = r
        return (Status.ATTENTION, worst) if worst else (Status.OK, None)

    # ---- acciones en vivo (pensadas para correr en un hilo) ----
    def read_live_bpm(self) -> int:
        return self._repo.read_live_bpm()

    def measure_resting_bpm(self) -> MeasureResult:
        return self._repo.measure_resting_bpm()

    def send_emergency(self, bpm: int) -> EmergencyAck:
        return self._repo.send_emergency(bpm)

    def cancel_emergency(self, reason: str) -> None:
        self._repo.cancel_emergency(reason)
