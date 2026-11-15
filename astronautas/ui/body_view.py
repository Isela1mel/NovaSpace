"""Cuerpo translúcido interactivo: puntos tocables, acercamiento animado y aro que late."""
from __future__ import annotations

import math
import time
from typing import Dict, Optional, Tuple

from PySide6.QtCore import QEasingCurve, QPointF, QRectF, QTimer, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QBrush, QColor, QFontMetricsF, QPainter, QPen, QPixmap, QRadialGradient
from PySide6.QtWidgets import QWidget

from ..domain.enums import Region, Status
from .body_regions import REGION_VISUALS
from .theme import STATUS_COLOR, Colors, make_font, qcolor


class Hotspot:
    """Datos para dibujar el punto de una zona."""

    def __init__(self, status: Status, short_name: str, call: str):
        self.status, self.short_name, self.call = status, short_name, call


class BodyView(QWidget):
    region_clicked = Signal(object)      # Region
    background_clicked = Signal()

    ZOOM_MS = 900
    DOT_R = 23.0

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(280, 320)

        base = QPixmap(str(image_path))
        self._has_image = not base.isNull()
        self._levels: Dict[float, QPixmap] = {}
        if self._has_image:
            self._levels[1.0] = base
            for lv in (0.5, 0.25):      # niveles reducidos: evitan parpadeos al alejar la imagen
                self._levels[lv] = base.scaled(int(base.width() * lv), int(base.height() * lv),
                                               Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._img_w, self._img_h = float(base.width()), float(base.height())
        else:
            self._img_w, self._img_h = 736.0, 1008.0

        self._hotspots: Dict[Region, Hotspot] = {}
        self._label_rects: Dict[Region, QRectF] = {}
        self._mode: Optional[Region] = None
        self._ring_region: Optional[Region] = None
        self._hover: Optional[Region] = None
        self._bpm = 76
        self._t = 1.0
        self._from: Optional[Tuple[float, float, float]] = None

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self.ZOOM_MS)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.valueChanged.connect(self._on_anim)

        self._t0 = time.perf_counter()
        self._pulse = QTimer(self)
        self._pulse.setInterval(33)
        self._pulse.timeout.connect(self.update)
        self._pulse.start()

    # ---------- API pública ----------
    def set_hotspots(self, hotspots: Dict[Region, Hotspot]) -> None:
        self._hotspots = dict(hotspots)
        self.update()

    def set_bpm(self, bpm: int) -> None:
        self._bpm = max(30, int(bpm))

    def zoom_to(self, region: Optional[Region]) -> None:
        if region is self._mode:
            return
        self._from = self._current()
        if region is not None:
            self._ring_region = region
        self._mode = region
        self._t = 0.0
        self._anim.stop()
        self._anim.start()

    # ---------- geometría ----------
    def _box(self) -> Tuple[float, float, float, float]:
        """Rectángulo (l, t, ancho, alto) donde cabe la imagen sin acercar."""
        W, H = float(self.width()), float(self.height())
        ratio = self._img_h / self._img_w
        bh = min(H, W * ratio)
        bw = bh / ratio
        return (W - bw) / 2, (H - bh) / 2, bw, bh

    def _target(self, region: Optional[Region]) -> Tuple[float, float, float]:
        """(k, tx, ty): pantalla = (tx + k·x, ty + k·y)."""
        if region is None:
            return 1.0, 0.0, 0.0
        W, H = float(self.width()), float(self.height())
        l, t, bw, bh = self._box()
        g = REGION_VISUALS[region]
        px, py = l + g.fx * bw, t + g.fy * bh
        desired = 0.62 * min(W, H * 0.75)                  # diámetro del aro en pantalla
        k = max(2.0, min(6.0, desired / (g.ring * bw)))
        return k, W / 2 - k * px, H * 0.42 - k * py

    def _current(self) -> Tuple[float, float, float]:
        target = self._target(self._mode)
        if self._from is None or self._t >= 1.0:
            return target
        t = self._t
        return tuple(a + (b - a) * t for a, b in zip(self._from, target))   # type: ignore[return-value]

    def _on_anim(self, value) -> None:
        self._t = float(value)
        if self._t >= 1.0:
            self._from = None
        self.update()

    def _zoom_amount(self) -> float:
        return self._t if self._mode is not None else 1.0 - self._t

    def _to_screen(self, region: Region, params: Tuple[float, float, float]) -> QPointF:
        k, tx, ty = params
        l, t, bw, bh = self._box()
        g = REGION_VISUALS[region]
        return QPointF(tx + k * (l + g.fx * bw), ty + k * (t + g.fy * bh))

    def _period(self) -> float:
        return 60.0 / self._bpm

    # ---------- pintura ----------
    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
                         | QPainter.RenderHint.TextAntialiasing)
        p.fillRect(self.rect(), QColor(Colors.navy))
        params = self._current()
        amt = self._zoom_amount()
        now = time.perf_counter() - self._t0

        self._paint_image(p, params)
        self._paint_vignette(p)
        if self._ring_region is not None and amt > 0.01:
            self._paint_glow(p, self._ring_region, params, amt, now)
        fade = max(0.0, 1.0 - amt * 3.3)
        self._label_rects = {}
        if fade > 0.01:
            for region, info in self._hotspots.items():
                self._paint_hotspot(p, region, info, self._to_screen(region, params), fade, now)

    def _paint_image(self, p: QPainter, params) -> None:
        if not self._has_image:
            p.setPen(qcolor("#ffffff"))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Falta assets/body.png")
            return
        k, tx, ty = params
        l, t, bw, bh = self._box()
        level = 1.0
        for cand in (0.25, 0.5, 1.0):
            if self._img_w * cand >= k * bw:
                level = cand
                break
        pm = self._levels[level]
        dst = QRectF(tx + k * l, ty + k * t, k * bw, k * bh)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)   # el negro de la imagen se funde con el azul
        p.drawPixmap(dst, pm, QRectF(0, 0, pm.width(), pm.height()))
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

    def _paint_vignette(self, p: QPainter) -> None:
        W, H = float(self.width()), float(self.height())
        grad = QRadialGradient(QPointF(W / 2, H / 2), max(W, H) * 0.7)
        grad.setColorAt(0.55, QColor(6, 26, 66, 0))
        grad.setColorAt(1.0, QColor(6, 26, 66, 204))
        p.fillRect(self.rect(), QBrush(grad))

    def _paint_glow(self, p: QPainter, region: Region, params, amt: float, now: float) -> None:
        k = params[0]
        l, t, bw, bh = self._box()
        c = self._to_screen(region, params)
        pulse = 1.0 + 0.04 * (1.0 - math.cos(2 * math.pi * now / self._period()))
        r = REGION_VISUALS[region].ring * bw * k / 2 * pulse
        color = QColor(STATUS_COLOR[self._hotspots[region].status] if region in self._hotspots else Colors.accent)
        p.save()
        p.setOpacity(max(0.0, min(1.0, (amt - 0.6) / 0.4)))
        glow = QRadialGradient(c, r * 1.4)
        a, b, z = QColor(color), QColor(color), QColor(color)
        a.setAlpha(30); b.setAlpha(110); z.setAlpha(0)
        glow.setColorAt(0.0, a)
        glow.setColorAt(0.71, b)
        glow.setColorAt(1.0, z)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(c, r * 1.4, r * 1.4)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(color, 3))
        p.drawEllipse(c, r, r)
        p.restore()

    def _paint_hotspot(self, p: QPainter, region: Region, info: Hotspot, pos: QPointF, opacity: float, now: float) -> None:
        color = QColor(STATUS_COLOR[info.status])
        ph = (now % self._period()) / self._period()
        hover = self._hover is region
        r = self.DOT_R + (2.0 if hover else 0.0)
        p.save()
        p.setOpacity(opacity)
        ring = QColor("white")
        ring.setAlpha(int(170 * (1.0 - ph)))
        p.setPen(QPen(ring, 2))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(pos, r + 18 * ph, r + 18 * ph)
        p.setPen(QPen(QColor("white"), 3))
        p.setBrush(color)
        p.drawEllipse(pos, r, r)
        p.setPen(QColor("white"))
        p.setFont(make_font(13, True))
        p.drawText(QRectF(pos.x() - r, pos.y() - r, 2 * r, 2 * r), Qt.AlignmentFlag.AlignCenter, info.status.symbol)
        self._paint_label(p, region, info, pos)
        p.restore()

    def _paint_label(self, p: QPainter, region: Region, info: Hotspot, pos: QPointF) -> None:
        f1, f2 = make_font(9.5, True), make_font(8.5)
        m1, m2 = QFontMetricsF(f1), QFontMetricsF(f2)
        t1 = f"{info.short_name} · {info.status.label}"
        w = max(m1.horizontalAdvance(t1), m2.horizontalAdvance(info.call)) + 24
        h = m1.height() + m2.height() + 12
        W, H = float(self.width()), float(self.height())
        x = pos.x() + 31                                    # a la derecha del punto
        y = pos.y() - h / 2
        if x + w > W - 8:                                   # si no cabe: a la izquierda
            x = pos.x() - 31 - w
        if x < 8:                                           # si tampoco: debajo
            x, y = pos.x() - w / 2, pos.y() + 34
        x = max(8.0, min(W - w - 8, x))
        y = max(8.0, min(H - h - 8, y))
        rect = QRectF(x, y, w, h)
        self._label_rects[region] = rect
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 90))
        p.drawRoundedRect(rect.translated(0, 3), 14, 14)
        p.setBrush(QColor(Colors.card))
        p.drawRoundedRect(rect, 14, 14)
        p.setFont(f1)
        p.setPen(QColor(Colors.text))
        p.drawText(QRectF(x + 12, y + 6, w - 24, m1.height()), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, t1)
        p.setFont(f2)
        p.setPen(QColor(Colors.muted))
        p.drawText(QRectF(x + 12, y + 6 + m1.height(), w - 24, m2.height()),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, info.call)

    # ---------- interacción ----------
    def _region_at(self, pos: QPointF) -> Optional[Region]:
        if self._mode is not None or self._zoom_amount() > 0.2:
            return None
        params = self._current()
        for region in self._hotspots:
            c = self._to_screen(region, params)
            if math.hypot(pos.x() - c.x(), pos.y() - c.y()) <= self.DOT_R + 4:
                return region
            rect = self._label_rects.get(region)
            if rect is not None and rect.contains(pos):
                return region
        return None

    def mouseMoveEvent(self, e) -> None:
        hover = self._region_at(e.position())
        self._hover = hover
        self.setCursor(Qt.CursorShape.PointingHandCursor if hover else Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(e)

    def leaveEvent(self, e) -> None:
        self._hover = None
        super().leaveEvent(e)

    def mousePressEvent(self, e) -> None:
        if e.button() != Qt.MouseButton.LeftButton:
            return
        if self._mode is None:
            region = self._region_at(e.position())
            if region is not None:
                self.region_clicked.emit(region)
        else:
            params = self._current()
            c = self._to_screen(self._mode, params)
            r = REGION_VISUALS[self._mode].ring * self._box()[2] * params[0] / 2
            if math.hypot(e.position().x() - c.x(), e.position().y() - c.y()) > r:
                self.background_clicked.emit()

    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key.Key_Escape:
            self.background_clicked.emit()
        else:
            super().keyPressEvent(e)
