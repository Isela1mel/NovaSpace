from __future__ import annotations

from ...services.health_service import fx, signed
from ..theme import Colors
from ..widgets.common import BarMeter, label, muted
from .base import SectionView, note, page_layout, vcard


class PredictionSection(SectionView):
    id = "prediccion"
    title = "Predicción y ventanas de intervención"
    short_title = "Predicción"

    def build(self, parent):
        svc, m = self.svc, self.svc.mission
        lay = page_layout(parent)
        lay.addWidget(note("Estimaciones simuladas, no predicciones clínicas validadas. La aplicación no decide el regreso "
                           "de un astronauta: apoya la decisión del equipo médico."))

        f, v = vcard(2)
        v.addWidget(label(f"Tiempo hasta el umbral · {m.name}", 11, True, heading=True, wrap=True))
        v.addWidget(muted(f"Retorno: {m.return_text}", 9))
        for a in svc.indicators(self.c.region):
            d = a.spec.decimals
            v.addSpacing(6)
            v.addWidget(label(a.spec.short_name, 10, True))
            v.addWidget(label(svc.window_text(a), 10, True, Colors.primary))
            v.addWidget(muted(f"Actual {fx(a.last, d)} {a.spec.unit} · umbral {a.spec.threshold:g} · tendencia {signed(a.slope, 2)}/día", 9, wrap=True))
            v.addWidget(muted(svc.comparison_text(a), 9, wrap=True))
        v.addSpacing(4)
        v.addWidget(muted("Regresión de los últimos 10 días con intervalo de confianza de 95 %.", 8.5, wrap=True))
        lay.addWidget(f)

        risk = svc.global_risk()
        f, v = vcard(4)
        v.addWidget(label("Modelo global de riesgo (prototipo)", 11, True, heading=True))
        level = "Riesgo bajo" if risk < .25 else "Riesgo moderado" if risk < .5 else "Riesgo alto"
        v.addWidget(label(f"{round(risk * 100)} %  ·  {level}", 18, True, heading=True))
        v.addWidget(BarMeter(risk))
        v.addWidget(muted("Pesos de ejemplo; en el sistema real se entrenará con datos históricos.", 8.5, wrap=True))
        lay.addWidget(f)

        f, v = vcard(4)
        v.addWidget(label("Variables que más influyen", 11, True, heading=True))
        for a, share in svc.risk_contributions()[:5]:
            v.addWidget(muted(f"{a.spec.short_name}: {round(share * 100)} %"))
            v.addWidget(BarMeter(share))
        v.addWidget(muted("Importancia relativa; no es una explicación clínica definitiva.", 8.5, wrap=True))
        lay.addWidget(f)
        lay.addStretch(1)
