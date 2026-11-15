"""Reglas de adaptación al tamaño de la ventana. Edita aquí para cambiar el reparto de columnas."""
from __future__ import annotations

from typing import Tuple


def clamp(value: float, low: float, high: float) -> int:
    return int(max(low, min(high, value)))


def column_widths(window_width: int) -> Tuple[int, int]:
    """(ancho columna izquierda, ancho columna derecha). La del centro ocupa el resto."""
    left = clamp(window_width * 0.23, 230, 320)
    right = clamp(window_width * 0.33, 320, 460)
    return left, right
