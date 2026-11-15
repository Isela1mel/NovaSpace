"""Datos simulados (los mismos de la pantalla web 'Mi cuerpo')."""
from __future__ import annotations

import math
import random
import time
from typing import Dict

from ..domain.enums import Region, Status
from ..domain.models import (
    EmergencyAck, MeasureResult, RegionReport, SignalReading, VoiceInfo, WatchStatus,
)
from .repository import BodyRepository


class MockBodyRepository(BodyRepository):
    def get_reports(self) -> Dict[Region, RegionReport]:
        heart = RegionReport(
            region=Region.HEART, name="Corazón y circulación", short_name="Corazón", status=Status.ATTENTION,
            call="Algo cambió: latidos en reposo altos",
            summary="tus latidos en reposo están más altos que tu normal.",
            what="Tus latidos en reposo llevan 3 días más altos de lo normal.",
            note="Es una señal de seguimiento estimada, no un diagnóstico.",
            readings=[SignalReading("↑", "Latidos en reposo", "76 bpm (tu normal: 62)"),
                      SignalReading("↓", "Variabilidad del ritmo", "más baja de lo habitual")],
            chart_title="Latidos en reposo, últimos 7 días (bpm)",
            values=[62, 61, 63, 66, 70, 73, 76], baseline=62,
            todo=["Siéntate y descansa 10 minutos respirando lento.",
                  "Mide otra vez en reposo.",
                  "Si sientes dolor de pecho, mareo o falta de aire, usa EMERGENCIA o avisa a un compañero."],
            function="Mueve la sangre y el oxígeno por todo tu cuerpo. En el espacio se adapta a la microgravedad y puede trabajar distinto.",
            can_measure=True)
        head = RegionReport(
            region=Region.HEAD, name="Bienestar emocional", short_name="Emocional", status=Status.OK,
            call="Todo en orden", summary="todo en orden.",
            what="No hay problema con esta parte: tu ánimo y tu estrés están dentro de lo habitual.",
            note="Representa tu bienestar emocional, no el cerebro.",
            readings=[SignalReading("✓", "Ánimo", "estable"), SignalReading("✓", "Estrés", "bajo"),
                      SignalReading("✓", "Descanso", "6.8 h anoche")],
            chart_title="Ánimo, últimos 7 días (0 a 10)",
            values=[7, 7, 6, 7, 7, 7, 7], baseline=7,
            todo=["Sigue con tu rutina de descanso y ejercicio.", "Si te sientes diferente, cuéntalo a tu tripulación."],
            function="Cómo llevas el ánimo, el estrés y el descanso. El aislamiento y el encierro pueden afectarlos.")
        return {Region.HEART: heart, Region.HEAD: head}

    def get_watch_status(self) -> WatchStatus:
        return WatchStatus(True, "Reloj conectado · en vivo")

    def get_voice_info(self) -> VoiceInfo:
        return VoiceInfo(
            title="Asistente por voz", soon_text="Próximamente · etapa futura",
            headline="Una plática hablada: tú hablas y el asistente te responde con voz.",
            lead="Aún no escucha ni responde. Aquí queda indicado lo que queremos que haga.",
            abilities=["Escucha tu voz y responde hablando, sin teclear ni tocar la pantalla.",
                       "Te cuenta cómo vas: consulta tus indicadores y explica resultados y tendencias en palabras simples.",
                       "Te guía paso a paso para hacer una medición.",
                       "Te recuerda las evaluaciones pendientes.",
                       "Responde dudas sobre los riesgos del vuelo espacial y da orientación preventiva con fuentes científicas.",
                       "Te ayuda a decidir cuándo pedir asistencia médica o usar EMERGENCIA."],
            examples=["“¿Por qué me avisó el corazón?”", "“Guíame para medir mi presión.”",
                      "“¿Qué tengo pendiente hoy?”", "“Me siento más cansado, ¿es normal?”"],
            rules=["No diagnostica ni propone tratamientos fuera de protocolos validados.",
                   "Dice de dónde viene su información.",
                   "Solo escucha cuando tú lo activas.",
                   "Funciona sin conexión con una versión local cuando no hay comunicación con la Tierra."],
            build_note="Reconocimiento de voz y respuesta hablada, con recuperación de información sobre "
                       "documentación científica (RAG con búsqueda híbrida).")

    def read_live_bpm(self) -> int:
        return 76 + round(math.sin(time.time() / 4) * 2 + (random.random() - .5) * 2)

    def measure_resting_bpm(self) -> MeasureResult:
        time.sleep(2.5)       # simula la espera del reloj
        return MeasureResult(75, "Resultado en reposo: 75 bpm. Sigue un poco alto: repite en 30 minutos y "
                                 "observa cómo te sientes.")

    def send_emergency(self, bpm: int) -> EmergencyAck:
        return EmergencyAck(True, "Tu tripulación y control de misión fueron avisados (simulado).")

    def cancel_emergency(self, reason: str) -> None:
        return None
