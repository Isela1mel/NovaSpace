"""Controlador: único puente entre la interfaz y los servicios.
La UI emite acciones (select_region, select_section...) y se suscribe a señales;
nunca habla directo con repositorios o servicios para modificar estado."""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from ..domain.enums import Region
from ..services.health_service import HealthService


class _LoaderSignals(QObject):
    done = Signal(object)
    failed = Signal(str)


class _Loader(QRunnable):
    def __init__(self, service: HealthService):
        super().__init__()
        self.service = service
        self.signals = _LoaderSignals()
        self.setAutoDelete(False)          # Python conserva la referencia

    def run(self) -> None:  # hilo secundario: NO tocar widgets aquí
        try:
            self.signals.done.emit(self.service.fetch())
        except Exception as exc:  # noqa: BLE001
            self.signals.failed.emit(str(exc))


class MainController(QObject):
    region_changed = Signal(object)          # Region | None
    section_changed = Signal(str, bool)      # id de sección, panel abierto
    data_changed = Signal()                  # datos, misión o filtro de zona cambiaron
    loading_changed = Signal(bool)
    error = Signal(str)

    def __init__(self, service: HealthService, default_section: str, panel_open: bool = True):
        super().__init__()
        self.service = service
        self._region: Optional[Region] = None
        self._section = default_section
        self._panel_open = panel_open
        self._loader: Optional[_Loader] = None

    def shutdown(self) -> None:
        """Silencia las señales (una carga en curso ya no tocará la ventana cerrada)."""
        self.blockSignals(True)

    # ---- estado ----
    @property
    def region(self) -> Optional[Region]:
        return self._region

    @property
    def section(self) -> str:
        return self._section

    @property
    def panel_open(self) -> bool:
        return self._panel_open

    # ---- acciones ----
    def select_region(self, region: Optional[Region]) -> None:
        if region is self._region:
            return
        self._region = region
        self.region_changed.emit(region)
        self.data_changed.emit()

    def clear_region(self) -> None:
        self.select_region(None)

    def select_section(self, section_id: str) -> None:
        """Clic en el menú: muestra esa opción en la columna derecha."""
        self._section = section_id
        self.section_changed.emit(self._section, True)

    def open_panel(self) -> None:
        if not self._panel_open:
            self._panel_open = True
            self.section_changed.emit(self._section, True)

    def set_mission(self, index: int) -> None:
        self.service.set_mission(index)
        self.data_changed.emit()

    def refresh(self) -> None:
        """Recarga los datos en segundo plano (apto para un backend lento)."""
        if self._loader is not None:
            return
        self._loader = _Loader(self.service)
        self._loader.signals.done.connect(self._on_loaded)
        self._loader.signals.failed.connect(self._on_failed)
        self.loading_changed.emit(True)
        QThreadPool.globalInstance().start(self._loader)

    def _on_loaded(self, snapshot) -> None:
        self._loader = None
        self.service.apply(snapshot)
        self.loading_changed.emit(False)
        self.data_changed.emit()

    def _on_failed(self, message: str) -> None:
        self._loader = None
        self.loading_changed.emit(False)
        self.error.emit(message)
