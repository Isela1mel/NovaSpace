from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton

from ...services.health_service import RECOMMENDATIONS, fx, signed
from ..theme import Colors
from ..widgets.charts import TrendChart
from ..widgets.common import StatusPill, label, muted
from .base import SectionView, note, page_layout, vcard


class IndicatorsSection(SectionView):
    id = "indicadores"
    title = "Indicadores"
    short_title = "Indicadores"

    def __init__(self, controller):
        super().__init__(controller)
        self._sel = None

    def build(self, parent):
        svc = self.svc
        inds = svc.indicators(self.c.region)
        lay = page_layout(parent)
        lay.addWidget(note("Datos simulados. El rango personal se calcula con los primeros 20 días como línea base."))
        if not inds:
            lay.addWidget(muted("Sin indicadores para esta zona."))
            return
        if self._sel not in [a.spec.id for a in inds]:
            self._sel = inds[0].spec.id
        a = svc.indicator(self._sel)

        for x in inds:                               # selector en columna
            b = QPushButton(x.spec.short_name)
            b.setObjectName("chip")
            b.setCheckable(True)
            b.setChecked(x.spec.id == self._sel)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, i=x.spec.id: self._select(i))
            lay.addWidget(b)

        f, v = vcard(6)
        v.addWidget(label(a.spec.name, 12, True, heading=True, wrap=True))
        v.addWidget(StatusPill(a.status), 0, Qt.AlignmentFlag.AlignLeft)
        chart = TrendChart(); chart.set_analysis(a); v.addWidget(chart)
        v.addWidget(muted("Punteada y sombra azul: proyección a 7 días · sombra verde: rango personal (±2 DE) · "
                          "círculos ámbar: anomalías.", 8.5, wrap=True))
        lay.addWidget(f)

        f, v = vcard(4)
        v.addWidget(label("Estadísticas", 12, True, heading=True))
        d = a.spec.decimals
        for k, val in [("Última medición", f"{fx(a.last, d)} {a.spec.unit}"), ("Promedio base", f"{fx(a.mean, d)} {a.spec.unit}"),
                       ("Desviación base", fx(a.sd, d + 1)), ("Desviación actual (z)", fx(a.z, 1)),
                       ("Mínimo / máximo", f"{fx(min(a.values), d)} / {fx(max(a.values), d)}"),
                       ("Tendencia (10 días)", f"{signed(a.slope, 2)} {a.spec.unit}/día"),
                       ("Umbral de riesgo", f"{a.spec.threshold:g} {a.spec.unit}"), ("Anomalías", str(len(a.anomalies)))]:
            v.addWidget(muted(k, 9))
            v.addWidget(label(val, 10, True))
        v.addWidget(label("Qué hacer", 10, True, Colors.primary))
        v.addWidget(muted(RECOMMENDATIONS[a.spec.id], 9.5, wrap=True))
        lay.addWidget(f)
        lay.addStretch(1)

    def _select(self, ind_id: str) -> None:
        self._sel = ind_id
        self.rebuild()
