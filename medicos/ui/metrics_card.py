"""Tarjeta flotante con las métricas de la zona seleccionada (aparece al tocar el cuerpo)."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from ..domain.models import MetricCard, RegionSummary
from .theme import STATUS_COLOR, Colors
from .widgets.charts import Sparkline
from .widgets.common import StatusPill, clear_layout, label, make_scroll, muted


class MetricRow(QFrame):
    def __init__(self, m: MetricCard, parent=None):
        super().__init__(parent)
        c = STATUS_COLOR[m.status]
        self.setObjectName("metricrow")
        self.setStyleSheet(
            f"QFrame#metricrow {{ background: {Colors.bg}; border: 1px solid {Colors.line}; "
            f"border-left: 4px solid {c}; border-radius: 10px; }}")
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 8, 10, 8)
        left = QVBoxLayout()
        left.setSpacing(0)
        name = ("★ " if m.is_priority else "") + m.label
        left.addWidget(muted(name, 9))
        left.addWidget(label(f"{m.value} {m.unit}", 16, True, Colors.text, heading=True))
        left.addWidget(muted(m.delta_text, 8.5))
        row.addLayout(left, 1)
        right = QVBoxLayout()
        right.setSpacing(2)
        spark = Sparkline(m.series, Colors.accent)
        spark.setFixedWidth(104)
        right.addWidget(spark)
        right.addWidget(StatusPill(m.status, short=True), 0, Qt.AlignmentFlag.AlignRight)
        row.addLayout(right)


class MetricsCard(QFrame):
    closed = Signal()
    detail_requested = Signal()

    WIDTH = 410

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("floatcard")
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(8)

        self._pill = StatusPill()
        root.addWidget(self._pill, 0, Qt.AlignmentFlag.AlignLeft)
        close = QPushButton("✕", self)
        self._close = close
        close.setObjectName("close")
        close.setCursor(Qt.CursorShape.PointingHandCursor)
        close.setToolTip("Volver al cuerpo completo (Esc)")
        close.clicked.connect(self.closed.emit)

        self._title = label("", 20, True, Colors.text, heading=True)
        root.addWidget(self._title)

        self._inner = QWidget()
        self._lay = QVBoxLayout(self._inner)
        self._lay.setContentsMargins(0, 0, 6, 0)
        self._lay.setSpacing(8)
        root.addWidget(make_scroll(self._inner), 1)

        btn = QPushButton("Ver detalle clínico")
        btn.setObjectName("primary")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self.detail_requested.emit)
        root.addWidget(btn)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._close.adjustSize()
        self._close.move(self.width() - self._close.width() - 12, 10)
        self._close.raise_()

    def set_summary(self, s: RegionSummary) -> None:
        self._pill.set_status(s.status)
        self._title.setText(s.region.title)
        clear_layout(self._lay)
        for f in s.findings:
            box = QHBoxLayout()
            box.setSpacing(10)
            dot = QFrame()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(f"background: {STATUS_COLOR[f.status]}; border-radius: 5px;")
            wrap = QVBoxLayout()
            wrap.addWidget(dot, 0, Qt.AlignmentFlag.AlignTop)
            wrap.addStretch(1)
            wrap.setContentsMargins(0, 6, 0, 0)
            txt = QVBoxLayout()
            txt.setSpacing(0)
            txt.addWidget(label(f.title, 11, True, Colors.text, wrap=True))
            txt.addWidget(muted(f.text, 10, wrap=True))
            box.addLayout(wrap)
            box.addLayout(txt, 1)
            self._lay.addLayout(box)
        self._lay.addSpacing(4)
        self._lay.addWidget(label("Métricas", 10, True, Colors.primary))
        for m in s.metrics:
            self._lay.addWidget(MetricRow(m))
        self._lay.addStretch(1)
