"""Lógica de negocio: análisis de series, estados, ventanas de intervención,
resúmenes por zona del cuerpo y alertas. No depende de Qt."""
from __future__ import annotations

import math
from typing import List, Optional

from ..data.repository import HealthRepository
from ..domain.enums import Domain, Region, Status
from ..domain.models import (
    Alert, Compliance, Finding, Hazard, IndicatorAnalysis, IndicatorSeries, MetricCard, Mission,
    PsychData, RegionSummary, Snapshot, ConnectionStatus,
)

RECOMMENDATIONS = {
    "fc": "Repetir la medición en reposo a la misma hora y revisar carga de ejercicio, sueño y estrés.",
    "hrv": "Priorizar descanso y repetir la medición en condiciones similares; informar tendencia al médico de vuelo.",
    "pa": "Repetir la medición con técnica estándar y revisar ingesta de líquidos.",
    "spo2": "Repetir la medición y verificar el sensor.",
    "temp": "Repetir la medición y revisar el entorno de la cabina.",
    "sue": "Mantener horarios regulares de descanso y registrar las interrupciones del sueño.",
    "glu": "Registrar mediciones adicionales para activar el seguimiento.",
}


def fx(v: float, k: int) -> str:
    return f"{v:.{max(k, 0)}f}"


def signed(v: float, k: int) -> str:
    return ("+" if v > 0 else "") + fx(v, k)


def analyze(series: IndicatorSeries) -> IndicatorAnalysis:
    spec, s = series.spec, series.values
    base = s[:20]
    m = sum(base) / len(base)
    sd = math.sqrt(sum((v - m) ** 2 for v in base) / (len(base) - 1)) or 1e-9
    last = s[-1]
    z = (last - m) / sd

    y = s[20:]
    n = len(y)
    xm = (n - 1) / 2
    ym = sum(y) / n
    sxx = sum((i - xm) ** 2 for i in range(n))
    slope = sum((i - xm) * (v - ym) for i, v in enumerate(y)) / sxx
    res = math.sqrt(sum((v - (ym + slope * (i - xm))) ** 2 for i, v in enumerate(y)) / (n - 2))
    se = res / math.sqrt(sxx)

    hi = spec.direction == "hi"
    toward = slope > 0 if hi else slope < 0
    significant = abs(slope) > 1.96 * se
    gap = spec.threshold - last
    days = dlo = None
    if toward and significant:
        days = max(0.0, gap / slope)
        denom = slope + (1 if hi else -1) * 1.96 * se
        dlo = max(0.0, gap / denom) if denom else days
        if dlo < days:
            days, dlo = dlo, days

    breach = last >= spec.threshold if hi else last <= spec.threshold
    risk_z = max(0.0, z if hi else -z)
    if breach:
        status = Status.PRIORITY
    elif abs(z) >= 2 or (days is not None and days <= 14):
        status = Status.ATTENTION
    else:
        status = Status.OK
    anomalies = [i for i, v in enumerate(s) if abs((v - m) / sd) >= 2]
    return IndicatorAnalysis(spec, list(s), m, sd, last, z, slope, res, se, days, dlo, status, anomalies, risk_z)


