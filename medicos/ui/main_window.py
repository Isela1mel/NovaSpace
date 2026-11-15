"""Ventana principal en TRES COLUMNAS verticales separadas:
   [ Menú ] | [ Cuerpo interactivo ] | [ Despliegue de la opción elegida ]"""
from __future__ import annotations

from typing import Optional

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QMessageBox, QVBoxLayout, QWidget

from .. import config
from ..controllers.main_controller import MainController
from ..domain.enums import Region
from .body_stage import BodyStage
from .menu_bar import MenuBar
from .section_panel import SectionPanel
from .sections import SECTION_CLASSES
from .theme import Colors


def _separator() -> QFrame:
    s = QFrame()
    s.setFixedWidth(1)
    s.setStyleSheet(f"background: {Colors.line};")
    return s


class MainWindow(QMainWindow):
    def __init__(self, controller: MainController, allow_back: bool = False):
        super().__init__()
        self.c = controller
        self.setWindowTitle(f"{config.APP_NAME} · Panel de escritorio")
        self.resize(1260, 860)
        self.setMinimumSize(1040, 680)

        enabled = [sid for sid in config.ENABLED_SECTIONS if sid in SECTION_CLASSES]
        views = {sid: SECTION_CLASSES[sid](controller) for sid in enabled}

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        cols = QHBoxLayout(root)
        cols.setContentsMargins(0, 0, 0, 0)
        cols.setSpacing(0)

        self.menu = MenuBar([(sid, views[sid].short_title) for sid in enabled], config.APP_NAME, show_back=allow_back)
        cols.addWidget(self.menu)
        cols.addWidget(_separator())

        middle = QWidget()
        ml = QVBoxLayout(middle)
        ml.setContentsMargins(14, 14, 14, 14)
        self.stage = BodyStage(config.BODY_IMAGE)
        ml.addWidget(self.stage)
        cols.addWidget(middle, 1)
        cols.addWidget(_separator())

        self.panel = SectionPanel(views)
        cols.addWidget(self.panel)

        # --- vista → controlador ---
        self.menu.section_clicked.connect(controller.select_section)
        self.menu.mission_changed.connect(controller.set_mission)
        self.menu.sync_clicked.connect(controller.refresh)
        self.menu.back_clicked.connect(self.close)          # vuelve al menú principal
        self.stage.region_requested.connect(controller.select_region)
        self.stage.detail_requested.connect(lambda: controller.select_section(
            "indicadores" if "indicadores" in views else controller.section))
        QShortcut(QKeySequence("Esc"), self, activated=controller.clear_region)

        # --- controlador → vista ---
        controller.region_changed.connect(self._on_region)
        controller.section_changed.connect(self._on_section)
        controller.data_changed.connect(self._on_data)
        controller.loading_changed.connect(self._on_loading)
        controller.error.connect(lambda m: QMessageBox.warning(self, "No se pudo sincronizar", m))

        self.menu.set_missions(controller.service.missions, controller.service.mission_index)
        self._on_data()
        self._on_section(controller.section, True)

    def closeEvent(self, e) -> None:
        self.c.shutdown()
        super().closeEvent(e)

    def _on_region(self, region: Optional[Region]) -> None:
        summary = self.c.service.region_summary(region) if region else None
        self.stage.set_region(region, summary)
        self._update_context()

    def _on_data(self) -> None:
        svc = self.c.service
        self.stage.set_statuses({r: svc.region_status(r) for r in Region})
        if self.c.region is not None:
            self.stage.update_summary(svc.region_summary(self.c.region))
        self.menu.set_badge("alertas", len(svc.alerts()))
        self.menu.set_connection(svc.connection)
        self._update_context()

    def _on_section(self, section_id: str, _is_open: bool = True) -> None:
        self.panel.show_section(section_id)
        self.menu.set_active(section_id)

    def _on_loading(self, loading: bool) -> None:
        self.menu.set_connection(self.c.service.connection, loading)

    def _update_context(self) -> None:
        r = self.c.region
        self.panel.set_context(f"Mostrando: {r.title} · {r.domain.label}" if r else "Mostrando: cuerpo completo")
