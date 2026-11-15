"""Tema visual. Paleta de la guía de marca (#0A3D91, #1E6BFF, #7A869A, #D7DEE8, #FFFFFF)
más los azules marino del panel web. Para cambiar colores o fuentes edita SOLO este archivo."""
from __future__ import annotations

from string import Template

from PySide6.QtGui import QColor, QFont

from ..domain.enums import Status


class Colors:
    navy = "#0a2c6b"          # fondo del cuerpo
    navy_dark = "#071f4d"     # columna izquierda
    card = "#ffffff"
    text = "#0b2150"
    muted = "#55627a"
    line = "#d7dee8"
    primary = "#0a3d91"
    accent = "#1e6bff"
    ok = "#0f8a5f"
    att = "#b86e00"
    red = "#d92d20"
    bg = "#eef2f8"
    brand_gray = "#7a869a"    # gris de la guía de marca
    line_dark = "#1b3a73"
    live = "#34d399"


STATUS_COLOR = {Status.OK: Colors.ok, Status.ATTENTION: Colors.att}

# Si instalas la tipografía "Aerospace" de la guía de marca, se usará automáticamente en títulos.
BODY_FAMILIES = ["Inter", "Segoe UI", "Roboto", "Helvetica Neue", "Arial"]
HEAD_FAMILIES = ["Aerospace", "Space Grotesk", "Inter", "Segoe UI", "Roboto", "Helvetica Neue", "Arial"]


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
#leftcol { background: $navy_dark; }
#centercol { background: $navy; }
#rightcol { background: $card; }
#card { background: $card; border: 0; border-radius: 18px; }
#subcard { background: $bg; border: 1px solid $line; border-radius: 12px; }
#quote { background: $bg; border: 0; border-left: 3px solid $accent; border-radius: 0 10px 10px 0; }
#regioncard { background: $card; border: 1px solid $line; border-radius: 16px; }
#regioncard:hover { border-color: $accent; }
QPushButton#btn { background: $primary; color: #ffffff; border: 0; border-radius: 12px; padding: 11px 16px;
                  font-weight: 600; min-height: 24px; }
QPushButton#btn:hover { background: $accent; }
QPushButton#btn:disabled { background: $brand_gray; }
QPushButton#btng { background: $bg; color: $primary; border: 1px solid $line; border-radius: 12px; padding: 11px 16px;
                   font-weight: 600; min-height: 24px; }
QPushButton#btng:hover { border-color: $accent; }
QPushButton#btnw { background: #ffffff; color: $red; border: 0; border-radius: 12px; padding: 11px 16px; font-weight: 600; min-height: 24px; }
QPushButton#btnw:hover { background: #fde8e6; }
QPushButton#btnwg { background: rgba(255,255,255,38); color: #ffffff; border: 1px solid rgba(255,255,255,150);
                    border-radius: 12px; padding: 11px 16px; font-weight: 600; min-height: 24px; }
QPushButton#btnwg:hover { background: rgba(255,255,255,70); }
#emergency { background: $red; }
QScrollArea { background: transparent; border: 0; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: $line; border-radius: 4px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
""")


def build_stylesheet() -> str:
    return _QSS.substitute(
        navy=Colors.navy, navy_dark=Colors.navy_dark, card=Colors.card, bg=Colors.bg, line=Colors.line,
        primary=Colors.primary, accent=Colors.accent, red=Colors.red, brand_gray=Colors.brand_gray)