class HealthService:
    def __init__(self, repository: HealthRepository):
        self._repo = repository
        self._snap: Optional[Snapshot] = None
        self._analyses: List[IndicatorAnalysis] = []
        self._mission_idx = 0

    # ---- carga ----
    def fetch(self) -> Snapshot:
        """Puede correr en un hilo secundario (no toca la UI)."""
        return self._repo.load_snapshot()

    def apply(self, snap: Snapshot) -> None:
        self._snap = snap
        self._analyses = [analyze(s) for s in snap.series]
        self._mission_idx = min(self._mission_idx, max(len(snap.missions) - 1, 0))

    def load(self) -> None:
        self.apply(self.fetch())

    # ---- misión / conexión ----
    @property
    def missions(self) -> List[Mission]:
        return self._snap.missions

    @property
    def mission(self) -> Mission:
        return self._snap.missions[self._mission_idx]

    @property
    def mission_index(self) -> int:
        return self._mission_idx

    def set_mission(self, idx: int) -> None:
        self._mission_idx = idx

    @property
    def connection(self) -> ConnectionStatus:
        return self._snap.connection

    # ---- indicadores ----
    def indicators(self, region: Optional[Region] = None) -> List[IndicatorAnalysis]:
        if region is None:
            return list(self._analyses)
        return [a for a in self._analyses if a.spec.domain == region.domain]

    def indicator(self, ind_id: str) -> IndicatorAnalysis:
        return next(a for a in self._analyses if a.spec.id == ind_id)

    def overall_status(self, region: Optional[Region] = None) -> Status:
        statuses = [a.status for a in self.indicators(region)]
        if region in (None, Region.HEAD):
            statuses += [f.status for f in self._psych_findings()]
        return Status.worst(statuses)

    def global_risk(self) -> float:
        score = sum(a.spec.weight * a.risk_z for a in self._analyses)
        return 1 / (1 + math.exp(-(score - 2.5)))

    def risk_contributions(self):
        items = sorted(self._analyses, key=lambda a: a.spec.weight * a.risk_z, reverse=True)
        top = max((a.spec.weight * a.risk_z for a in items), default=0) or 1.0
        return [(a, a.spec.weight * a.risk_z / top) for a in items]

    def anomalies_total(self) -> int:
        return sum(len(a.anomalies) for a in self._analyses)

    @property
    def psych(self) -> PsychData:
        return self._snap.psych

    @property
    def compliance(self) -> List[Compliance]:
        return self._snap.compliance

    def compliance_pct(self) -> int:
        done = sum(c.done for c in self.compliance)
        total = sum(c.total for c in self.compliance) or 1
        return round(done / total * 100)

    # ---- textos ----
    def window_text(self, a: IndicatorAnalysis) -> str:
        if a.days_to_threshold is None:
            return "Sin tendencia significativa hacia el umbral"
        lo, hi = fx(a.days_to_threshold, 1), fx(a.days_to_threshold_alt, 1)
        if a.days_to_threshold_alt - a.days_to_threshold < .1:
            return f"≈ {lo} días"
        return f"≈ {lo} a {hi} días"

    def comparison_text(self, a: IndicatorAnalysis) -> str:
        m = self.mission
        if a.days_to_threshold is None:
            return "Sin cuenta regresiva: no se proyecta cruce del umbral."
        if m.return_days is None:
            return ("Para esta misión no hay retorno inmediato: prioriza la orientación a bordo "
                    "y la comunicación con los responsables médicos.")
        if a.days_to_threshold < m.return_days:
            return (f"El umbral podría alcanzarse antes de completar un retorno ({m.return_text}). "
                    "Requiere valoración médica prioritaria.")
        return f"Hay margen frente al tiempo de retorno ({m.return_text}); mantener seguimiento."

    # ---- psicológico ----
    @staticmethod
    def _rising(series: List[float], by: float = 2) -> bool:
        return series[-1] - series[0] >= by

    def _psych_findings(self) -> List[Finding]:
        p = self.psych
        out: List[Finding] = []
        if p.stress[-1] >= 6 or self._rising(p.stress):
            out.append(Finding("Estrés detectado", "Tu nivel de tensión está más alto de lo habitual.", Status.ATTENTION))
        if self._rising(p.phq9) and self._rising(p.gad7, 2):
            out.append(Finding("Ánimo y ansiedad en seguimiento",
                               "PHQ-9 y GAD-7 muestran tendencia ascendente en las últimas 4 semanas.", Status.ATTENTION))
        return out

    # ---- resumen por zona del cuerpo ----
    def region_summary(self, region: Region) -> RegionSummary:
        return self._head_summary() if region is Region.HEAD else self._heart_summary()

    def metric_cards(self, region: Optional[Region] = None) -> List[MetricCard]:
        if region is Region.HEAD:
            return self._head_summary().metrics
        if region is Region.HEART:
            return self._heart_summary().metrics
        return [self._card(a) for a in self._analyses]

    def _card(self, a: IndicatorAnalysis) -> MetricCard:
        d = a.spec.decimals
        return MetricCard(a.spec.short_name, fx(a.last, d), a.spec.unit,
                          f"{signed(a.delta, d)} vs. línea base", a.status, a.values[-30:],
                          a.spec.id in self.mission.priority_ids)

    def _heart_summary(self) -> RegionSummary:
        analyses = self.indicators(Region.HEART)
        findings: List[Finding] = []
        for a in analyses:
            if a.status is Status.OK:
                continue
            d = a.spec.decimals
            side = "por encima" if a.delta > 0 else "por debajo"
            extra = f" Ventana estimada hasta el umbral: {self.window_text(a)}." if a.days_to_threshold is not None else ""
            findings.append(Finding(f"{a.spec.short_name} {side} de tu base",
                                    f"Valor actual {fx(a.last, d)} {a.spec.unit}, {fx(abs(a.delta), d)} {a.spec.unit} "
                                    f"{side} de tu línea base.{extra}", a.status))
        if not findings:
            findings.append(Finding("Sin alteraciones", "Tus indicadores cardiovasculares están dentro de tu rango personal.", Status.OK))
        return RegionSummary(Region.HEART, Status.worst(f.status for f in findings), findings,
                             [self._card(a) for a in analyses])

    def _head_summary(self) -> RegionSummary:
        p = self.psych
        sleep = self.indicator("sue")
        findings = self._psych_findings()
        if sleep.status is not Status.OK or sleep.delta <= -.5:
            st = sleep.status if sleep.status is not Status.OK else Status.ATTENTION
            findings.append(Finding("Poco descanso",
                                    f"Dormiste {fx(sleep.last, 1)} h frente a {fx(sleep.mean, 1)} h de tu base.", st))
        if not findings:
            findings.append(Finding("Sin alteraciones", "Tu bienestar mental está dentro de tu patrón habitual.", Status.OK))

        def rise(s, by=2): return Status.ATTENTION if s[-1] - s[0] >= by else Status.OK
        def fall(s, by=2): return Status.ATTENTION if s[0] - s[-1] >= by else Status.OK
        def card(label, s, unit): return MetricCard(label, f"{s[-1]:g}", unit, f"{signed(s[-1] - s[0], 0)} vs. inicio",
                                                   rise(s) if label != "Ánimo" else fall(s), list(s))
        metrics = [card("Estrés percibido", p.stress, "/10"), self._card(sleep),
                   card("PHQ-9", p.phq9, "/27"), card("GAD-7", p.gad7, "/21"),
                   card("Ánimo", p.mood, "/10"), card("Fatiga", p.fatigue, "/10")]
        return RegionSummary(Region.HEAD, Status.worst(f.status for f in findings), findings, metrics)

    def region_status(self, region: Region) -> Status:
        return self.region_summary(region).status

    # ---- alertas ----
    def alerts(self, region: Optional[Region] = None) -> List[Alert]:
        out: List[Alert] = []
        for a in self._analyses:
            if a.status is Status.OK:
                continue
            d = a.spec.decimals
            reg = {Domain.CARDIOVASCULAR: Region.HEART, Domain.MENTAL: Region.HEAD}.get(a.spec.domain)
            side = "por encima" if a.delta > 0 else "por debajo"
            win = f" Ventana estimada hasta el umbral: {self.window_text(a)}." if a.days_to_threshold is not None else ""
            out.append(Alert(a.status, a.spec.short_name,
                             f"Valor actual {fx(a.last, d)} {a.spec.unit}, {fx(abs(a.delta), d)} {a.spec.unit} {side} de tu línea base.{win}",
                             " → ".join(fx(v, d) for v in a.values[-5:]), RECOMMENDATIONS[a.spec.id], reg))
        if self._psych_findings():
            p = self.psych
            out.append(Alert(Status.ATTENTION, "Bienestar psicológico",
                             "PHQ-9 y GAD-7 muestran una tendencia ascendente en las últimas 4 semanas, junto con más fatiga y estrés percibido.",
                             "PHQ-9: " + " → ".join(f"{v:g}" for v in p.phq9) + " · GAD-7: " + " → ".join(f"{v:g}" for v in p.gad7),
                             "Completar los cuestionarios programados y comentar la tendencia con el médico de vuelo.", Region.HEAD))
        out.sort(key=lambda al: -al.status.severity)
        if region is not None:
            out = [al for al in out if al.region is region]
        return out

    # ---- contexto de misión ----
    def hazards(self) -> List[Hazard]:
        def worst_of(ids):
            l = [self.indicator(i) for i in ids]
            return Status.worst(a.status for a in l) if l else Status.OK

        def names(ids):
            return ", ".join(self.indicator(i).spec.short_name for i in ids) or "comunicación y autonomía médica"

        m = self.mission
        spec = [
            ("Radiación espacial", ["fc", "hrv"], "Dosis acumulada: 0.62 mSv/día (simulada)"),
            ("Aislamiento y confinamiento", ["sue"], "Bienestar psicológico: PHQ-9 y GAD-7 en ascenso"),
            ("Distancia a la Tierra", [], "Comunicación: " + m.comms),
            ("Campos gravitacionales", ["pa", "fc"], "Actividad física: 42 min/día (habitual 60)"),
            ("Entornos cerrados hostiles", ["spo2", "temp"], "CO₂ de cabina: 0.4 % (simulado)"),
        ]
        return [Hazard(n, worst_of(ids), names(ids), e) for n, ids, e in spec]
