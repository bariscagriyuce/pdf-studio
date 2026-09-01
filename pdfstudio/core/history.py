"""Anlık görüntü (snapshot) tabanlı geri al / yinele yığını."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Snapshot:
    label: str
    data: bytes
    page_hint: int = 0


class History:
    """Belge baytlarının tam kopyalarını tutan basit ve güvenli undo yığını.

    Karmaşık ters-işlem mantığı yerine tam kopya kullanılır; PDF üzerinde
    yapılan her işlem (redaksiyon, sayfa taşıma, font gömme) böylece
    kayıpsız geri alınabilir.
    """

    def __init__(self, limit: int = 30):
        self.limit = limit
        self._undo: list[Snapshot] = []
        self._redo: list[Snapshot] = []

    def clear(self) -> None:
        self._undo.clear()
        self._redo.clear()

    def push(self, snap: Snapshot) -> None:
        self._undo.append(snap)
        if len(self._undo) > self.limit:
            self._undo.pop(0)
        self._redo.clear()

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def undo_label(self) -> str:
        return self._undo[-1].label if self._undo else ""

    def redo_label(self) -> str:
        return self._redo[-1].label if self._redo else ""

    def undo(self, current: Snapshot) -> Snapshot | None:
        if not self._undo:
            return None
        snap = self._undo.pop()
        self._redo.append(Snapshot(snap.label, current.data, current.page_hint))
        return snap

    def redo(self, current: Snapshot) -> Snapshot | None:
        if not self._redo:
            return None
        snap = self._redo.pop()
        self._undo.append(Snapshot(snap.label, current.data, current.page_hint))
        return snap

    def memory_usage(self) -> int:
        return sum(len(s.data) for s in self._undo) + sum(len(s.data) for s in self._redo)
