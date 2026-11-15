"""Vista inicial de la columna derecha: resumen de las zonas tocables."""
from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from ...domain.enums import Region
from ...domain.models import RegionReport
from ..widgets.common import ClickableFrame, StatusPill, label, make_scroll, muted


class RegionCard(ClickableFrame):
    def __init__(self, report: RegionReport, parent=None):
        super().__init__("regioncard", parent)
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(4)
        v.addWidget(StatusPill(report.status), 0, Qt.AlignmentFlag.AlignLeft)
        v.addWidget(label(report.name, 12, True, heading=True, wrap=True))
        v.addWidget(muted(report.call, 10, wrap=True))


class OverviewView(QWidget):
    region_chosen = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._scroll = make_scroll(QWidget())
        lay.addWidget(self._scroll)

    def set_reports(self, reports: List[RegionReport]) -> None:
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setContentsMargins(4, 4, 10, 8)
        v.setSpacing(10)
        v.addWidget(label("Mi cuerpo", 20, True, heading=True))
        v.addWidget(muted("Toca el corazón o la cabeza para ver cómo van.", 10.5, wrap=True))
        v.addSpacing(6)
        for r in reports:
            c = RegionCard(r)
            c.clicked.connect(lambda reg=r.region: self.region_chosen.emit(reg))
            v.addWidget(c)
        v.addStretch(1)
        old = self._scroll.takeWidget()
        self._scroll.setWidget(inner)
        inner.setAutoFillBackground(False)
        if old is not None:
            old.deleteLater()
