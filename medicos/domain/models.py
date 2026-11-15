"""Modelos de datos puros (dataclasses). Son el 'contrato' entre el backend,
los servicios y la interfaz."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .enums import Domain, Region, Status


# ---------- Datos crudos (lo que entrega un repositorio) ----------

@dataclass(frozen=True)
class IndicatorSpec:
    id: str
    name: str
    unit: str
    threshold: float
    direction: str          # "hi": riesgo al subir · "lo": riesgo al bajar
    weight: float
    decimals: int
    domain: Domain

    @property
    def short_name(self) -> str:
        return self.name.split(" (")[0]


@dataclass
class IndicatorSeries:
    spec: IndicatorSpec
    values: List[float]     # un valor por día (30 días)


@dataclass(frozen=True)
class VoiceMetric:
    name: str
    unit: str
    baseline: float
    current: float


@dataclass
class PsychData:
    phq9: List[float]
    gad7: List[float]
    mood: List[float]
    fatigue: List[float]
    stress: List[float]
    voice: List[VoiceMetric] = field(default_factory=list)


@dataclass(frozen=True)
class Compliance:
    name: str
    done: int
    total: int


@dataclass(frozen=True)
class Mission:
    id: str
    name: str
    return_days: Optional[float]
    return_text: str
    comms: str
    priority_ids: Tuple[str, ...]


@dataclass(frozen=True)
class ConnectionStatus:
    online: bool
    last_sync: str


@dataclass
class Snapshot:
    """Todo lo que la app necesita del backend en un momento dado."""
    missions: List[Mission]
    series: List[IndicatorSeries]
    psych: PsychData
    compliance: List[Compliance]
    connection: ConnectionStatus


# ---------- Datos calculados (lo que consume la UI) ----------

@dataclass
class IndicatorAnalysis:
    spec: IndicatorSpec
    values: List[float]
    mean: float
    sd: float
    last: float
    z: float
    slope: float
    residual: float
    slope_se: float
    days_to_threshold: Optional[float]
    days_to_threshold_alt: Optional[float]
    status: Status
    anomalies: List[int]
    risk_z: float

    @property
    def delta(self) -> float:
        return self.last - self.mean

    def projection(self, day: int) -> float:
        return self.last + self.slope * day


@dataclass
class MetricCard:
    """Métrica genérica lista para mostrarse (tarjeta o fila)."""
    label: str
    value: str
    unit: str
    delta_text: str
    status: Status
    series: List[float] = field(default_factory=list)
    is_priority: bool = False


@dataclass
class Finding:
    title: str
    text: str
    status: Status


@dataclass
class RegionSummary:
    region: Region
    status: Status
    findings: List[Finding]
    metrics: List[MetricCard]


@dataclass
class Alert:
    status: Status
    title: str
    explanation: str
    evidence: str
    action: str
    region: Optional[Region] = None


@dataclass
class Hazard:
    name: str
    status: Status
    related: str
    detail: str
