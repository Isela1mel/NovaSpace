"""COLUMNA 1 · Menú vertical (sin 'Asistente'): marca, opciones, misión y conexión."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QComboBox, QFrame, QLabel, QPushButton, QVBoxLayout

from ..domain.models import ConnectionStatus, Mission
from .theme import make_font
from .widgets.common import label


def _back_button() -> QPushButton:
    """Botón discreto '← Menú principal' (solo se muestra al abrir la app desde el menú)."""
    b = QPushButton("←  Menú principal")
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setFont(make_font(9.5))
    b.setFlat(True)
    b.setStyleSheet("QPushButton { color: #b9c6e4; background: transparent; border: 0; text-align: left; padding: 2px 0; }"
                    "QPushButton:hover { color: #ffffff; }")
    return b


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)


class MenuBar(QFrame):
    section_clicked = Signal(str)
    mission_changed = Signal(int)
    sync_clicked = Signal()
    back_clicked = Signal()          # '← Menú principal'

    def __init__(self, sections: List[Tuple[str, str]], app_name: str, parent=None, show_back: bool = False):
        super().__init__(parent)
        self.setObjectName("menubar")
        self.setFixedWidth(210)
        col = QVBoxLayout(self)
        col.setContentsMargins(14, 18, 14, 16)
        col.setSpacing(4)

        if show_back:
            back = _back_button()
            back.clicked.connect(self.back_clicked.emit)
            col.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)
            col.addSpacing(6)
        col.addWidget(label(app_name, 16, True, "#ffffff", heading=True))
        col.addSpacing(18)

        self._titles: Dict[str, str] = dict(sections)
        self._buttons: Dict[str, QPushButton] = {}
        self._group = QButtonGroup(self)
        self._group.setExclusive(False)
        for sid, title in sections:
            b = QPushButton(title)
            b.setObjectName("navbtn")
            b.setCheckable(True)
            b.setFont(make_font(10))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, s=sid: self.section_clicked.emit(s))
            col.addWidget(b)
            self._buttons[sid] = b
        col.addStretch(1)

        col.addWidget(label("Misión", 9, False, "#b9c6e4"))
        self._mission = QComboBox()
        self._mission.setObjectName("mission")
        self._mission.currentIndexChanged.connect(self.mission_changed.emit)
        col.addWidget(self._mission)
        col.addSpacing(10)
        self._conn = ClickableLabel()
        self._conn.setObjectName("chipdark")
        self._conn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._conn.clicked.connect(self.sync_clicked.emit)
        col.addWidget(self._conn)

    def set_missions(self, missions: List[Mission], current: int) -> None:
        self._mission.blockSignals(True)
        self._mission.clear()
        self._mission.addItems([m.name for m in missions])
        self._mission.setCurrentIndex(current)
        self._mission.blockSignals(False)

    def set_connection(self, status: ConnectionStatus, loading: bool = False) -> None:
        if loading:
            self._conn.setText("<span style='color:#fbbf24'>●</span>&nbsp; Sincronizando…")
        elif status.online:
            self._conn.setText("<span style='color:#34d399'>●</span>&nbsp; Conectado")
        else:
            self._conn.setText("<span style='color:#fbbf24'>●</span>&nbsp; Modo local")
        self._conn.setToolTip(f"Última sincronización: {status.last_sync}\nClic para sincronizar")

    def set_active(self, section_id: Optional[str]) -> None:
        for sid, b in self._buttons.items():
            b.setChecked(sid == section_id)

    def set_badge(self, section_id: str, count: int) -> None:
        if section_id in self._buttons:
            base = self._titles[section_id]
            self._buttons[section_id].setText(f"{base}  ({count})" if count else base)
