from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout

from PySide6.QtCore import Qt
from ..widgets.common import StatusPill, card, label, muted
from .base import SectionView, bordered, column_of, note, page_layout


class ContextSection(SectionView):
    id = "contexto"
    title = "Contexto de la misión"
    short_title = "Contexto"

    def build(self, parent):
        svc, m = self.svc, self.svc.mission
        lay = page_layout(parent)
        lay.addWidget(note("Relaciona los indicadores con los cinco peligros del vuelo espacial humano (NASA HRP). "
                           "Las lecturas ambientales son simuladas."))
        tiles = []
        for h in svc.hazards():
            f = bordered(h.status, "hazard")
            v = QVBoxLayout(f); v.setContentsMargins(14, 10, 12, 10); v.setSpacing(4)
            v.addWidget(label(h.name, 11, True, heading=True))
            v.addWidget(StatusPill(h.status), 0, Qt.AlignmentFlag.AlignLeft)
            v.addWidget(muted("Indicadores relacionados: " + h.related, 9, wrap=True))
            v.addWidget(label(h.detail, 10, wrap=True))
            tiles.append(f)
        lay.addLayout(column_of(tiles))
        pri = ", ".join(svc.indicator(i).spec.short_name for i in m.priority_ids)
        c = card(); cv = QVBoxLayout(c); cv.setContentsMargins(14, 10, 14, 10)
        cv.addWidget(label(f"Perfil de {m.name}", 11, True, heading=True))
        cv.addWidget(label(f"Comunicación {m.comms}. Tiempo operativo de retorno: {m.return_text}. Indicadores prioritarios: {pri}.", 10, wrap=True))
        cv.addWidget(muted("Los límites clínicos no cambian sin criterios validados.", 9))
        lay.addWidget(c)
        lay.addStretch(1)
