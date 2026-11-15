"""Enumeraciones del dominio (sin Qt, sin backend)."""
from __future__ import annotations

from enum import Enum
from typing import Iterable


class Status(Enum):
    OK = "ok"
    ATTENTION = "att"

    @property
    def severity(self) -> int:
        return 0 if self is Status.OK else 1

    @property
    def label(self) -> str:
        return "Normal" if self is Status.OK else "Atención"

    @property
    def symbol(self) -> str:
        return "✓" if self is Status.OK else "!"

    @staticmethod
    def worst(statuses: Iterable["Status"]) -> "Status":
        best = Status.OK
        for s in statuses:
            if s.severity > best.severity:
                best = s
        return best


class Region(Enum):
    """Zonas tocables del cuerpo. Para añadir una: agrégala aquí, en `ui/body_regions.py`
    y entrega su `RegionReport` desde el repositorio."""

    HEART = "heart"
    HEAD = "head"
