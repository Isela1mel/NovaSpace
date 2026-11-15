"""Información del asistente por voz (próximamente)."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QFrame

from ...domain.models import VoiceInfo
from ..theme import Colors, rgba_css
from ..widgets.common import button, label, make_scroll, muted


class VoiceView(QWidget):
    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        self._scroll = make_scroll(QWidget())
        lay.addWidget(self._scroll)

    def set_info(self, info: VoiceInfo) -> None:
        inner = QWidget()
        v = QVBoxLayout(inner)
        v.setContentsMargins(4, 4, 10, 10)
        v.setSpacing(8)

        head = QHBoxLayout()
        title = QVBoxLayout()
        title.setSpacing(6)
        title.addWidget(label(info.title, 18, True, heading=True, wrap=True))
        soon = label(info.soon_text, 9.5, True, Colors.accent)
        soon.setStyleSheet(f"color: {Colors.accent}; background: {rgba_css(Colors.accent, 36)}; "
                           "border-radius: 11px; padding: 3px 11px;")
        title.addWidget(soon, 0, Qt.AlignmentFlag.AlignLeft)
        head.addLayout(title, 1)
        close = button("Cerrar", "btng")
        close.clicked.connect(self.close_requested.emit)
        head.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
        v.addLayout(head)

        v.addSpacing(4)
        v.addWidget(label(info.headline, 12, True, wrap=True))
        v.addWidget(muted(info.lead, 10, wrap=True))

        def bullets(title_text: str, items) -> None:
            v.addSpacing(10)
            v.addWidget(muted(title_text, 10.5))
            for t in items:
                v.addWidget(label("•  " + t, 10.5, wrap=True))

        bullets("Qué hará", info.abilities)
        v.addSpacing(10)
        v.addWidget(muted("Ejemplos de lo que le dirás", 10.5))
        for q in info.examples:
            f = QFrame()
            f.setObjectName("quote")
            fl = QVBoxLayout(f)
            fl.setContentsMargins(12, 8, 12, 8)
            fl.addWidget(label(q, 10.5, wrap=True))
            v.addWidget(f)
        bullets("Reglas de comportamiento", info.rules)
        v.addSpacing(10)
        v.addWidget(muted("Cómo se construirá", 10.5))
        v.addWidget(muted(info.build_note, 10, wrap=True))
        v.addStretch(1)

        old = self._scroll.takeWidget()
        self._scroll.setWidget(inner)
        inner.setAutoFillBackground(False)
        if old is not None:
            old.deleteLater()
