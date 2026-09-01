"""Sayfa görüntüleme: PyMuPDF pixmap -> QImage, LRU önbellekli."""
from __future__ import annotations

from collections import OrderedDict

import pymupdf
from PySide6.QtGui import QImage, QPixmap

BASE_DPI = 72.0


class PageRenderer:
    """Sayfa görüntülerini önbelleğe alan yardımcı.

    Anahtar: (belge_versiyonu, sayfa_no, zoom, ek_dönüş)
    """

    def __init__(self, document, max_items: int = 24, max_bytes: int = 512 * 1024 * 1024):
        self.document = document
        self.max_items = max_items
        self.max_bytes = max_bytes
        self._cache: OrderedDict[tuple, QImage] = OrderedDict()
        self._bytes = 0

    def clear(self) -> None:
        self._cache.clear()
        self._bytes = 0

    def invalidate_page(self, pno: int) -> None:
        for key in [k for k in self._cache if k[1] == pno]:
            img = self._cache.pop(key)
            self._bytes -= img.sizeInBytes()

    # ---------------------------------------------------------------- render
    def image(self, pno: int, zoom: float, extra_rotation: int = 0, dpr: float = 1.0) -> QImage:
        key = (self.document.version, pno, round(zoom, 4), extra_rotation % 360, round(dpr, 2))
        img = self._cache.get(key)
        if img is not None:
            self._cache.move_to_end(key)
            return img
        img = self._render(pno, zoom * dpr, extra_rotation)
        img.setDevicePixelRatio(dpr)
        self._cache[key] = img
        self._bytes += img.sizeInBytes()
        self._trim()
        return img

    def pixmap(self, pno: int, zoom: float, extra_rotation: int = 0, dpr: float = 1.0) -> QPixmap:
        return QPixmap.fromImage(self.image(pno, zoom, extra_rotation, dpr))

    def thumbnail(self, pno: int, max_side: int = 180) -> QImage:
        page = self.document.page(pno)
        r = page.rect
        long_side = max(r.width, r.height) or 1.0
        zoom = max_side / long_side
        return self._render(pno, zoom, 0)

    def _render(self, pno: int, zoom: float, extra_rotation: int) -> QImage:
        page = self.document.page(pno)
        mat = pymupdf.Matrix(zoom, zoom)
        if extra_rotation:
            mat = mat * pymupdf.Matrix(extra_rotation)
        try:
            pm = page.get_pixmap(matrix=mat, alpha=False, annots=True)
        except Exception:
            pm = page.get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False)
        fmt = QImage.Format_RGB888 if pm.n == 3 else QImage.Format_Grayscale8
        img = QImage(pm.samples, pm.width, pm.height, pm.stride, fmt)
        return img.copy()  # PyMuPDF tamponu serbest bırakacağı için kopya şart

    def _trim(self) -> None:
        while self._cache and (len(self._cache) > self.max_items or self._bytes > self.max_bytes):
            _, img = self._cache.popitem(last=False)
            self._bytes -= img.sizeInBytes()
