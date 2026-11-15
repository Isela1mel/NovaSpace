"""Tema: paleta tomada del panel web de Vita Orbital + hoja de estilos Qt."""
from __future__ import annotations

from string import Template

from PySide6.QtGui import QColor, QFont

from ..domain.enums import Status


class Colors:
    bg = "#eef2f8"
    card = "#ffffff"
    text = "#0b2150"
    muted = "#55627a"
    line = "#d7dee8"
    primary = "#0a3d91"
    accent = "#1e6bff"
    ok = "#0f8a5f"
    att = "#b86e00"
    pri = "#c0392b"
    side = "#0a2c6b"        # barra de menú (igual al lateral del panel web)
    tint = "#e6eefc"


STATUS_COLOR = {Status.OK: Colors.ok, Status.ATTENTION: Colors.att, Status.PRIORITY: Colors.pri}

BODY_FAMILIES = ["Inter", "Segoe UI", "Roboto", "Helvetica Neue", "Arial"]
HEAD_FAMILIES = ["Space Grotesk", "Inter", "Segoe UI", "Roboto", "Helvetica Neue", "Arial"]


def qcolor(hex_color: str, alpha: int = 255) -> QColor:
    c = QColor(hex_color)
    c.setAlpha(alpha)
    return c


def rgba_css(hex_color: str, alpha: int) -> str:
    c = QColor(hex_color)
    return f"rgba({c.red()},{c.green()},{c.blue()},{alpha})"


def make_font(size: float = 10, bold: bool = False, heading: bool = False) -> QFont:
    f = QFont()
    f.setFamilies(HEAD_FAMILIES if heading else BODY_FAMILIES)
    f.setPointSizeF(size)
    f.setWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
    return f


_QSS = Template("""
#root { background: $bg; }
#menubar { background: $side; }
QPushButton#navbtn { color: #d7dee8; background: transparent; border: 0; border-radius: 10px; padding: 11px 14px; text-align: left; }
QPushButton#navbtn:hover { background: rgba(255,255,255,24); color: #ffffff; }
QPushButton#navbtn:checked { background: rgba(255,255,255,45); color: #ffffff; font-weight: 600; }
QLabel#chipdark { color: #ffffff; background: rgba(255,255,255,28); border: 1px solid rgba(255,255,255,50);
                  border-radius: 14px; padding: 5px 12px; }
QComboBox#mission { color: #ffffff; background: rgba(255,255,255,28); border: 1px solid rgba(255,255,255,50);
                    border-radius: 14px; padding: 5px 12px; min-width: 150px; }
QComboBox#mission QAbstractItemView { color: $text; background: $card; selection-background-color: $tint;
                                      selection-color: $primary; outline: 0; }
#stage { background: #010101; border: 1px solid #0a2c6b; border-radius: 16px; }
#panel { background: $card; border: 0; }
#card { background: $card; border: 1px solid $line; border-radius: 14px; }
#floatcard { background: $card; border: 1px solid $line; border-radius: 18px; }
#subcard { background: $bg; border: 1px solid $line; border-radius: 12px; }
QPushButton#primary { background: $primary; color: #ffffff; border: 0; border-radius: 12px; padding: 11px 18px; font-weight: 600; }
QPushButton#primary:hover { background: $accent; }
QPushButton#chip { background: $card; color: $text; border: 1px solid $line; border-radius: 15px; padding: 5px 13px; }
QPushButton#chip:hover { border-color: $accent; }
QPushButton#chip:checked { background: $primary; color: #ffffff; border-color: $primary; }
QPushButton#close { background: transparent; color: $muted; border: 0; font-size: 18px; padding: 2px 8px; border-radius: 10px; }
QPushButton#close:hover { background: $bg; color: $text; }
QPushButton#collapse { background: transparent; color: $muted; border: 1px solid $line; border-radius: 12px; padding: 3px 12px; }
QPushButton#collapse:hover { border-color: $accent; color: $primary; }
QScrollArea { background: transparent; border: 0; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: $line; border-radius: 4px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: $line; border-radius: 4px; min-width: 28px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QTableWidget { background: transparent; border: 0; gridline-color: $line; }
QHeaderView::section { background: transparent; color: $muted; border: 0; border-bottom: 1px solid $line; padding: 6px; font-weight: 500; }
QTextBrowser { background: $card; border: 1px solid $line; border-radius: 12px; padding: 8px; }
""")


def build_stylesheet() -> str:
    return _QSS.substitute(
        bg=Colors.bg, card=Colors.card, text=Colors.text, muted=Colors.muted, line=Colors.line,
        primary=Colors.primary, accent=Colors.accent, side=Colors.side, tint=Colors.tint,
    )
