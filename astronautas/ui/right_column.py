"""COLUMNA 3 · Detalle: resumen, zona seleccionada o asistente por voz."""
from __future__ import annotations

from typing import List, Union

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QStackedWidget, QVBoxLayout

from ..domain.enums import Region
from ..domain.models import RegionReport, VoiceInfo
from .views.overview_view import OverviewView
from .views.region_view import RegionView
from .views.voice_view import VoiceView


class RightColumn(QFrame):
    region_chosen = Signal(object)
    close_requested = Signal()
    measure_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("rightcol")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 18, 8, 12)
        self._stack = QStackedWidget()
        self.overview = OverviewView()
        self.region_view = RegionView()
        self.voice_view = VoiceView()
        for w in (self.overview, self.region_view, self.voice_view):
            self._stack.addWidget(w)
        lay.addWidget(self._stack)

        self.overview.region_chosen.connect(self.region_chosen.emit)
        self.region_view.close_requested.connect(self.close_requested.emit)
        self.voice_view.close_requested.connect(self.close_requested.emit)
        self.region_view.measure_requested.connect(self.measure_requested.emit)

    def set_reports(self, reports: List[RegionReport]) -> None:
        self.overview.set_reports(reports)

    def set_voice_info(self, info: VoiceInfo) -> None:
        self.voice_view.set_info(info)

    def show_overview(self) -> None:
        self._stack.setCurrentWidget(self.overview)

    def show_region(self, report: RegionReport) -> None:
        self.region_view.set_report(report)
        self._stack.setCurrentWidget(self.region_view)

    def show_voice(self) -> None:
        self._stack.setCurrentWidget(self.voice_view)
