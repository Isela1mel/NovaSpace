"""Cuerpo interactivo con acercamiento animado (como la app móvil)."""
from __future__ import annotations

import math
from typing import Dict, Optional

from PySide6.QtCore import QEasingCurve, QElapsedTimer, QPointF, QRectF, QTimer, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPixmap, QRadialGradient
from PySide6.QtWidgets import QWidget

from ..domain.enums import Region, Status
from .body_regions import REGION_GEOMETRY
from .theme import STATUS_COLOR, Colors, make_font, qcolor

_Params = tuple  # (anchor: QPointF, center: QPointF, scale: float)


def _heart_path() -> QPainterPath:
    """Corazón en coordenadas unitarias (ancho ≈ 2, alto ≈ 2)."""
    path = QPainterPath(QPointF(0, -0.35))
    path.cubicTo(QPointF(0.0, -0.95), QPointF(-1.0, -0.95), QPointF(-1.0, -0.25))
    path.cubicTo(QPointF(-1.0, 0.35), QPointF(-0.3, 0.6), QPointF(0, 1.0))
    path.cubicTo(QPointF(0.3, 0.6), QPointF(1.0, 0.35), QPointF(1.0, -0.25))
    path.cubicTo(QPointF(1.0, -0.95), QPointF(0.0, -0.95), QPointF(0, -0.35))
    return path


