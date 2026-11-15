"""Piezas visuales pequeñas y reutilizables."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QLayout, QPushButton, QScrollArea, QSizePolicy, QWidget

from ...domain.enums import Status
from ..theme import STATUS_COLOR, Colors, make_font, rgba_css


def label(text: str = "", size: float = 10, bold: bool = False, color: str = Colors.text,
          heading: bool = False, wrap: bool = False) -> QLabel:
    lb = QLabel(text)
    lb.setFont(make_font(size, bold, heading))
    lb.setStyleSheet(f"color: {color}; background: transparent;")
    lb.setWordWrap(wrap)
    lb.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
    return lb


def muted(text: str = "", size: float = 9.5, wrap: bool = False) -> QLabel:
    return label(text, size, False, Colors.muted, wrap=wrap)


def card(name: str = "card") -> QFrame:
    f = QFrame()
    f.setObjectName(name)
    return f


class ClickableFrame(QFrame):
    """Tarjeta que emite `clicked` al tocarla."""
    clicked = Signal()

    def __init__(self, name: str = "card", parent=None):
        super().__init__(parent)
        self.setObjectName(name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)


def button(text: str, kind: str = "btn") -> QPushButton:
    """kind: btn (principal) · btng (secundario) · btnw / btnwg (sobre fondo rojo)."""
    b = QPushButton(text)
    b.setObjectName(kind)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    return b


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
    """Etiqueta de estado: ✓ Normal · ! Atención."""

    def __init__(self, status: Status = Status.OK, parent=None):
        super().__init__(parent)
        self.setFont(make_font(10, True))
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.set_status(status)

    def set_status(self, status: Status) -> None:
        c = STATUS_COLOR[status]
        self.setText(f"{status.symbol}  {status.label}")
        self.setStyleSheet(f"color: {c}; background: {rgba_css(c, 34)}; border-radius: 12px; padding: 3px 12px;")
