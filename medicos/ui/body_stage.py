"""Escenario central: cuerpo interactivo + chips de zona + tarjeta de métricas."""
from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QPushButton, QVBoxLayout, QWidget

from ..domain.enums import Region, Status
from ..domain.models import RegionSummary
from .body_view import BodyView
from .metrics_card import MetricsCard
from .widgets.common import muted


class BodyStage(QFrame):
    region_requested = Signal(object)    # Region | None
    detail_requested = Signal()

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setObjectName("stage")
        self.body = BodyView(image_path, self)
        self.body.region_clicked.connect(self.region_requested.emit)
        self.body.background_clicked.connect(lambda: self.region_requested.emit(None))

        self.hint = muted("Toca la cabeza o el corazón", 11)
        self.hint.setParent(self)
        self.hint.setStyleSheet('color: #9db8e6; background: transparent;')
        self.hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint.show()

        # chips de zona (alternativa al toque directo)
        self._chips = QWidget(self)
        lay = QVBoxLayout(self._chips)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: Dict[Optional[Region], QPushButton] = {}
        for region, text in ((None, "Cuerpo completo"), (Region.HEAD, "Cabeza"), (Region.HEART, "Corazón")):
            b = QPushButton(text)
            b.setObjectName("chip")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, r=region: self.region_requested.emit(r))
            self._group.addButton(b)
            lay.addWidget(b)
            self._buttons[region] = b
        self._buttons[None].setChecked(True)

        self.card = MetricsCard(self)
        self.card.hide()
        self.card.closed.connect(lambda: self.region_requested.emit(None))
        self.card.detail_requested.connect(self.detail_requested.emit)
        self._card_anim: Optional[QPropertyAnimation] = None

    # ---- API ----
    def set_statuses(self, statuses: Dict[Region, Status]) -> None:
        self.body.set_statuses(statuses)

    def set_region(self, region: Optional[Region], summary: Optional[RegionSummary]) -> None:
        self._buttons[region].setChecked(True)
        self.body.zoom_to(region)
        self.hint.setVisible(region is None)
        if region is None or summary is None:
            self.card.hide()
            return
        was_hidden = not self.card.isVisible()
        self.card.set_summary(summary)
        target = self._card_rect()
        self.card.show()
        self.card.raise_()
        if was_hidden:
            self.card.setGeometry(target.translated(0, 80))
            self._card_anim = QPropertyAnimation(self.card, b"geometry", self)
            self._card_anim.setDuration(420)
            self._card_anim.setStartValue(target.translated(0, 80))
            self._card_anim.setEndValue(target)
            self._card_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._card_anim.start()
        else:
            self.card.setGeometry(target)

    def update_summary(self, summary: RegionSummary) -> None:
        if self.card.isVisible():
            self.card.set_summary(summary)

    # ---- layout ----
    def _card_rect(self) -> QRect:
        top = int(self.height() * 0.56)
        return QRect(12, top, self.width() - 24, self.height() - top - 12)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self.body.setGeometry(self.rect().adjusted(1, 1, -1, -1))
        self.hint.setGeometry(0, self.height() - 38, self.width(), 24)
        self._chips.adjustSize()
        self._chips.move(16, 12)
        if self.card.isVisible() and not (self._card_anim and self._card_anim.state() == QPropertyAnimation.State.Running):
            self.card.setGeometry(self._card_rect())
        self._chips.raise_()
