"""PLANTILLA para conectar el backend real.

1. Implementa cada método llamando a tu API y devolviendo los modelos de
   `medicos.domain.models` (no hace falta cambiar nada de la interfaz).
2. En `medicos/config.py`, dentro de `build_repository()`, devuelve
   `ApiHealthRepository(base_url=..., token=...)` en lugar del mock.

`load_snapshot()` se ejecuta en un hilo secundario (ver MainController.refresh),
así que una llamada HTTP lenta no congela la ventana."""
from __future__ import annotations

from typing import List, Optional

from ..domain.models import Compliance, ConnectionStatus, IndicatorSeries, Mission, PsychData
from .repository import HealthRepository


class ApiHealthRepository(HealthRepository):
    def __init__(self, base_url: str, token: Optional[str] = None, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    # Ejemplo con `requests` (pip install requests):
    #   import requests
    #   r = requests.get(f"{self.base_url}/indicators", headers=self._headers(), timeout=self.timeout)
    #   r.raise_for_status(); data = r.json()
    #   -> convierte `data` a IndicatorSeries(IndicatorSpec(...), values=[...])
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def get_missions(self) -> List[Mission]:
        raise NotImplementedError("GET /missions")

    def get_indicator_series(self) -> List[IndicatorSeries]:
        raise NotImplementedError("GET /indicators?days=30")

    def get_psychological(self) -> PsychData:
        raise NotImplementedError("GET /psychological")

    def get_compliance(self) -> List[Compliance]:
        raise NotImplementedError("GET /compliance")

    def get_connection_status(self) -> ConnectionStatus:
        raise NotImplementedError("GET /status")
