"""Ventana principal en TRES COLUMNAS verticales y responsivas:
   [ HUD ] | [ Cuerpo interactivo ] | [ Detalle ]  + pantalla roja de emergencia encima."""
from __future__ import annotations

from typing import Optional

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QMessageBox, QWidget

from .. import config
from ..controllers.app_controller import VOICE, AppController
from ..domain.enums import Region
from .center_column import CenterColumn
from .emergency_overlay import EmergencyOverlay
from .left_column import LeftColumn
from .responsive import column_widths
from .right_column import RightColumn
from .theme import Colors


def _separator() -> QFrame:
    s = QFrame()
    s.setFixedWidth(1)
    s.setStyleSheet(f"background: {Colors.line_dark};")
    return s


class MainWindow(QMainWindow):
    def __init__(self, controller: AppController, allow_back: bool = False):
        super().__init__()
        self.c = controller
        self.setWindowTitle(config.WINDOW_TITLE)
        self.resize(1280, 820)
        self.setMinimumSize(900, 620)

        root = QWidget()
        self.setCentralWidget(root)
        cols = QHBoxLayout(root)
        cols.setContentsMargins(0, 0, 0, 0)
        cols.setSpacing(0)
        self.left = LeftColumn(config.APP_NAME, show_back=allow_back)
        self.center = CenterColumn(config.BODY_IMAGE, config.SOS_HOLD_MS)
        self.right = RightColumn()
        cols.addWidget(self.left)
        cols.addWidget(_separator())
        cols.addWidget(self.center, 1)
        cols.addWidget(_separator())
        cols.addWidget(self.right)
        self.overlay = EmergencyOverlay(root)

        # --- vista → controlador ---
        self.center.region_requested.connect(controller.select_region)
        self.center.close_requested.connect(controller.close_detail)
        self.center.emergency_fired.connect(controller.trigger_emergency)
        self.left.see_region.connect(controller.select_region)
        self.left.back_clicked.connect(self.close)          # vuelve al menú principal
        self.left.voice_clicked.connect(controller.open_voice)
        self.right.region_chosen.connect(controller.select_region)
        self.right.close_requested.connect(controller.close_detail)
        self.right.measure_requested.connect(controller.measure)
        self.overlay.dismissed.connect(controller.end_emergency)
        QShortcut(QKeySequence("Esc"), self, activated=controller.close_detail)

        # --- controlador → vista ---
        controller.view_changed.connect(self._on_view)
        controller.bpm_changed.connect(self._on_bpm)
        controller.measure_started.connect(self.right.region_view.set_measuring)
        controller.measure_finished.connect(self.right.region_view.set_measure_result)
        controller.emergency_started.connect(self._on_emergency_started)
        controller.emergency_ended.connect(lambda _reason: self.overlay.stop())
        controller.error.connect(lambda m: QMessageBox.warning(self, "Aviso", m))

        self._populate()
        self._apply_widths()

    # ---- datos iniciales ----
    def _populate(self) -> None:
        svc = self.c.service
        reports = {r.region: r for r in svc.reports()}
        self.left.set_watch(svc.watch)
        status, worst = svc.headline()
        self.left.set_headline(status, worst)
        self.center.set_reports(reports)
        self.right.set_reports(svc.reports())
        self.right.set_voice_info(svc.voice_info)
        self.right.show_overview()
        self._on_bpm(self.c.bpm)

    # ---- reacciones ----
    def _on_view(self, view) -> None:
        if isinstance(view, Region):
            self.center.set_region(view)
            self.right.show_region(self.c.service.report(view))
        elif view == VOICE:
            self.center.set_region(None)
            self.right.show_voice()
        else:
            self.center.set_region(None)
            self.right.show_overview()

    def _on_bpm(self, bpm: int) -> None:
        self.left.set_bpm(bpm)
        self.center.set_bpm(bpm)
        self.overlay.set_bpm(bpm)

    def _on_emergency_started(self) -> None:
        self.overlay.set_bpm(self.c.bpm)
        self.overlay.start()

    # ---- cierre limpio (detiene el sondeo de bpm y la pantalla de emergencia) ----
    def closeEvent(self, e) -> None:
        self.overlay.stop()
        self.c.stop()
        super().closeEvent(e)

    # ---- responsivo ----
    def _apply_widths(self) -> None:
        left, right = column_widths(self.width())
        self.left.setFixedWidth(left)
        self.right.setFixedWidth(right)

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._apply_widths()
        self.overlay.setGeometry(0, 0, self.width(), self.height())
