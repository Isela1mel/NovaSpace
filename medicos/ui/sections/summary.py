from __future__ import annotations

from ...domain.enums import Status
from ..widgets.common import BarMeter, StatusPill, label, muted
from .base import SectionView, bordered, column_of, metric_tile, note, page_layout, vcard
from PySide6.QtWidgets import QVBoxLayout


class SummarySection(SectionView):
    id = "resumen"
    title = "Resumen de salud"
    short_title = "Resumen"

    def build(self, parent):
        svc, region = self.svc, self.c.region
        lay = page_layout(parent)
        lay.addWidget(note("Datos simulados con fines demostrativos. Las estimaciones son apoyo a la decisión, "
                           "no diagnóstico ni predicción clínica validada."))
        inds = svc.indicators(region)
        follow = sum(1 for a in inds if a.status is not Status.OK)
        overall = svc.overall_status(region)
        risk = svc.global_risk()

        f = bordered(overall)
        v = QVBoxLayout(f); v.setContentsMargins(14, 10, 12, 10)
        v.addWidget(muted("Estado general")); v.addWidget(StatusPill(overall))
        v.addWidget(muted(f"{follow} de {len(inds)} indicadores con seguimiento"))
        lay.addWidget(f)

        f, v = vcard()
        v.addWidget(muted("Riesgo global estimado"))
        level = "Bajo" if risk < .25 else "Moderado" if risk < .5 else "Alto"
        v.addWidget(label(f"{round(risk * 100)} %  ·  {level}", 18, True, heading=True))
        v.addWidget(BarMeter(risk))
        lay.addWidget(f)

        f, v = vcard()
        v.addWidget(muted("Anomalías individuales (30 días)"))
        v.addWidget(label(str(sum(len(a.anomalies) for a in inds)), 18, True, heading=True))
        v.addWidget(muted("puntos fuera del rango personal"))
        lay.addWidget(f)

        f, v = vcard()
        v.addWidget(muted("Cumplimiento programado"))
        v.addWidget(label(f"{svc.compliance_pct()} %", 18, True, heading=True))
        lay.addWidget(f)

        lay.addLayout(column_of([metric_tile(m) for m in svc.metric_cards(region)]))
        lay.addStretch(1)
