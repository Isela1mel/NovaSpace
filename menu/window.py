"""Ventana del MENÚ: imagen de fondo, título y una tarjeta por app.
Distribución responsiva (se decide por el tamaño de la ventana):
   ancho  → una tarjeta a cada lado del planeta
   medio  → dos tarjetas lado a lado, abajo
   angosto→ tarjetas apiladas, abajo"""
from __future__ import annotations

from typing import List

from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QLabel, QMainWindow

from .background import SpaceBackground
from .registry import AppEntry
from .role_card import RoleCard
from .theme import BACKGROUND_IMAGE, Colors, make_font

WIDE_MIN_W, WIDE_MIN_H = 1000, 560
MEDIUM_MIN_W = 700


class MenuWindow(QMainWindow):
    app_chosen = Signal(str)         # key de la app elegida

    def __init__(self, apps: List[AppEntry]):
        super().__init__()
        self.setWindowTitle("NovaSpace")
        self.resize(1180, 740)
        self.setMinimumSize(640, 560)

        self._bg = SpaceBackground(BACKGROUND_IMAGE)
        self.setCentralWidget(self._bg)

        self._title = QLabel("Vita Orbital", self._bg)
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet("color: #ffffff; background: transparent;")
        self._subtitle = QLabel("Elige cómo quieres entrar", self._bg)
        self._subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle.setStyleSheet(f"color: {Colors.muted}; background: transparent;")
        self._footer = QLabel("Prototipo con datos simulados   ·   Tab para moverte · Enter para entrar · 1 Astronautas · 2 Médicos",
                              self._bg)
        self._footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer.setFont(make_font(9))
        self._footer.setStyleSheet("color: rgba(255,255,255,150); background: transparent;")

        self._cards: List[RoleCard] = []
        for i, entry in enumerate(apps):
            card = RoleCard(entry, self._bg)
            card.clicked.connect(self.app_chosen.emit)
            self._cards.append(card)
            QShortcut(QKeySequence(str(i + 1)), self, activated=lambda k=entry.key: self.app_chosen.emit(k))
        if self._cards:
            self._cards[0].setFocus(Qt.FocusReason.OtherFocusReason)   # Enter funciona, sin resaltar
        self._relayout()

    # ---- distribución responsiva ----
    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._relayout()

    def _relayout(self) -> None:
        W, H = self._bg.width(), self._bg.height()
        margin = max(16, int(W * 0.03))

        # título (crece con la ventana, con límites)
        self._title.setFont(make_font(max(24, min(44, W / 24)), True, True))
        self._subtitle.setFont(make_font(max(10.5, min(15, W / 70))))
        top = int(H * 0.055)
        th = self._title.sizeHint().height()
        sh = self._subtitle.sizeHint().height()
        self._title.setGeometry(0, top, W, th)
        self._subtitle.setGeometry(0, top + th, W, sh)

        footer_h = 26
        self._footer.setGeometry(0, H - footer_h - 8, W, footer_h)
        n = len(self._cards)
        if n == 0:
            return
        gap = 16

        if W >= WIDE_MIN_W and H >= WIDE_MIN_H:                       # ANCHO: a los lados del planeta
            cw = max(260, min(340, int(W * 0.25)))
            ch = 170
            y = int(H * 0.58) - ch // 2
            xs = [margin * 2, W - margin * 2 - cw]
            for i, card in enumerate(self._cards):
                card.set_compact(False)
                card.setGeometry(QRect(xs[i % 2], y, cw, ch))
        elif W >= MEDIUM_MIN_W:                                       # MEDIO: lado a lado, abajo
            cw = (W - 2 * margin - gap * (n - 1)) // n
            ch = 150
            y = H - footer_h - 16 - ch
            for i, card in enumerate(self._cards):
                card.set_compact(False)
                card.setGeometry(QRect(margin + i * (cw + gap), y, cw, ch))
        else:                                                         # ANGOSTO: apiladas, abajo
            cw = W - 2 * margin
            ch = 110
            y = H - footer_h - 16 - (n * ch + (n - 1) * gap)
            for i, card in enumerate(self._cards):
                card.set_compact(True)
                card.setGeometry(QRect(margin, y + i * (ch + gap), cw, ch))
