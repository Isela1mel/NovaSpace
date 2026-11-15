"""`python -m medicos` abre solo la app de médicos (sin menú)."""
import sys

from .app import run

sys.exit(run())
