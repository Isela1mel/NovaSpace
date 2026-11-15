"""Ejecuta funciones lentas (llamadas al backend) en un hilo y devuelve el resultado
al hilo de la interfaz de forma segura."""
from __future__ import annotations

from typing import Any, Callable, Optional, Set

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

Callback = Optional[Callable[[Any], None]]


class _Dispatcher(QObject):
    """Vive en el hilo de la interfaz; entrega callbacks emitidos desde otros hilos."""
    deliver = Signal(object, object)

    def __init__(self) -> None:
        super().__init__()
        self.deliver.connect(self._call)

    def _call(self, fn, value) -> None:
        if fn is not None:
            fn(value)


_dispatcher: Optional[_Dispatcher] = None
_alive: Set["_Task"] = set()


class _Task(QRunnable):
    def __init__(self, fn: Callable[[], Any], ok: Callback, err: Callback):
        super().__init__()
        self.fn, self.ok, self.err = fn, ok, err
        self.setAutoDelete(False)

    def run(self) -> None:           # hilo secundario: NO tocar widgets aquí
        d = _dispatcher
        try:
            result = self.fn()
        except Exception as exc:     # noqa: BLE001
            d.deliver.emit(self.err, str(exc))
        else:
            d.deliver.emit(self.ok, result)
        finally:
            _alive.discard(self)


def run_async(fn: Callable[[], Any], ok: Callback = None, err: Callback = None) -> None:
    """Llama a run_async desde el hilo de la interfaz."""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = _Dispatcher()
    task = _Task(fn, ok, err)
    _alive.add(task)
    QThreadPool.globalInstance().start(task)
