"""PLANTILLA para conectar el backend real.

1. Implementa cada método llamando a tu API y devolviendo los modelos de `astronautas.domain.models`.
2. En `astronautas/config.py → build_repository()` devuelve `ApiBodyRepository(...)`.

Los métodos de "acciones en vivo" se ejecutan en un hilo secundario (ver controllers/workers.py),
así que una llamada HTTP lenta no congela la ventana."""
from __future__ import annotations

from typing import Dict, Optional

from ..domain.enums import Region
from ..domain.models import EmergencyAck, MeasureResult, RegionReport, VoiceInfo, WatchStatus
from .repository import BodyRepository


class ApiBodyRepository(BodyRepository):
    def __init__(self, base_url: str, token: Optional[str] = None, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    # Ejemplo con `requests` (pip install requests):
    #   r = requests.get(f"{self.base_url}/body/reports", headers=self._headers(), timeout=self.timeout)
    #   r.raise_for_status(); data = r.json()   ->   convierte `data` a RegionReport(...)
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def get_reports(self) -> Dict[Region, RegionReport]:
        raise NotImplementedError("GET /body/reports")

    def get_watch_status(self) -> WatchStatus:
        raise NotImplementedError("GET /watch/status")

    def get_voice_info(self) -> VoiceInfo:
        raise NotImplementedError("GET /assistant/voice-info (o déjalo local)")

    def read_live_bpm(self) -> int:
        raise NotImplementedError("GET /watch/bpm")

    def measure_resting_bpm(self) -> MeasureResult:
        raise NotImplementedError("POST /watch/measure")

    def send_emergency(self, bpm: int) -> EmergencyAck:
        raise NotImplementedError("POST /emergency")

    def cancel_emergency(self, reason: str) -> None:
        raise NotImplementedError("POST /emergency/cancel")
