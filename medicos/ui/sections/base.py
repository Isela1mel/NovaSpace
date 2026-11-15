"""Base de las secciones del despliegue + piezas visuales compartidas."""
from __future__ import annotations

from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QWidget

from ...domain.models import MetricCard
from ...services.health_service import HealthService
from ..theme import STATUS_COLOR, Colors
from ..widgets.charts import Sparkline
from ..widgets.common import StatusPill, label, make_scroll, muted


class SectionView(QWidget):
    """Una opción del menú. Hereda, define `id`/`title` e implementa `build()`.
    Se reconstruye sola cuando cambian datos, misión o zona seleccionada."""

    id = ""
    title = ""
    short_title = ""

    def __init__(self, controller):
        super().__init__()
        self.c = controller
        self._dirty = True
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._scroll = make_scroll(QWidget())
        lay.addWidget(self._scroll)
        controller.data_changed.connect(self._mark_dirty)

    @property
    def svc(self) -> HealthService:
        return self.c.service

    def _mark_dirty(self) -> None:
        self._dirty = True
        if self.isVisible():
            self.rebuild()

    def showEvent(self, e) -> None:
        if self._dirty:
            self.rebuild()
        super().showEvent(e)

    def rebuild(self) -> None:
        self._dirty = False
        inner = QWidget()
        self.build(inner)
        old = self._scroll.takeWidget()      # no borrar de golpe: este código puede venir de un clic en `old`
        self._scroll.setWidget(inner)
        inner.setAutoFillBackground(False)
        if old is not None:
            old.deleteLater()

    def build(self, parent: QWidget) -> None:  # pragma: no cover
        raise NotImplementedError


def page_layout(parent: QWidget, spacing: int = 12) -> QVBoxLayout:
    lay = QVBoxLayout(parent)
    lay.setContentsMargins(4, 4, 10, 8)
    lay.setSpacing(spacing)
    return lay


def note(text: str) -> QFrame:
    f = QFrame()
    f.setObjectName("subcard")
    l = QVBoxLayout(f)
    l.setContentsMargins(12, 7, 12, 7)
    l.addWidget(muted(text, 9, wrap=True))
    return f


def bordered(status, name: str = "kpi") -> QFrame:
    """Tarjeta con borde izquierdo del color del estado."""
    f = QFrame()
    f.setObjectName(name)
    f.setStyleSheet(
        f"QFrame#{name} {{ background: {Colors.card}; border: 1px solid {Colors.line}; "
        f"border-left: 5px solid {STATUS_COLOR[status]}; border-radius: 12px; }}")
    return f


def metric_tile(m: MetricCard) -> QFrame:
    f = bordered(m.status)
    v = QVBoxLayout(f)
    v.setContentsMargins(14, 10, 12, 10)
    v.setSpacing(1)
    v.addWidget(muted(("★ " if m.is_priority else "") + m.label, 9, wrap=True))
    v.addWidget(label(f"{m.value} {m.unit}", 18, True, Colors.text, heading=True))
    v.addWidget(muted(m.delta_text, 8.5))
    v.addWidget(Sparkline(m.series, Colors.accent))
    v.addWidget(StatusPill(m.status, short=True), 0, Qt.AlignmentFlag.AlignLeft)
    return f


def column_of(widgets: List[QWidget]) -> QVBoxLayout:
    """Apila los widgets en UNA columna (el diseño no usa filas ni cuadrículas)."""
    v = QVBoxLayout()
    v.setSpacing(10)
    for w in widgets:
        v.addWidget(w)
    return v


def vcard(spacing: int = 3):
    """Tarjeta con layout vertical: devuelve (frame, layout)."""
    f = QFrame()
    f.setObjectName("card")
    v = QVBoxLayout(f)
    v.setContentsMargins(14, 10, 12, 10)
    v.setSpacing(spacing)
    return f, v
