from __future__ import annotations

from ...services.health_service import fx
from ..theme import Colors
from ..widgets.charts import Sparkline
from ..widgets.common import BarMeter, label, muted
from .base import SectionView, note, page_layout, vcard


def _phq(v): return "mínimos" if v < 5 else "leves" if v < 10 else "moderados" if v < 15 else "más elevados"
def _gad(v): return "mínima" if v < 5 else "leve" if v < 10 else "moderada" if v < 15 else "más elevada"


class PsychologicalSection(SectionView):
    id = "psicologico"
    title = "Bienestar psicológico"
    short_title = "Bienestar"

    def build(self, parent):
        p = self.svc.psych
        lay = page_layout(parent)
        lay.addWidget(note("Instrumentos de detección y seguimiento, no diagnósticos clínicos. "
                           "Voz e imagen son señales complementarias y exploratorias."))

        for title, s, mx, text in (
            ("PHQ-9 (semanal)", p.phq9, 27, f"Síntomas {_phq(p.phq9[-1])} · tendencia {'ascendente' if p.phq9[-1] > p.phq9[0] else 'estable'}"),
            ("GAD-7 (semanal)", p.gad7, 21, f"Ansiedad {_gad(p.gad7[-1])} · tendencia {'ascendente' if p.gad7[-1] > p.gad7[0] else 'estable'}")):
            f, v = vcard()
            v.addWidget(muted(title))
            v.addWidget(label(f"{s[-1]:g} / {mx}", 20, True, heading=True))
            v.addWidget(Sparkline(s))
            v.addWidget(muted(text, 9, wrap=True))
            lay.addWidget(f)

        f, v = vcard(4)
        v.addWidget(label("Registro diario (promedio semanal, 0 a 10)", 10, True, wrap=True))
        for name, s in (("Ánimo", p.mood), ("Fatiga", p.fatigue), ("Estrés percibido", p.stress)):
            v.addWidget(muted(f"{name}: {s[-1]:g}"))
            v.addWidget(Sparkline(s))
        lay.addWidget(f)

        f, v = vcard(4)
        v.addWidget(label("Voz (cambio vs. tu patrón)", 11, True, heading=True))
        for m in p.voice:
            ch = (m.current - m.baseline) / m.baseline * 100
            col = Colors.att if abs(ch) > 8 else Colors.ok
            v.addWidget(label(m.name, 10, True))
            v.addWidget(label(f"{m.current:g} {m.unit} · base {m.baseline:g} · {'+' if ch > 0 else ''}{fx(ch, 0)} %", 9.5, False, col))
        v.addWidget(muted("La voz no permite diagnosticar por sí sola una condición psicológica.", 8.5, wrap=True))
        lay.addWidget(f)

        f, v = vcard(4)
        v.addWidget(label("Imagen (exploratorio)", 11, True, heading=True))
        v.addWidget(muted("Variación leve en la expresión facial respecto a tu patrón durante los últimos 7 días. "
                          "Resultado exploratorio; no se usa como evidencia clínica independiente.", 9.5, wrap=True))
        lay.addWidget(f)

        f, v = vcard(4)
        v.addWidget(label("Cumplimiento de evaluaciones", 11, True, heading=True))
        for c in self.svc.compliance:
            v.addWidget(muted(f"{c.name}: {c.done}/{c.total}"))
            v.addWidget(BarMeter(c.done / c.total))
        lay.addWidget(f)
        lay.addStretch(1)
