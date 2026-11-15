"""COLUMNA 2 · Cuerpo interactivo con el botón de emergencia flotante."""
from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout

from ..domain.enums import Region
from ..domain.models import RegionReport
from .body_view import BodyView, Hotspot
from .sos_button import SosButton
from .widgets.common import label


class CenterColumn(QFrame):
    region_requested = Signal(object)    # Region
    close_requested = Signal()
    emergency_fired = Signal()

    def __init__(self, image_path, hold_ms: int, parent=None):
        super().__init__(parent)
        self.setObjectName("centercol")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self.body = BodyView(image_path)
        self.body.region_clicked.connect(self.region_requested.emit)
        self.body.background_clicked.connect(self.close_requested.emit)
        lay.addWidget(self.body)

        self.sos = SosButton(hold_ms, self)
        self.sos.fired.connect(self.emergency_fired.emit)
        self._caption = label("Mantén presionado", 9, True, "#ffffff")
        self._caption.setParent(self)
        self._caption.setStyleSheet("color: #ffffff; background: #071f4d; border-radius: 10px; padding: 4px 10px;")
        self._caption.adjustSize()
        self._caption.show()

    def set_reports(self, reports: Dict[Region, RegionReport]) -> None:
        self.body.set_hotspots({r: Hotspot(rep.status, rep.short_name, rep.call) for r, rep in reports.items()})

    def set_region(self, region: Optional[Region]) -> None:
        self.body.zoom_to(region)

    def set_bpm(self, bpm: int) -> None:
        self.body.set_bpm(bpm)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        m = 20
        self.sos.move(self.width() - self.sos.width() - m, self.height() - self.sos.height() - m)
        self._caption.adjustSize()
        self._caption.move(self.width() - self._caption.width() - m, self.sos.y() - self._caption.height() - 8)
        self.sos.raise_()
        self._caption.raise_()
