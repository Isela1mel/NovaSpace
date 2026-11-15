"""Registro de secciones. Para añadir una opción de menú nueva:
1) crea una clase que herede de SectionView, 2) agrégala a SECTION_CLASSES,
3) inclúyela en config.ENABLED_SECTIONS."""
from typing import Dict, Type

from .alerts import AlertsSection
from .base import SectionView
from .context import ContextSection
from .indicators import IndicatorsSection
from .prediction import PredictionSection
from .psychological import PsychologicalSection
from .report import ReportSection
from .summary import SummarySection

SECTION_CLASSES: Dict[str, Type[SectionView]] = {
    cls.id: cls
    for cls in (SummarySection, IndicatorsSection, PsychologicalSection, PredictionSection,
                AlertsSection, ContextSection, ReportSection)
}
