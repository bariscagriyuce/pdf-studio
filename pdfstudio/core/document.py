"""Belge modeli: PyMuPDF belgesini sarmalar, undo/redo ve sinyalleri yönetir."""
from __future__ import annotations

import os
from contextlib import contextmanager

import pymupdf
from PySide6.QtCore import QObject, Signal

from .history import History, Snapshot


class DocumentError(Exception):
    pass


class PasswordRequired(DocumentError):
    pass


class PdfDocument(QObject):
    """Açık PDF belgesi.

    Sinyaller:
        structureChanged  -> sayfa sayısı/sırası değişti, her şey yeniden çizilmeli
        pagesChanged(list) -> sadece verilen sayfalar yeniden çizilmeli
        dirtyChanged(bool) -> kaydedilmemiş değişiklik durumu
        historyChanged     -> undo/redo düğmeleri güncellenmeli
        opened / closed
    """

    structureChanged = Signal()
    pagesChanged = Signal(list)
    dirtyChanged = Signal(bool)
    historyChanged = Signal()
    opened = Signal()
    closed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc: pymupdf.Document | None = None
        self.path: str | None = None
        self.password: str | None = None
        self._dirty = False
        self.history = History()
        self.version = 0  # render önbelleğini geçersiz kılmak için sayaç

    # ------------------------------------------------------------------ durum
    @property
    def doc(self) -> pymupdf.Document | None:
        return self._doc

    @property
    def is_open(self) -> bool:
        return self._doc is not None

    @property
    def page_count(self) -> int:
        return self._doc.page_count if self._doc else 0

    @property
    def dirty(self) -> bool:
        return self._dirty

    def set_dirty(self, value: bool) -> None:
        if self._dirty != value:
            self._dirty = value
            self.dirtyChanged.emit(value)

    @property
    def display_name(self) -> str:
        if self.path:
            return os.path.basename(self.path)
        return "Adsız.pdf"

    def page(self, index: int) -> pymupdf.Page:
        if not self._doc:
            raise DocumentError("Açık belge yok")
        return self._doc[index]

    def page_size(self, index: int) -> tuple[float, float]:
        """Görüntülenen sayfa boyutu (nokta).

        PyMuPDF'te ``page.rect`` dönüşü zaten uygulanmış hâlde döner, bu yüzden
        ayrıca eksen değiştirmek gerekmez.
        """
        r = self._doc[index].rect
        return r.width, r.height

    # ------------------------------------------------------------------ açma
    def open(self, path: str, password: str | None = None) -> None:
        doc = pymupdf.open(path)
        if doc.needs_pass:
            if password is None or not doc.authenticate(password):
                doc.close()
                raise PasswordRequired("Belge parola korumalı")
        self._install(doc, path)
        self.password = password

    def open_bytes(self, data: bytes, name: str = "Adsız.pdf") -> None:
        doc = pymupdf.open("pdf", data)
        self._install(doc, None)
        self.path = None

    def new_blank(self, width: float = 595.0, height: float = 842.0, pages: int = 1) -> None:
        doc = pymupdf.open()
        for _ in range(max(1, pages)):
            doc.new_page(width=width, height=height)
        self._install(doc, None)
        self.set_dirty(True)

    def new_from_images(self, paths: list[str]) -> None:
        doc = pymupdf.open()
        for p in paths:
            img = pymupdf.open(p)
            pdfbytes = img.convert_to_pdf()
            img.close()
            src = pymupdf.open("pdf", pdfbytes)
            doc.insert_pdf(src)
            src.close()
        if doc.page_count == 0:
            doc.new_page()
        self._install(doc, None)
        self.set_dirty(True)

    def _install(self, doc: pymupdf.Document, path: str | None) -> None:
        if self._doc is not None:
            self._doc.close()
        self._doc = doc
        self.path = path
        self._dirty = False
        self.history.clear()
        self.version += 1
        self.dirtyChanged.emit(False)
        self.historyChanged.emit()
        self.opened.emit()
        self.structureChanged.emit()

    def close(self) -> None:
        if self._doc is not None:
            self._doc.close()
        self._doc = None
        self.path = None
        self._dirty = False
        self.history.clear()
        self.version += 1
        self.closed.emit()
        self.structureChanged.emit()

    # --------------------------------------------------------------- kaydetme
    def save(self, path: str | None = None, **opts) -> str:
        if not self._doc:
            raise DocumentError("Açık belge yok")
        target = path or self.path
        if not target:
            raise DocumentError("Hedef dosya belirtilmedi")

        same_file = self.path is not None and os.path.abspath(target) == os.path.abspath(self.path)
        kwargs = dict(garbage=4, deflate=True, clean=True)
        kwargs.update(opts)
        if same_file:
            # Aynı dosyanın üzerine yazarken PyMuPDF güvenli yolu kullanmalı.
            kwargs["incremental"] = kwargs.get("incremental", False)
            if not kwargs["incremental"]:
                data = self._doc.tobytes(**{k: v for k, v in kwargs.items() if k != "incremental"})
                with open(target, "wb") as fh:
                    fh.write(data)
            else:
                kwargs.pop("garbage", None)
                kwargs.pop("clean", None)
                kwargs.pop("deflate", None)
                self._doc.save(target, **kwargs)
        else:
            kwargs.pop("incremental", None)
            self._doc.save(target, **kwargs)

        self.path = target
        self.set_dirty(False)
        return target

    def export_bytes(self, **opts) -> bytes:
        return self._doc.tobytes(garbage=4, deflate=True, clean=True, **opts)

    # ------------------------------------------------------------ düzenleme
    def snapshot(self, label: str = "", page_hint: int = 0) -> Snapshot:
        return Snapshot(label, self._doc.tobytes(garbage=0, deflate=True), page_hint)

    @contextmanager
    def edit(self, label: str, pages: list[int] | None = None, structural: bool = False):
        """Bir düzenleme işlemini undo yığınına kaydederek çalıştırır.

        Kullanım:
            with doc.edit("Vurgu ekle", pages=[3]):
                page.add_highlight_annot(...)
        """
        if not self._doc:
            raise DocumentError("Açık belge yok")
        before = self.snapshot(label, pages[0] if pages else 0)
        try:
            yield self._doc
        except Exception:
            raise
        self.history.push(before)
        self.version += 1
        self.set_dirty(True)
        self.historyChanged.emit()
        if structural or pages is None:
            self.structureChanged.emit()
        else:
            self.pagesChanged.emit(list(pages))

    def _restore(self, snap: Snapshot) -> None:
        data = snap.data
        newdoc = pymupdf.open("pdf", data)
        old = self._doc
        self._doc = newdoc
        if old is not None:
            old.close()
        self.version += 1
        self.set_dirty(True)
        self.historyChanged.emit()
        self.structureChanged.emit()

    def undo(self) -> str:
        if not self.history.can_undo():
            return ""
        label = self.history.undo_label()
        snap = self.history.undo(self.snapshot(label))
        if snap:
            self._restore(snap)
        return label

    def redo(self) -> str:
        if not self.history.can_redo():
            return ""
        label = self.history.redo_label()
        snap = self.history.redo(self.snapshot(label))
        if snap:
            self._restore(snap)
        return label

    # ------------------------------------------------------------ meta veri
    def metadata(self) -> dict:
        return dict(self._doc.metadata or {}) if self._doc else {}

    def set_metadata(self, meta: dict) -> None:
        with self.edit("Meta veri", structural=True):
            self._doc.set_metadata(meta)

    def toc(self) -> list:
        return self._doc.get_toc(simple=False) if self._doc else []

    def set_toc(self, toc: list) -> None:
        with self.edit("Yer imleri", structural=True):
            self._doc.set_toc(toc)

    def permissions(self) -> int:
        return self._doc.permissions if self._doc else 0

    def is_encrypted(self) -> bool:
        return bool(self._doc.is_encrypted) if self._doc else False
