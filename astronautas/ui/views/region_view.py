"""Detalle de una zona: qué pasa, señales, gráfica de 7 días, qué hacer y para qué sirve."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget

from ...domain.models import RegionReport
from ..theme import STATUS_COLOR, Colors, rgba_css
from ..widgets.common import StatusPill, button, label, make_scroll, muted
from ..widgets.week_chart import WeekChart


def _circle(text: str, bg: str, fg: str, size: int = 30) -> QFrame:
    f = QFrame()
    f.setFixedSize(size, size)
    f.setStyleSheet(f"background: {bg}; border-radius: {size // 2}px;")
    v = QVBoxLayout(f)
    v.setContentsMargins(0, 0, 0, 0)
    lb = label(text, 10, True, fg)
    lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(lb)
    return f


class RegionView(QWidget):
    close_requested = Signal()
    measure_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._scroll = make_scroll(QWidget())
        lay.addWidget(self._scroll)
        self._measure_btn = None
        self._measure_lbl = None

    def set_report(self, r: RegionReport) -> None:
        color = STATUS_COLOR[r.status]
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setContentsMargins(4, 4, 10, 10)
        v.setSpacing(8)

        # título (columna) + botón cerrar (columna)
        head = QHBoxLayout()
        title = QVBoxLayout()
        title.setSpacing(6)
        title.addWidget(label(r.name, 18, True, heading=True, wrap=True))
        title.addWidget(StatusPill(r.status), 0, Qt.AlignmentFlag.AlignLeft)
        head.addLayout(title, 1)
        close = button("Cerrar", "btng")
        close.clicked.connect(self.close_requested.emit)
        head.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        v.addLayout(head)

        v.addSpacing(4)
        v.addWidget(label(r.what, 12, True, wrap=True))
        v.addWidget(muted(r.note, 9.5, wrap=True))

        v.addSpacing(10)
        v.addWidget(muted("Qué estamos viendo", 10.5))
        for s in r.readings:
            row = QHBoxLayout()
            row.setSpacing(10)
            row.addWidget(_circle(s.icon, rgba_css(color, 40), color), 0, Qt.AlignmentFlag.AlignTop)
            col = QVBoxLayout()
            col.setSpacing(0)
            col.addWidget(label(s.title, 10.5, True, wrap=True))
            col.addWidget(muted(s.detail, 10, wrap=True))
            row.addLayout(col, 1)
            v.addLayout(row)

        v.addSpacing(10)
        v.addWidget(muted(r.chart_title, 10.5, wrap=True))
        v.addWidget(WeekChart(r.values, r.baseline, r.status))

        v.addSpacing(10)
        v.addWidget(muted("Qué hacer ahora", 10.5))
        for i, t in enumerate(r.todo, start=1):
            row = QHBoxLayout()
            row.setSpacing(10)
            row.addWidget(_circle(str(i), Colors.primary, "#ffffff", 26), 0, Qt.AlignmentFlag.AlignTop)
            row.addWidget(label(t, 10.5, wrap=True), 1)
            v.addLayout(row)

        self._measure_btn = self._measure_lbl = None
        if r.can_measure:
            self._measure_btn = button("Medir de nuevo", "btn")
            self._measure_btn.clicked.connect(self.measure_requested.emit)
            self._measure_lbl = muted("", 10, wrap=True)
            v.addSpacing(4)
            v.addWidget(self._measure_btn)
            v.addWidget(self._measure_lbl)

        v.addSpacing(10)
        v.addWidget(muted("Para qué sirve esta parte", 10.5))
        v.addWidget(label(r.function, 10.5, wrap=True))
        v.addStretch(1)

        old = self._scroll.takeWidget()
        self._scroll.setWidget(inner)
        inner.setAutoFillBackground(False)
        self._scroll.verticalScrollBar().setValue(0)
        if old is not None:
            old.deleteLater()

    # ---- estado de la medición ----
    def set_measuring(self) -> None:
        if self._measure_btn is not None:
            self._measure_btn.setEnabled(False)
            self._measure_btn.setText("Midiendo…")

    def set_measure_result(self, text: str) -> None:
        if self._measure_btn is not None:
            self._measure_btn.setEnabled(True)
            self._measure_btn.setText("Medir de nuevo")
        if self._measure_lbl is not None:
            self._measure_lbl.setText(text)
