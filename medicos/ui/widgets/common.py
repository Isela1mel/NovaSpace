"""Widgets pequeños y reutilizables."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QFrame, QLabel, QLayout, QScrollArea, QSizePolicy, QWidget

from ...domain.enums import Status
from ..theme import STATUS_COLOR, Colors, make_font, qcolor, rgba_css


def label(text: str = "", size: float = 10, bold: bool = False, color: str = Colors.text,
          heading: bool = False, wrap: bool = False) -> QLabel:
    lb = QLabel(text)
    lb.setFont(make_font(size, bold, heading))
    lb.setStyleSheet(f"color: {color}; background: transparent;")
    lb.setWordWrap(wrap)
    lb.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    return lb


def muted(text: str = "", size: float = 9, wrap: bool = False) -> QLabel:
    return label(text, size, False, Colors.muted, wrap=wrap)


def card(name: str = "card") -> QFrame:
    f = QFrame()
    f.setObjectName(name)
    return f


def clear_layout(layout: QLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())


def make_scroll(inner: QWidget) -> QScrollArea:
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    sa.setWidget(inner)
    inner.setAutoFillBackground(False)
    sa.viewport().setAutoFillBackground(False)
    return sa


class StatusPill(QLabel):
    """Etiqueta de estado con color: ✓ Normal · ! Atención · ▲ Prioritaria."""

    def __init__(self, status: Status = Status.OK, text: Optional[str] = None, short: bool = False, parent=None):
        super().__init__(parent)
        self.setFont(make_font(9, True))
        self.set_status(status, text, short)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

    def set_status(self, status: Status, text: Optional[str] = None, short: bool = False) -> None:
        c = STATUS_COLOR[status]
        body = text or (status.short_label if short else status.label)
        self.setText(f"{status.symbol}  {body}")
        self.setStyleSheet(
            f"color: {c}; background: {rgba_css(c, 32)}; border-radius: 11px; padding: 3px 11px;")


class BarMeter(QWidget):
    """Barra de progreso redondeada (0..1)."""

    def __init__(self, value: float = 0.0, color: str = Colors.accent, parent=None):
        super().__init__(parent)
        self._v, self._color = max(0.0, min(1.0, value)), color
        self.setFixedHeight(8)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        r = QRectF(0, 0, self.width(), self.height())
        p.setBrush(qcolor(Colors.line))
        p.drawRoundedRect(r, 4, 4)
        if self._v > 0:
            p.setBrush(qcolor(self._color))
            p.drawRoundedRect(QRectF(0, 0, max(8.0, self.width() * self._v), self.height()), 4, 4)