class BodyView(QWidget):
    region_clicked = Signal(object)     # Region
    background_clicked = Signal()

    ZOOM_MS = 620

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(260, 260)

        base = QPixmap(str(image_path))
        self._has_image = not base.isNull()
        self._levels: Dict[float, QPixmap] = {}
        if self._has_image:
            self._levels[1.0] = base
            for lv in (0.5, 0.25):  # niveles reducidos: evitan el "aliasing" al alejar
                self._levels[lv] = base.scaled(int(base.width() * lv), int(base.height() * lv),
                                               Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._img_w, self._img_h = float(base.width()), float(base.height())
        else:
            self._img_w, self._img_h = 2208.0, 3024.0

        self._statuses: Dict[Region, Status] = {r: Status.OK for r in Region}
        self._mode: Optional[Region] = None       # zona acercada (None = cuerpo completo)
        self._ring_region: Optional[Region] = None
        self._hover: Optional[Region] = None
        self._t = 1.0
        self._from: Optional[_Params] = None
        self._heart = _heart_path()

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(self.ZOOM_MS)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.valueChanged.connect(self._on_anim)

        self._clock = QElapsedTimer()
        self._clock.start()
        self._pulse = QTimer(self)
        self._pulse.setInterval(33)
        self._pulse.timeout.connect(self.update)
        self._pulse.start()

    # ---------- API pública ----------
    def set_statuses(self, statuses: Dict[Region, Status]) -> None:
        self._statuses.update(statuses)
        self.update()

    def zoom_to(self, region: Optional[Region]) -> None:
        if region is self._mode:
            return
        self._from = self._current_params()
        if region is not None:
            self._ring_region = region
        self._mode = region
        self._t = 0.0
        self._anim.stop()
        self._anim.start()

    # ---------- geometría ----------
    def _fit_scale(self) -> float:
        return min(self.width() * 0.92 / self._img_w, self.height() * 0.95 / self._img_h)

    def _params_for(self, region: Optional[Region]) -> _Params:
        w, h = float(self.width()), float(self.height())
        if region is None:
            return QPointF(w / 2, h / 2), QPointF(self._img_w / 2, self._img_h / 2), self._fit_scale()
        g = REGION_GEOMETRY[region]
        scale = min(w * 0.78, h * 0.46) / (2 * g.ring_radius)
        return QPointF(w / 2, h * 0.30), QPointF(g.center), scale

    def _current_params(self) -> _Params:
        target = self._params_for(self._mode)
        if self._from is None or self._t >= 1.0:
            return target
        t = self._t
        (a0, c0, s0), (a1, c1, s1) = self._from, target
        lerp = lambda p, q: QPointF(p.x() + (q.x() - p.x()) * t, p.y() + (q.y() - p.y()) * t)
        scale = math.exp(math.log(s0) + (math.log(s1) - math.log(s0)) * t)
        return lerp(a0, a1), lerp(c0, c1), scale

    def _on_anim(self, value) -> None:
        self._t = float(value)
        if self._t >= 1.0:
            self._from = None
        self.update()

    def _zoom_amount(self) -> float:
        return self._t if self._mode is not None else 1.0 - self._t

    def _to_screen(self, p: QPointF, params: _Params) -> QPointF:
        anchor, center, s = params
        return QPointF(anchor.x() + (p.x() - center.x()) * s, anchor.y() + (p.y() - center.y()) * s)

    # ---------- pintura ----------
    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
                         | QPainter.RenderHint.TextAntialiasing)
        params = self._current_params()
        anchor, center, s = params
        amt = self._zoom_amount()
        phase = self._clock.elapsed() / 1000.0

        self._paint_body(p, params)
        self._paint_heart(p, params, phase)
        if amt < 0.999:
            for region in Region:
                self._paint_marker(p, region, params, (1.0 - amt), phase)
        if self._ring_region is not None and amt > 0.001:
            self._paint_ring(p, self._ring_region, params, amt)

    def _paint_body(self, p: QPainter, params: _Params) -> None:
        anchor, center, s = params
        if not self._has_image:
            p.setPen(qcolor(Colors.muted))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Falta assets/body.png")
            return
        level = 1.0
        for cand in (0.25, 0.5, 1.0):
            if cand >= s:
                level = cand
                break
        p.save()
        p.translate(anchor)
        p.scale(s / level, s / level)
        p.translate(-center.x() * level, -center.y() * level)
        p.drawPixmap(0, 0, self._levels[level])
        p.restore()

    def _paint_heart(self, p: QPainter, params: _Params, phase: float) -> None:
        """Corazón dibujado sobre la imagen; late suavemente."""
        anchor, center, s = params
        g = REGION_GEOMETRY[Region.HEART]
        beat = abs(math.sin(phase * math.pi * 1.25)) ** 10
        radius = 78.0 * (1.0 + 0.07 * beat)
        c = self._to_screen(g.center, params)
        p.save()
        p.translate(c)
        p.scale(radius * s, radius * s)
        grad = QRadialGradient(QPointF(0, 0.1), 1.15)
        grad.setColorAt(0.0, QColor(90, 200, 255, 120))
        grad.setColorAt(0.65, QColor(30, 140, 255, 80))
        grad.setColorAt(1.0, QColor(30, 140, 255, 30))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor(150, 225, 255, 210), 0.05))
        p.drawPath(self._heart)
        p.setPen(QPen(QColor(200, 240, 255, 110), 0.035))
        p.setBrush(Qt.BrushStyle.NoBrush)
        inner = QPainterPath()
        inner.moveTo(-0.55, -0.35)
        inner.cubicTo(QPointF(-0.4, -0.6), QPointF(-0.1, -0.6), QPointF(0.0, -0.3))
        p.drawPath(inner)
        p.restore()

    def _paint_marker(self, p: QPainter, region: Region, params: _Params, opacity: float, phase: float) -> None:
        status = self._statuses[region]
        color = QColor(STATUS_COLOR[status])
        c = self._to_screen(REGION_GEOMETRY[region].center, params)
        hover = self._hover is region
        r = 20.0 + (3.0 if hover else 0.0)
        p.save()
        p.setOpacity(opacity)
        # onda de pulso
        k = (phase * 0.9 + (0.5 if region is Region.HEART else 0.0)) % 1.0
        pulse = QColor(color)
        pulse.setAlpha(int(110 * (1.0 - k)))
        p.setPen(QPen(pulse, 2.5))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(c, r + 22 * k, r + 22 * k)
        # círculo
        p.setPen(QPen(QColor("white"), 3))
        p.setBrush(color)
        p.drawEllipse(c, r, r)
        p.setPen(QColor("white"))
        p.setFont(make_font(14, True))
        p.drawText(QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r), Qt.AlignmentFlag.AlignCenter, status.symbol)
        p.restore()

    def _paint_ring(self, p: QPainter, region: Region, params: _Params, amount: float) -> None:
        g = REGION_GEOMETRY[region]
        color = QColor(STATUS_COLOR[self._statuses[region]])
        c = self._to_screen(g.center, params)
        r = g.ring_radius * params[2]
        p.save()
        p.setOpacity(amount)
        glow = QRadialGradient(c, r * 1.4)
        inner, edge, out = QColor(color), QColor(color), QColor(color)
        inner.setAlpha(20); edge.setAlpha(80); out.setAlpha(0)
        glow.setColorAt(0.0, inner)
        glow.setColorAt(0.71, edge)
        glow.setColorAt(1.0, out)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow))
        p.drawEllipse(c, r * 1.4, r * 1.4)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(color, 6))
        p.drawEllipse(c, r, r)
        p.restore()

    # ---------- interacción ----------
    def _region_at(self, pos: QPointF) -> Optional[Region]:
        params = self._current_params()
        anchor, center, s = params
        ax, ay = (pos.x() - anchor.x()) / s + center.x(), (pos.y() - anchor.y()) / s + center.y()
        for region in (Region.HEART, Region.HEAD):          # corazón primero (queda sobre el pecho)
            g = REGION_GEOMETRY[region]
            marker = self._to_screen(g.center, params)
            near_marker = math.hypot(pos.x() - marker.x(), pos.y() - marker.y()) <= 26
            inside = ((ax - g.center.x()) / g.hit_rx) ** 2 + ((ay - g.center.y()) / g.hit_ry) ** 2 <= 1.0
            if near_marker or inside:
                return region
        return None

    def mouseMoveEvent(self, e) -> None:
        if self._mode is None:
            hover = self._region_at(e.position())
            if hover is not self._hover:
                self._hover = hover
            self.setCursor(Qt.CursorShape.PointingHandCursor if hover else Qt.CursorShape.ArrowCursor)
        else:
            self._hover = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
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
            g = REGION_GEOMETRY[self._mode]
            c = self._to_screen(g.center, self._current_params())
            if math.hypot(e.position().x() - c.x(), e.position().y() - c.y()) > g.ring_radius * self._current_params()[2]:
                self.background_clicked.emit()

    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key.Key_Escape:
            self.background_clicked.emit()
        else:
            super().keyPressEvent(e)
