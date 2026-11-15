"""COLUMNA 3 · Despliegue de la opción de menú elegida (siempre visible)."""
from __future__ import annotations

from typing import Dict

from PySide6.QtWidgets import QFrame, QStackedWidget, QVBoxLayout

from .sections.base import SectionView
from .theme import Colors
from .widgets.common import label, muted


class SectionPanel(QFrame):
    WIDTH = 450

    def __init__(self, sections: Dict[str, SectionView], parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setFixedWidth(self.WIDTH)
        self._sections = sections
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 8, 12)
        root.setSpacing(2)
        self._title = label("", 14, True, Colors.text, heading=True, wrap=True)
        root.addWidget(self._title)
        self._context = muted("", 9.5)
        root.addWidget(self._context)
        root.addSpacing(8)
        self._stack = QStackedWidget()
        for view in sections.values():
            self._stack.addWidget(view)
        root.addWidget(self._stack, 1)

    def show_section(self, section_id: str) -> None:
        view = self._sections[section_id]
        self._stack.setCurrentWidget(view)
        self._title.setText(view.title)

    def set_context(self, text: str) -> None:
        self._context.setText(text)
