from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout

from ..theme import Colors
from ..widgets.common import StatusPill, label, muted
from .base import SectionView, bordered, page_layout


class AlertsSection(SectionView):
    id = "alertas"
    title = "Alertas y recomendaciones"
    short_title = "Alertas"

    def build(self, parent):
        lay = page_layout(parent)
        alerts = self.svc.alerts(self.c.region)
        if not alerts:
            lay.addWidget(muted("No hay alertas para esta selección. Seguimiento habitual.", 10))
        for al in alerts:
            f = bordered(al.status, "alert")
            v = QVBoxLayout(f); v.setContentsMargins(14, 10, 14, 10); v.setSpacing(3)
            v.addWidget(StatusPill(al.status), 0, Qt.AlignmentFlag.AlignLeft)
            v.addWidget(label(al.title, 11, True))
            v.addWidget(label(al.explanation, 10, wrap=True))
            v.addWidget(muted("Evolución reciente: " + al.evidence, 9, wrap=True))
            v.addWidget(label("Acción recomendada: " + al.action, 10, True, Colors.primary, wrap=True))
            lay.addWidget(f)
        lay.addStretch(1)
