from __future__ import annotations

from PySide6.QtGui import QPageSize, QPdfWriter, QTextDocument
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QTextBrowser

from ...services.report_builder import build_report_html
from ..widgets.common import label
from .base import SectionView, page_layout


class ReportSection(SectionView):
    id = "reportes"
    title = "Reporte de salud"
    short_title = "Reportes"

    def build(self, parent):
        lay = page_layout(parent)
        html = build_report_html(self.svc)
        btn = QPushButton("Guardar como PDF")
        btn.setObjectName("primary")
        btn.clicked.connect(lambda: self._export(html))
        lay.addWidget(btn)
        view = QTextBrowser()
        view.setHtml(html)
        view.setMinimumHeight(520)
        lay.addWidget(view)

    def _export(self, html: str) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Guardar reporte", "reporte_vita_orbital.pdf", "PDF (*.pdf)")
        if not path:
            return
        try:
            writer = QPdfWriter(path)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            doc = QTextDocument()
            doc.setHtml(html)
            doc.print_(writer)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "No se pudo guardar", str(exc))
