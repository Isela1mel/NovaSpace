"""Tarjeta de una opción del menú (Astronautas / Médicos): cristal oscuro sobre la imagen,
se ilumina al pasar el mouse o al enfocarla con Tab; Enter / Espacio / clic la abren."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .registry import AppEntry
from .theme import Colors, make_font


def _mix(a: QColor, b: QColor, t: float) -> QColor:
    return QColor(*(round(x + (y - x) * t) for x, y in
                    ((a.red(), b.red()), (a.green(), b.green()), (a.blue(), b.blue()), (a.alpha(), b.alpha()))))


class RoleCard(QFrame):
    clicked = Signal(str)            # key de la app

    def __init__(self, entry: AppEntry, parent=None):
        super().__init__(parent)
        self.entry = entry
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAccessibleName(f"{entry.title}: {entry.tagline}")
        self._hover = 0.0
        self._kbd_focus = False          # true solo si se llegó con Tab (no con el mouse)
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(160)
        self._anim.valueChanged.connect(self._set_hover)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(6)

        texts = QVBoxLayout()
        texts.setSpacing(0)
        self._title = QLabel(entry.title)
        self._title.setFont(make_font(21, True, True))
        self._title.setStyleSheet("color: #ffffff;")
        self._tag = QLabel(entry.tagline)
        self._tag.setFont(make_font(11))
        self._tag.setStyleSheet(f"color: {Colors.muted};")
        texts.addStretch(1)
        texts.addWidget(self._title)
        texts.addWidget(self._tag)
        texts.addStretch(1)
        root.addLayout(texts)

        self._features = QLabel("<br>".join(
            f"<span style='color:{Colors.ok}'>✓</span>&nbsp;&nbsp;{f}" for f in entry.features))
        self._features.setTextFormat(Qt.TextFormat.RichText)
        self._features.setFont(make_font(10.5))
        self._features.setStyleSheet("color: #e6eefc;")
        self._features.setVisible(bool(entry.features))
        root.addSpacing(4)
        root.addWidget(self._features)
        root.addStretch(1)

        self._cta = QLabel(f"Entrar como {entry.title[:-1].lower() if entry.title.endswith('s') else entry.title.lower()}  →")
        self._cta.setFont(make_font(10.5, True))
        self._cta.setStyleSheet(f"color: #ffffff; background: {Colors.accent}; border-radius: 10px; padding: 5px 12px;")
        root.addWidget(self._cta, 0, Qt.AlignmentFlag.AlignLeft)

    # ---- distribución ----
    def set_compact(self, compact: bool) -> None:
        """En tarjetas bajitas se oculta la lista de puntos."""
        self._features.setVisible(not compact)

    # ---- animación de hover ----
    def _set_hover(self, v) -> None:
        self._hover = float(v)
        self.update()

    def _animate_to(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._hover)
        self._anim.setEndValue(target)
        self._anim.start()

    def enterEvent(self, e) -> None:
        self._animate_to(1.0)
        super().enterEvent(e)

    def leaveEvent(self, e) -> None:
        self._animate_to(0.0)
        super().leaveEvent(e)

    def focusInEvent(self, e) -> None:
        self._kbd_focus = e.reason() in (Qt.FocusReason.TabFocusReason, Qt.FocusReason.BacktabFocusReason)
        self.update()
        super().focusInEvent(e)

    def focusOutEvent(self, e) -> None:
        self._kbd_focus = False
        self.update()
        super().focusOutEvent(e)

    # ---- pintura ----
    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = max(self._hover, 1.0 if self._kbd_focus else 0.0)
        fill = _mix(QColor(7, 24, 60, 165), QColor(14, 48, 112, 205), t)
        border = _mix(QColor(255, 255, 255, 70), QColor(Colors.accent), t)
        p.setBrush(fill)
        p.setPen(QPen(border, 1.5 + 0.8 * t))
        p.drawRoundedRect(QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5), 20, 20)

    # ---- interacción ----
    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton and self.rect().contains(e.position().toPoint()):
            self.clicked.emit(self.entry.key)
        super().mouseReleaseEvent(e)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.clicked.emit(self.entry.key)
        else:
            super().keyPressEvent(e)
