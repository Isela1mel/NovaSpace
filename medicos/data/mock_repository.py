"""Datos simulados (mismos que el panel web de Vita Orbital)."""
from __future__ import annotations

from typing import Callable, List

from ..domain.enums import Domain
from ..domain.models import (
    Compliance, ConnectionStatus, IndicatorSeries, IndicatorSpec, Mission, PsychData, VoiceMetric,
)
from .repository import HealthRepository

_M = 0xFFFFFFFF


def _rng(seed: int) -> Callable[[], float]:
    """mulberry32, igual que el panel web, para obtener las mismas series."""
    s = seed & _M

    def nxt() -> float:
        nonlocal s
        s = (s + 0x6D2B79F5) & _M
        t = ((s ^ (s >> 15)) * (1 | s)) & _M
        t = (((t + (((t ^ (t >> 7)) * (61 | t)) & _M)) & _M) ^ t) & _M
        return ((t ^ (t >> 14)) & _M) / 4294967296

    return nxt


def _gauss(r: Callable[[], float]) -> float:
    return (sum(r() for _ in range(6)) - 3) * 1.41


# (spec, base, sd, deriva diaria desde el día 21)
_DEFS = [
    (IndicatorSpec("fc", "Frecuencia cardíaca en reposo", "bpm", 80, "hi", .25, 0, Domain.CARDIOVASCULAR), 62, 2, .55),
    (IndicatorSpec("hrv", "Variabilidad de la frecuencia (HRV)", "ms", 40, "lo", .20, 0, Domain.CARDIOVASCULAR), 62, 6, -1.2),
    (IndicatorSpec("pa", "Presión arterial sistólica", "mmHg", 135, "hi", .15, 0, Domain.CARDIOVASCULAR), 118, 4, .5),
    (IndicatorSpec("spo2", "Saturación de oxígeno", "%", 94, "lo", .10, 1, Domain.CARDIOVASCULAR), 98, .5, 0),
    (IndicatorSpec("temp", "Temperatura corporal", "°C", 37.8, "hi", .05, 2, Domain.GENERAL), 36.6, .15, 0),
    (IndicatorSpec("sue", "Horas de sueño", "h", 5.5, "lo", .20, 1, Domain.MENTAL), 7, .5, -.12),
    (IndicatorSpec("glu", "Glucosa en sangre (registro manual)", "mg/dL", 125, "hi", .05, 0, Domain.GENERAL), 92, 5, 0),
]


class MockHealthRepository(HealthRepository):
    def get_missions(self) -> List[Mission]:
        return [
            Mission("iss", "Estación espacial", .25, "unas horas", "continua", ("fc", "sue", "hrv")),
            Mission("moon", "Misión lunar", 3, "unos 3 días", "retraso de ~1.3 s", ("fc", "hrv", "sue")),
            Mission("mars", "Misión a Marte", None, "no hay retorno inmediato", "retraso de 3 a 22 min", ("sue", "hrv", "fc")),
        ]

    def get_indicator_series(self) -> List[IndicatorSeries]:
        out = []
        for k, (spec, base, sd, drift) in enumerate(_DEFS):
            r = _rng(k * 97 + 11)
            vals = []
            for i in range(30):
                v = base + (drift * (i - 19) if i >= 20 else 0) + _gauss(r) * sd * .8
                vals.append(round(v, spec.decimals + 1))
            out.append(IndicatorSeries(spec, vals))
        return out

    def get_psychological(self) -> PsychData:
        return PsychData(
            phq9=[3, 3, 4, 6], gad7=[2, 3, 4, 5], mood=[7, 7, 6, 5], fatigue=[3, 4, 5, 7], stress=[3, 4, 5, 6],
            voice=[
                VoiceMetric("Ritmo del habla", "palabras/min", 150, 138),
                VoiceMetric("Pausas", "por minuto", 6, 9),
                VoiceMetric("Intensidad", "dB", 62, 60),
            ],
        )

    def get_compliance(self) -> List[Compliance]:
        return [
            Compliance("Medición diaria", 28, 30), Compliance("Cuestionario diario", 24, 30),
            Compliance("PHQ-9 semanal", 3, 4), Compliance("GAD-7 semanal", 3, 4),
            Compliance("Muestra de voz", 6, 8), Compliance("Captura de imagen", 5, 8),
        ]

    def get_connection_status(self) -> ConnectionStatus:
        return ConnectionStatus(online=True, last_sync="hoy 08:12")
