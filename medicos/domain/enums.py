"""Enumeraciones del dominio. No dependen de Qt ni del backend."""
from __future__ import annotations

from enum import Enum
from typing import Iterable


class Status(Enum):
    OK = "ok"
    ATTENTION = "att"
    PRIORITY = "pri"

    @property
    def severity(self) -> int:
        return {"ok": 0, "att": 1, "pri": 2}[self.value]

    @property
    def label(self) -> str:
        return {
            "ok": "Normal",
            "att": "Atención preventiva",
            "pri": "Evaluación médica prioritaria",
        }[self.value]

    @property
    def short_label(self) -> str:
        return {"ok": "Normal", "att": "Atención", "pri": "Prioritaria"}[self.value]

    @property
    def symbol(self) -> str:
        return {"ok": "✓", "att": "!", "pri": "▲"}[self.value]

    @staticmethod
    def worst(statuses: Iterable["Status"]) -> "Status":
        best = Status.OK
        for s in statuses:
            if s.severity > best.severity:
                best = s
        return best


class Domain(Enum):
    CARDIOVASCULAR = "cardiovascular"
    MENTAL = "mental"
    GENERAL = "general"

    @property
    def label(self) -> str:
        return {"cardiovascular": "Cardiovascular", "mental": "Salud mental", "general": "General"}[self.value]


class Region(Enum):
    """Zonas interactivas del cuerpo. Para agregar una zona nueva: añade aquí,
    en `RegionGeometry` (ui/body_regions.py) y en `HealthService.region_summary`."""

    HEAD = "head"
    HEART = "heart"

    @property
    def title(self) -> str:
        return {"head": "Cabeza", "heart": "Corazón"}[self.value]

    @property
    def domain(self) -> Domain:
        return {"head": Domain.MENTAL, "heart": Domain.CARDIOVASCULAR}[self.value]
