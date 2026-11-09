"""Kenar panelleri: küçük resimler, yer imleri, açıklamalar, arama, formlar, görüntüler."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QMenu, QPushButton, QTableWidget,
                               QTableWidgetItem, QToolButton, QTreeWidget,
                               QTreeWidgetItem, QVBoxLayout, QWidget)

from ..i18n import _, _n  # noqa: F401
from . import icons
from .widgets import HLine


# ---------------------------------------------------------------- küçük resimler
class ThumbnailPanel(QWidget):
    pageActivated = Signal(int)
    reorderRequested = Signal(list)
    commandRequested = Signal(str, list)   # komut adı, sayfa listesi

    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view
        self.document = view.document
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        bar = QHBoxLayout()
        bar.setContentsMargins(8, 6, 8, 6)
        bar.setSpacing(5)
        self.size_box = QComboBox()
        self.size_box.addItems([_("Küçük"), _("Orta"), _("Büyük")])
        self.size_box.setCurrentIndex(1)
        self.size_box.currentIndexChanged.connect(self._resize_icons)
        bar.addWidget(QLabel(_("Boyut")))
        bar.addWidget(self.size_box, 1)
        lay.addLayout(bar)
        lay.addWidget(HLine())

        self.list = QListWidget()
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setMovement(QListWidget.Static)
        self.list.setSpacing(8)
        self.list.setUniformItemSizes(False)
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list.setDragDropMode(QAbstractItemView.InternalMove)
        self.list.setMovement(QListWidget.Snap)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._menu)
        self.list.itemClicked.connect(self._activate)
        self.list.model().rowsMoved.connect(self._rows_moved)
        lay.addWidget(self.list, 1)

        self._sizes = {0: 96, 1: 140, 2: 200}
        self._pending: list[int] = []
        self._timer = QTimer(self)
        self._timer.setInterval(15)
        self._timer.timeout.connect(self._render_next)
        self._suppress = False

    def _icon_size(self) -> int:
        return self._sizes[self.size_box.currentIndex()]

    def reload(self):
        self._suppress = True
        self.list.clear()
        self._pending = []
        if not self.document.is_open:
            self._suppress = False
            return
        side = self._icon_size()
        self.list.setIconSize(QSize(side, side))
        for pno in range(self.document.page_count):
            it = QListWidgetItem(f"{pno + 1}")
            it.setData(Qt.UserRole, pno)
            it.setTextAlignment(Qt.AlignHCenter | Qt.AlignBottom)
            it.setSizeHint(QSize(side + 18, side + 30))
            ph = QPixmap(side, side)
            ph.fill(Qt.transparent)
            it.setIcon(QIcon(ph))
            self.list.addItem(it)
            self._pending.append(pno)
        self._suppress = False
        self._timer.start()

    def refresh_pages(self, pages):
        for pno in pages:
            if pno not in self._pending:
                self._pending.append(pno)
        self._timer.start()

    def _render_next(self):
        if not self._pending or not self.document.is_open:
            self._timer.stop()
            return
        for _x in range(2):
            if not self._pending:
                break
            pno = self._pending.pop(0)
            if pno >= self.list.count():
                continue
            try:
                img = self.view.renderer.thumbnail(pno, self._icon_size())
            except Exception:
                continue
            item = None
            for i in range(self.list.count()):
                if self.list.item(i).data(Qt.UserRole) == pno:
                    item = self.list.item(i)
                    break
            if item is not None:
                item.setIcon(QIcon(QPixmap.fromImage(img)))

    def _resize_icons(self):
        self.reload()

    def set_current(self, pno: int):
        for i in range(self.list.count()):
            if self.list.item(i).data(Qt.UserRole) == pno:
                self.list.setCurrentRow(i)
                self.list.scrollToItem(self.list.item(i))
                break

    def _activate(self, item):
        self.pageActivated.emit(int(item.data(Qt.UserRole)))

    def selected_pages(self) -> list[int]:
        return sorted(int(i.data(Qt.UserRole)) for i in self.list.selectedItems())

    def _rows_moved(self, *_args):
        if self._suppress:
            return
        order = [int(self.list.item(i).data(Qt.UserRole)) for i in range(self.list.count())]
        self.reorderRequested.emit(order)

    def _menu(self, pos):
        pages = self.selected_pages()
        if not pages:
            item = self.list.itemAt(pos)
            if item is None:
                return
            pages = [int(item.data(Qt.UserRole))]
        m = QMenu(self)
        entries = [
            (_("Sola döndür"), "rotate-left", "rotate_left"),
            (_("Sağa döndür"), "rotate-right", "rotate_right"),
            (None, None, None),
            (_("Boş sayfa ekle (önüne)"), "page-add", "insert_before"),
            (_("Boş sayfa ekle (arkasına)"), "page-add", "insert_after"),
            (_("Çoğalt"), "page-copy", "duplicate"),
            (_("PDF olarak dışa aktar"), "extract", "extract"),
            (_("Görüntü olarak kaydet"), "image", "export_image"),
            (None, None, None),
            (_("Sil"), "page-delete", "delete"),
        ]
        for label, ic, cmd in entries:
            if label is None:
                m.addSeparator()
                continue
            act = QAction(icons.icon(ic, "#c7cedd", 18), label, m)
            act.triggered.connect(lambda _x=False, c=cmd, p=pages: self.commandRequested.emit(c, p))
            m.addAction(act)
        m.exec(self.list.mapToGlobal(pos))


# ------------------------------------------------------------------- yer imleri
class OutlinePanel(QWidget):
    navigate = Signal(int)
    tocChanged = Signal(list)

    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        bar = QHBoxLayout()
        bar.setContentsMargins(8, 6, 8, 6)
        bar.setSpacing(5)
        for name, tip, slot in (("plus", _("Yer imi ekle"), self.add_bookmark),
                                ("text-edit", _("Yeniden adlandır"), self.rename_bookmark),
                                ("trash", _("Sil"), self.delete_bookmark)):
            b = QToolButton()
            b.setIcon(icons.icon(name, "#c7cedd", 17))
            b.setToolTip(tip)
            b.clicked.connect(slot)
            bar.addWidget(b)
        bar.addStretch(1)
        lay.addLayout(bar)
        lay.addWidget(HLine())

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._clicked)
        lay.addWidget(self.tree, 1)

    def reload(self):
        self.tree.clear()
        if not self.document.is_open:
            return
        toc = self.document.toc()
        stack: list[tuple[int, QTreeWidgetItem]] = []
        for entry in toc:
            level, title, page = entry[0], entry[1], entry[2]
            item = QTreeWidgetItem([f"{title}"])
            item.setData(0, Qt.UserRole, max(0, page - 1))
            item.setToolTip(0, _("{title}  →  sayfa {page}").format(title=title, page=page))
            while stack and stack[-1][0] >= level:
                stack.pop()
            if stack:
                stack[-1][1].addChild(item)
            else:
                self.tree.addTopLevelItem(item)
            stack.append((level, item))
        self.tree.expandAll()

    def _clicked(self, item, _col):
        pno = item.data(0, Qt.UserRole)
        if pno is not None:
            self.navigate.emit(int(pno))

    def _flat_toc(self) -> list:
        return self.document.toc()

    def add_bookmark(self):
        if not self.document.is_open:
            return
        from PySide6.QtWidgets import QInputDialog
        cur = self.window().view.current_page
        title, ok = QInputDialog.getText(self, _("Yer imi ekle"),
                                         _("Sayfa {0} için başlık:").format(cur + 1))
        if not ok or not title.strip():
            return
        toc = [list(e[:3]) for e in self.document.toc()]
        toc.append([1, title.strip(), cur + 1])
        toc.sort(key=lambda e: e[2])
        self.document.set_toc(toc)
        self.reload()

    def rename_bookmark(self):
        item = self.tree.currentItem()
        if item is None:
            return
        from PySide6.QtWidgets import QInputDialog
        title, ok = QInputDialog.getText(self, _("Yeniden adlandır"), _("Başlık:"),
                                         text=item.text(0))
        if not ok or not title.strip():
            return
        toc = [list(e[:3]) for e in self.document.toc()]
        for e in toc:
            if e[1] == item.text(0) and e[2] - 1 == item.data(0, Qt.UserRole):
                e[1] = title.strip()
                break
        self.document.set_toc(toc)
        self.reload()

    def delete_bookmark(self):
        item = self.tree.currentItem()
        if item is None:
            return
        toc = [list(e[:3]) for e in self.document.toc()]
        toc = [e for e in toc
               if not (e[1] == item.text(0) and e[2] - 1 == item.data(0, Qt.UserRole))]
        self.document.set_toc(toc)
        self.reload()


# ------------------------------------------------------------------ açıklamalar
class AnnotationPanel(QWidget):
    navigate = Signal(int, object)
    deleteRequested = Signal(list)

    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        bar = QHBoxLayout()
        bar.setContentsMargins(8, 6, 8, 6)
        self.count_label = QLabel(_("0 açıklama"))
        self.count_label.setProperty("hint", True)
        bar.addWidget(self.count_label, 1)
        b = QToolButton()
        b.setIcon(icons.icon("trash", "#c7cedd", 17))
        b.setToolTip(_("Seçili açıklamaları sil"))
        b.clicked.connect(self._delete)
        bar.addWidget(b)
        lay.addLayout(bar)
        lay.addWidget(HLine())

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([_("Tür / İçerik"), _("Sayfa")])
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tree.itemClicked.connect(self._clicked)
        lay.addWidget(self.tree, 1)

    def reload(self):
        self.tree.clear()
        if not self.document.is_open:
            self.count_label.setText(_("0 açıklama"))
            return
        from ..core import annots as an
        items = an.all_annots(self.document)
        by_page: dict[int, list] = {}
        for a in items:
            by_page.setdefault(a.pno, []).append(a)
        for pno in sorted(by_page):
            parent = QTreeWidgetItem([_("Sayfa {0}").format(pno + 1), str(len(by_page[pno]))])
            parent.setFirstColumnSpanned(False)
            self.tree.addTopLevelItem(parent)
            for a in by_page[pno]:
                text = a.content.replace("\n", " ")[:70] or a.type_name
                child = QTreeWidgetItem([f"{a.type_name}: {text}" if a.content else a.type_name,
                                         str(pno + 1)])
                child.setData(0, Qt.UserRole, (a.pno, a.xref, a.rect))
                if a.author:
                    child.setToolTip(0, f"{a.author}\n{a.content}")
                parent.addChild(child)
            parent.setExpanded(True)
        self.count_label.setText(_n("{0} açıklama", len(items)).format(len(items)))

    def _clicked(self, item, _col):
        data = item.data(0, Qt.UserRole)
        if data:
            self.navigate.emit(data[0], data[2])

    def _delete(self):
        items = []
        for it in self.tree.selectedItems():
            data = it.data(0, Qt.UserRole)
            if data:
                items.append((data[0], data[1]))
        if items:
            self.deleteRequested.emit(items)


# ----------------------------------------------------------------------- arama
class SearchPanel(QWidget):
    searchRequested = Signal(str, bool, bool)
    hitActivated = Signal(int)
    replaceRequested = Signal(str, str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(9, 9, 9, 9)
        lay.setSpacing(7)

        self.query = QLineEdit()
        self.query.setPlaceholderText(_("Aranacak metin…"))
        self.query.setClearButtonEnabled(True)
        self.query.returnPressed.connect(self._search)
        lay.addWidget(self.query)

        opts = QHBoxLayout()
        self.case = QCheckBox(_("Büyük/küçük"))
        self.whole = QCheckBox(_("Tam kelime"))
        opts.addWidget(self.case)
        opts.addWidget(self.whole)
        opts.addStretch(1)
        lay.addLayout(opts)

        row = QHBoxLayout()
        btn = QPushButton(_("Ara"))
        btn.setProperty("accent", True)
        btn.clicked.connect(self._search)
        row.addWidget(btn, 1)
        lay.addLayout(row)

        lay.addWidget(HLine())
        lay.addWidget(QLabel(_("Değiştir")))
        self.replacement = QLineEdit()
        self.replacement.setPlaceholderText(_("Yeni metin…"))
        lay.addWidget(self.replacement)
        self.keep_style = QCheckBox(_("Özgün yazı tipi/rengi koru"))
        self.keep_style.setChecked(True)
        lay.addWidget(self.keep_style)
        rep = QPushButton(_("Tümünü değiştir"))
        rep.clicked.connect(
            lambda: self.replaceRequested.emit(self.query.text(), self.replacement.text(),
                                               self.keep_style.isChecked()))
        lay.addWidget(rep)
        lay.addWidget(HLine())

        self.result_label = QLabel("")
        self.result_label.setProperty("hint", True)
        lay.addWidget(self.result_label)
        self.results = QListWidget()
        self.results.itemClicked.connect(
            lambda it: self.hitActivated.emit(int(it.data(Qt.UserRole))))
        lay.addWidget(self.results, 1)

    def _search(self):
        self.searchRequested.emit(self.query.text(), self.case.isChecked(),
                                  self.whole.isChecked())

    def show_results(self, hits, snippets):
        self.results.clear()
        for i, ((pno, _r), text) in enumerate(zip(hits, snippets)):
            it = QListWidgetItem(_("s.{0}  …{text}…").format(pno + 1, text=text))
            it.setData(Qt.UserRole, i)
            self.results.addItem(it)
        self.result_label.setText(_n("{0} sonuç", len(hits)).format(len(hits)) if hits else _("Sonuç yok"))

    def focus_query(self):
        self.query.setFocus()
        self.query.selectAll()


# ---------------------------------------------------------------------- formlar
class FormPanel(QWidget):
    navigate = Signal(int)
    valueChanged = Signal(int, int, object)

    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        self._loading = False
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        bar = QHBoxLayout()
        bar.setContentsMargins(8, 6, 8, 6)
        self.info = QLabel(_("Form alanı yok"))
        self.info.setProperty("hint", True)
        bar.addWidget(self.info, 1)
        lay.addLayout(bar)
        lay.addWidget(HLine())

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels([_("Alan"), _("Tür"), _("Değer")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.itemChanged.connect(self._changed)
        self.table.itemSelectionChanged.connect(self._selected)
        lay.addWidget(self.table, 1)

    def reload(self):
        from ..core import forms as fm
        self._loading = True
        self.table.setRowCount(0)
        if not self.document.is_open:
            self._loading = False
            return
        fields = fm.list_fields(self.document)
        self.table.setRowCount(len(fields))
        for row, f in enumerate(fields):
            name = QTableWidgetItem(f.label or f.name)
            name.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            name.setData(Qt.UserRole, (f.pno, f.xref))
            kind = QTableWidgetItem(f.type_name)
            kind.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            value = QTableWidgetItem(f.value)
            value.setData(Qt.UserRole, (f.pno, f.xref))
            if f.readonly:
                value.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 0, name)
            self.table.setItem(row, 1, kind)
            self.table.setItem(row, 2, value)
        self.info.setText(_n("{0} form alanı", len(fields)).format(len(fields)) if fields else _("Form alanı yok"))
        self._loading = False

    def _changed(self, item):
        if self._loading or item.column() != 2:
            return
        data = item.data(Qt.UserRole)
        if data:
            self.valueChanged.emit(data[0], data[1], item.text())

    def _selected(self):
        items = self.table.selectedItems()
        if items:
            data = items[0].data(Qt.UserRole)
            if data:
                self.navigate.emit(data[0])


# -------------------------------------------------------------------- görüntüler
class ImagePanel(QWidget):
    navigate = Signal(int, object)
    commandRequested = Signal(str, object)

    def __init__(self, document, parent=None):
        super().__init__(parent)
        self.document = document
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        bar = QHBoxLayout()
        bar.setContentsMargins(8, 6, 8, 6)
        self.info = QLabel(_("Görüntü yok"))
        self.info.setProperty("hint", True)
        bar.addWidget(self.info, 1)
        b = QPushButton(_("Tümünü dışa aktar"))
        b.clicked.connect(lambda: self.commandRequested.emit("export_all", None))
        bar.addWidget(b)
        lay.addLayout(bar)
        lay.addWidget(HLine())

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([_("Görüntü"), _("Boyut"), _("Sayfa")])
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tree.itemClicked.connect(self._clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._menu)
        lay.addWidget(self.tree, 1)

    def reload(self, pno: int | None = None):
        from ..core import images as im
        self.tree.clear()
        if not self.document.is_open:
            return
        total = 0
        rng = [pno] if pno is not None else range(self.document.page_count)
        for p in rng:
            for img in im.list_images(self.document, p):
                item = QTreeWidgetItem([f"#{img.xref} {img.colorspace}",
                                        f"{img.width}×{img.height}", str(p + 1)])
                item.setData(0, Qt.UserRole, (p, img.xref, img.rect))
                self.tree.addTopLevelItem(item)
                total += 1
        self.info.setText(_n("{total} görüntü", total).format(total=total))

    def _clicked(self, item, _col):
        data = item.data(0, Qt.UserRole)
        if data:
            self.navigate.emit(data[0], data[2])

    def _menu(self, pos):
        item = self.tree.itemAt(pos)
        if item is None:
            return
        data = item.data(0, Qt.UserRole)
        m = QMenu(self)
        for label, cmd in ((_("Farklı kaydet…"), "save"), (_("Değiştir…"), "replace"),
                           (_("Sil"), "delete")):
            act = QAction(label, m)
            act.triggered.connect(lambda _x=False, c=cmd, d=data:
                                  self.commandRequested.emit(c, d))
            m.addAction(act)
        m.exec(self.tree.mapToGlobal(pos))
