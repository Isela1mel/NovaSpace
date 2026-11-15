"""Modelos de datos puros: el 'contrato' entre backend, servicio e interfaz."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .enums import Region, Status


@dataclass(frozen=True)
class SignalReading:
    """Una señal observada: ícono corto, título y detalle (p. ej. '↑', 'Latidos en reposo', '76 bpm')."""
    icon: str
    title: str
    detail: str


@dataclass
class RegionReport:
    region: Region
    name: str                  # 'Corazón y circulación'
    short_name: str            # 'Corazón'
    status: Status
    call: str                  # frase corta junto al punto del cuerpo
    summary: str               # frase para la tarjeta de estado
    what: str                  # explicación principal
    note: str                  # aviso (p. ej. "no es un diagnóstico")
    readings: List[SignalReading]
    chart_title: str
    values: List[float]        # últimos 7 días
    baseline: float            # "tu normal"
    todo: List[str]
    function: str              # para qué sirve esta parte
    can_measure: bool = False  # muestra el botón "Medir de nuevo"


@dataclass(frozen=True)
class WatchStatus:
    connected: bool
    label: str                 # 'Reloj conectado · en vivo'


@dataclass(frozen=True)
class MeasureResult:
    bpm: int
    message: str


@dataclass(frozen=True)
class EmergencyAck:
    sent: bool
    message: str


@dataclass
class VoiceInfo:
    title: str
    soon_text: str
    headline: str
    lead: str
    abilities: List[str]
    examples: List[str]
    rules: List[str]
    build_note: str


@dataclass
class BodySnapshot:
    """Todo lo que la pantalla necesita del backend para dibujarse."""
    reports: Dict[Region, RegionReport]
    watch: WatchStatus
    voice: VoiceInfo
    live_bpm: int = 76
