"""COLUMNA 1 · HUD: marca, estado del reloj, tarjeta de estado, latidos en vivo y asistente por voz."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ..domain.enums import Region, Status
from ..domain.models import RegionReport, WatchStatus
from .theme import Colors, make_font, qcolor, rgba_css
from .widgets.common import ClickableFrame, StatusPill, button, card, label, muted
from .widgets.ecg import EcgWidget
from .widgets.mic_icon import MicIcon


class LiveChip(QLabel):
    """'● Reloj conectado · en vivo' con punto que parpadea."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(make_font(9.5))
        self._text = ""
        self._on = True
        self._timer = QTimer(self)
        self._timer.setInterval(800)
        self._timer.timeout.connect(self._blink)
        self._timer.start()
        self.setStyleSheet("color: #ffffff; border: 1px solid rgba(255,255,255,64); border-radius: 14px; padding: 5px 12px;")

    def set_watch(self, watch: WatchStatus) -> None:
        self._text = watch.label
        self._on = True
        self._render(watch.connected)
        self._connected = watch.connected

    def _blink(self) -> None:
        self._on = not self._on
        self._render(getattr(self, "_connected", True))

    def _render(self, connected: bool) -> None:
        color = (Colors.live if self._on else "#17644f") if connected else "#fbbf24"
        self.setText(f"<span style='color:{color}'>●</span>&nbsp; {self._text}")


def _back_button() -> QPushButton:
    """Botón discreto '← Menú principal' (solo se muestra al abrir la app desde el menú)."""
    b = QPushButton("←  Menú principal")
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setFont(make_font(9.5))
    b.setFlat(True)
    b.setStyleSheet("QPushButton { color: #b9c6e4; background: transparent; border: 0; text-align: left; padding: 2px 0; }"
                    "QPushButton:hover { color: #ffffff; }")
    return b


class LeftColumn(QFrame):
    see_region = Signal(object)      # Region
    voice_clicked = Signal()
    back_clicked = Signal()          # '← Menú principal'

    def __init__(self, app_name: str, parent=None, show_back: bool = False):
        super().__init__(parent)
        self.setObjectName("leftcol")
        col = QVBoxLayout(self)
        col.setContentsMargins(16, 18, 16, 16)
        col.setSpacing(12)

        if show_back:
            back = _back_button()
            back.clicked.connect(self.back_clicked.emit)
            col.addWidget(back, 0, Qt.AlignmentFlag.AlignLeft)
        col.addWidget(label(app_name, 18, True, "#ffffff", heading=True))
        self._chip = LiveChip()
        col.addWidget(self._chip, 0, Qt.AlignmentFlag.AlignLeft)
        col.addSpacing(4)

        # tarjeta de estado
        self._status_card = card()
        sv = QVBoxLayout(self._status_card)
        sv.setContentsMargins(16, 14, 16, 14)
        sv.setSpacing(6)
        self._pill = StatusPill(Status.OK)
        sv.addWidget(self._pill, 0, Qt.AlignmentFlag.AlignLeft)
        self._summary = label("", 10.5, wrap=True)
        self._summary.setTextFormat(Qt.TextFormat.RichText)
        sv.addWidget(self._summary)
        self._see = button("Ver qué hacer", "btn")
        self._see.clicked.connect(self._on_see)
        sv.addWidget(self._see)
        col.addWidget(self._status_card)
        self._focus_region: Optional[Region] = None

        # latidos en vivo
        bpm_card = card()
        bv = QVBoxLayout(bpm_card)
        bv.setContentsMargins(16, 14, 16, 12)
        bv.setSpacing(2)
        bv.addWidget(muted("Latidos en vivo", 10))
        self._bpm = label("", 10, False, Colors.muted)
        self._bpm.setTextFormat(Qt.TextFormat.RichText)
        bv.addWidget(self._bpm)
        bv.addWidget(muted("Datos simulados del reloj", 9))
        self._ecg = EcgWidget()
        bv.addWidget(self._ecg)
        col.addWidget(bpm_card)

        # asistente por voz
        voice = ClickableFrame()
        voice.clicked.connect(self.voice_clicked.emit)
        voice.setStyleSheet(f"QFrame#card {{ background: {Colors.card}; border: 2px dashed {Colors.accent}; border-radius: 18px; }}")
        vh = QHBoxLayout(voice)
        vh.setContentsMargins(14, 12, 14, 12)
        vh.setSpacing(12)
        vh.addWidget(MicIcon(44), 0, Qt.AlignmentFlag.AlignTop)
        vc = QVBoxLayout()
        vc.setSpacing(2)
        vc.addWidget(label("Hablar con el asistente", 10.5, True, wrap=True))
        vc.addWidget(muted("Solo por voz", 9.5))
        soon = label("Próximamente", 9, True, Colors.accent)
        soon.setStyleSheet(f"color: {Colors.accent}; background: {rgba_css(Colors.accent, 36)}; border-radius: 10px; padding: 2px 10px;")
        vc.addWidget(soon, 0, Qt.AlignmentFlag.AlignLeft)
        vh.addLayout(vc, 1)
        col.addWidget(voice)
        col.addStretch(1)
        self.set_bpm(76)

    # ---- API ----
    def set_watch(self, watch: WatchStatus) -> None:
        self._chip.set_watch(watch)

    def set_headline(self, status: Status, report: Optional[RegionReport]) -> None:
        self._pill.set_status(status)
        if report is None:
            self._summary.setText("Todo en orden.")
            self._focus_region = None
            self._see.hide()
        else:
            self._summary.setText(f"<b>{report.short_name}:</b> {report.summary}")
            self._focus_region = report.region
            self._see.show()

    def set_bpm(self, bpm: int) -> None:
        self._bpm.setText(f"<span style=\"font-size:34pt; font-weight:700; color:{Colors.text}\">{bpm}</span>"
                          f" <span style=\"color:{Colors.muted}\">bpm</span>")
        self._ecg.set_bpm(bpm)

    def _on_see(self) -> None:
        if self._focus_region is not None:
            self.see_region.emit(self._focus_region)
