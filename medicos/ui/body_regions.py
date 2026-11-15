"""Geometría de las zonas interactivas, en píxeles de `assets/body.png`.

Si cambias la imagen del cuerpo, solo ajusta estos números. Para agregar una
zona nueva: añade una entrada aquí (y la zona en `domain/enums.py::Region`)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from PySide6.QtCore import QPointF

from ..domain.enums import Region


@dataclass(frozen=True)
class RegionGeometry:
    center: QPointF        # centro de la zona
    ring_radius: float     # radio del aro de selección (y del acercamiento)
    hit_rx: float          # elipse de toque (ancho / 2)
    hit_ry: float          # elipse de toque (alto / 2)


REGION_GEOMETRY: Dict[Region, RegionGeometry] = {
    Region.HEAD: RegionGeometry(QPointF(1086, 324), ring_radius=176, hit_rx=150, hit_ry=200),
    Region.HEART: RegionGeometry(QPointF(1134, 804), ring_radius=176, hit_rx=140, hit_ry=150),
}
