"""Posición de cada zona sobre la imagen, en FRACCIONES (0-1) del ancho y alto de la imagen.
Así funciona con cualquier resolución. Si cambias assets/body.png, ajusta solo estos números."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..domain.enums import Region


@dataclass(frozen=True)
class RegionVisual:
    fx: float          # centro, fracción del ancho de la imagen
    fy: float          # centro, fracción del alto de la imagen
    ring: float        # diámetro del aro de selección, fracción del ancho de la imagen


REGION_VISUALS: Dict[Region, RegionVisual] = {
    Region.HEART: RegionVisual(0.51, 0.26, 0.13),
    Region.HEAD: RegionVisual(0.50, 0.105, 0.15),
}
