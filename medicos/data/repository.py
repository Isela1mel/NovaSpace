"""Contrato de acceso a datos.

La interfaz y los servicios SOLO conocen esta clase abstracta. Para conectar el
backend real, crea una subclase (ver `api_repository.py`) y cámbiala en
`medicos/config.py::build_repository`. No hay que tocar nada más."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..domain.models import Compliance, ConnectionStatus, IndicatorSeries, Mission, PsychData, Snapshot


class HealthRepository(ABC):
    @abstractmethod
    def get_missions(self) -> List[Mission]: ...

    @abstractmethod
    def get_indicator_series(self) -> List[IndicatorSeries]: ...

    @abstractmethod
    def get_psychological(self) -> PsychData: ...

    @abstractmethod
    def get_compliance(self) -> List[Compliance]: ...

    @abstractmethod
    def get_connection_status(self) -> ConnectionStatus: ...

    def load_snapshot(self) -> Snapshot:
        """Carga todo de una vez. Puede ejecutarse en un hilo secundario, así que
        no debe tocar widgets. Sobrescríbelo si tu API entrega todo en una sola llamada."""
        return Snapshot(
            missions=self.get_missions(),
            series=self.get_indicator_series(),
            psych=self.get_psychological(),
            compliance=self.get_compliance(),
            connection=self.get_connection_status(),
        )
