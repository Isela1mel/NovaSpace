"""Colores y fuentes del MENÚ (paleta de la guía de marca)."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFont

MENU_ROOT = Path(__file__).resolve().parent
BACKGROUND_IMAGE = MENU_ROOT / "assets" / "menu_bg.jpg"


class Colors:
    navy_dark = "#071f4d"
    navy = "#0a2c6b"
    primary = "#0a3d91"
    accent = "#1e6bff"
    line = "#d7dee8"
    muted = "#9db8e6"
    text = "#ffffff"
    ok = "#34d399"


BODY_FAMILIES = ["Inter", "Segoe UI", "Roboto", "Helvetica Neue", "Arial"]
HEAD_FAMILIES = ["Aerospace", "Space Grotesk", "Inter", "Segoe UI", "Roboto", "Helvetica Neue", "Arial"]


def make_font(size: float = 10, bold: bool = False, heading: bool = False) -> QFont:
    f = QFont()
    f.setFamilies(HEAD_FAMILIES if heading else BODY_FAMILIES)
    f.setPointSizeF(size)
    f.setWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
    return f
