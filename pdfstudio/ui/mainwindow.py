"""PDF Studio ana penceresi."""
from __future__ import annotations

import os
import sys

import pymupdf
from PySide6.QtCore import QSettings, QSize, Qt, QTimer
from PySide6.QtGui import (QAction, QActionGroup, QGuiApplication, QImage,
                           QKeySequence, QPainter)
from PySide6.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog
from PySide6.QtWidgets import (QApplication, QComboBox, QDockWidget, QFileDialog,
                               QInputDialog, QLabel, QMainWindow, QMenu, QMessageBox,
                               QProgressDialog, QSizePolicy, QSpinBox, QTabWidget,
                               QToolBar, QWidget)

from ..core import annots as an
from ..core import exporting, forms as fm, images as im, pageops, security
from ..core import textedit as te
from ..core.document import PasswordRequired, PdfDocument
from ..core.fonts import FontManager
from . import dialogs as dlg
from . import icons
from .inspector import Inspector
from .pageview import (LAYOUT_CONTINUOUS, LAYOUT_FACING, LAYOUT_FACING_COVER,
                       LAYOUT_SINGLE, PageView)
from .panels import (AnnotationPanel, FormPanel, ImagePanel, OutlinePanel, SearchPanel,
                     ThumbnailPanel)
from .theme import THEMES, stylesheet
from .tools import TOOL_LABELS, Tool

APP_NAME = "PDF Studio"
APP_VERSION = "1.0.0"
PDF_FILTER = "PDF dosyaları (*.pdf);;Tüm dosyalar (*)"
IMAGE_FILTER = "Görüntüler (*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff);;Tüm dosyalar (*)"


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_store = QSettings("PDFStudio", "PDFStudio")
        self.theme_name = self.settings_store.value("theme", "dark")
        self.colors = THEMES.get(self.theme_name, THEMES["dark"])

        self.document = PdfDocument(self)
        self.view = PageView(self.document, self.colors, self)
        self.setCentralWidget(self.view)
        self.setAcceptDrops(True)
        self.setWindowTitle(APP_NAME)
        self.resize(1500, 950)

        self._search_hits: list = []
        self._suppress_page_signal = False

        self._build_docks()
        self._build_actions()
        self._build_toolbars()
        self._build_menu()
        self._build_statusbar()
        self._connect()
        self.apply_theme(self.theme_name)
        self._restore_state()
        self._update_actions()
        QTimer.singleShot(120, self._load_startup_file)

    # =====================================================================  UI
    def _build_docks(self):
        self.side_tabs = QTabWidget()
        self.side_tabs.setTabPosition(QTabWidget.North)
        self.side_tabs.setDocumentMode(True)
        self.side_tabs.setUsesScrollButtons(False)
        self.side_tabs.tabBar().setExpanding(True)
        self.side_tabs.setStyleSheet(
            "QTabBar::tab { padding: 6px 4px; margin: 3px 1px; min-width: 30px; }")

        self.thumbs = ThumbnailPanel(self.view)
        self.outline = OutlinePanel(self.document)
        self.annots_panel = AnnotationPanel(self.document)
        self.search_panel = SearchPanel()
        self.forms_panel = FormPanel(self.document)
        self.images_panel = ImagePanel(self.document)

        c = self.colors["icon"]
        for widget, name, label in (
            (self.thumbs, "thumbnails", "Sayfalar"),
            (self.outline, "bookmark", "Yer imleri"),
            (self.annots_panel, "comment", "Açıklamalar"),
            (self.search_panel, "search", "Ara"),
            (self.forms_panel, "form", "Formlar"),
            (self.images_panel, "image", "Görüntüler"),
        ):
            self.side_tabs.addTab(widget, icons.icon(name, c, 18), "")
            self.side_tabs.setTabToolTip(self.side_tabs.count() - 1, label)

        self.side_dock = QDockWidget("Gezinme", self)
        self.side_dock.setObjectName("sideDock")
        self.side_dock.setWidget(self.side_tabs)
        self.side_dock.setFeatures(QDockWidget.DockWidgetMovable |
                                   QDockWidget.DockWidgetClosable)
        self.side_dock.setMinimumWidth(250)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.side_dock)

        self.inspector = Inspector(self.view)
        self.inspector_dock = QDockWidget("Özellikler", self)
        self.inspector_dock.setObjectName("inspectorDock")
        self.inspector_dock.setWidget(self.inspector)
        self.inspector_dock.setMinimumWidth(280)
        self.addDockWidget(Qt.RightDockWidgetArea, self.inspector_dock)

    # ------------------------------------------------------------------ eylemler
    def _act(self, icon: str, text: str, slot=None, shortcut=None, checkable=False,
             tip: str = "") -> QAction:
        a = QAction(icons.icon(icon, self.colors["icon"], 20), text, self)
        if slot:
            a.triggered.connect(slot)
        if shortcut:
            a.setShortcut(QKeySequence(shortcut))
        a.setCheckable(checkable)
        a.setToolTip(f"{text}  ({shortcut})" if shortcut else (tip or text))
        return a

    def _build_actions(self):
        A = self._act
        self.act_new = A("new", "Yeni boş belge", self.file_new, "Ctrl+N")
        self.act_new_images = A("image", "Görüntülerden yeni PDF", self.file_new_from_images)
        self.act_open = A("open", "Aç…", self.file_open, "Ctrl+O")
        self.act_save = A("save", "Kaydet", self.file_save, "Ctrl+S")
        self.act_save_as = A("save-as", "Farklı kaydet…", self.file_save_as, "Ctrl+Shift+S")
        self.act_close = A("close", "Belgeyi kapat", self.file_close, "Ctrl+W")
        self.act_print = A("print", "Yazdır…", self.file_print, "Ctrl+P")
        self.act_print_preview = A("print", "Baskı önizleme…", self.file_print_preview)
        self.act_quit = A("close", "Çıkış", self.close, "Ctrl+Q")

        self.act_undo = A("undo", "Geri al", self.edit_undo, "Ctrl+Z")
        self.act_redo = A("redo", "Yinele", self.edit_redo, "Ctrl+Y")
        self.act_copy = A("page-copy", "Seçili metni kopyala", self.edit_copy, "Ctrl+C")
        self.act_find = A("search", "Bul / Değiştir", self.edit_find, "Ctrl+F")
        self.act_find_next = A("next", "Sonraki sonuç", lambda: self._step_hit(1), "F3")
        self.act_find_prev = A("prev", "Önceki sonuç", lambda: self._step_hit(-1), "Shift+F3")
        self.act_props = A("info", "Belge özellikleri…", self.edit_metadata)

        self.act_zoom_in = A("zoom-in", "Yakınlaştır", self.view.zoom_in, "Ctrl+=")
        self.act_zoom_out = A("zoom-out", "Uzaklaştır", self.view.zoom_out, "Ctrl+-")
        self.act_zoom_100 = A("grid", "Gerçek boyut (%100)",
                              lambda: self.view.set_zoom(1.0), "Ctrl+0")
        self.act_fit_width = A("fit-width", "Genişliğe sığdır",
                               lambda: self.view.fit("width"), "Ctrl+1")
        self.act_fit_page = A("fit-page", "Sayfaya sığdır",
                              lambda: self.view.fit("page"), "Ctrl+2")
        self.act_rot_left = A("rotate-left", "Sayfayı sola döndür",
                              lambda: self.page_rotate(-90), "Ctrl+Shift+Left")
        self.act_rot_right = A("rotate-right", "Sayfayı sağa döndür",
                               lambda: self.page_rotate(90), "Ctrl+Shift+Right")
        self.act_sidebar = A("sidebar", "Kenar çubuğu", self.toggle_sidebar, "F9", True)
        self.act_sidebar.setChecked(True)
        self.act_inspector = A("settings", "Özellikler paneli", self.toggle_inspector,
                               "F10", True)
        self.act_inspector.setChecked(True)
        self.act_fullscreen = A("fullscreen", "Tam ekran", self.toggle_fullscreen, "F11", True)
        self.act_theme = A("palette", "Temayı değiştir", self.toggle_theme, "Ctrl+Shift+T")
        self.act_text_boxes = A("grid", "Metin bloklarını göster", self.toggle_text_boxes,
                                None, True)
        self.act_text_boxes.setChecked(True)

        self.act_first = A("first", "İlk sayfa", lambda: self.view.goto_page(0), "Ctrl+Home")
        self.act_prev = A("prev", "Önceki sayfa", self.view.prev_page, "PgUp")
        self.act_next = A("next", "Sonraki sayfa", self.view.next_page, "PgDown")
        self.act_last = A("last", "Son sayfa",
                          lambda: self.view.goto_page(self.document.page_count - 1),
                          "Ctrl+End")

        # sayfa işlemleri
        self.act_page_insert = A("page-add", "Boş sayfa ekle…", self.page_insert)
        self.act_page_delete = A("page-delete", "Sayfaları sil", self.page_delete)
        self.act_page_dup = A("page-copy", "Sayfaları çoğalt", self.page_duplicate)
        self.act_page_extract = A("extract", "Sayfaları çıkar…", self.page_extract)
        self.act_page_crop = A("crop", "Kırpma aracı", lambda: self.set_tool(Tool.CROP))
        self.act_page_crop_reset = A("crop", "Kırpmayı sıfırla", self.page_reset_crop)
        self.act_page_resize = A("fit-page", "Sayfa boyutunu değiştir…", self.page_resize)
        self.act_merge = A("merge", "PDF birleştir…", self.page_merge)
        self.act_images_as_pages = A("image", "Görüntüleri sayfa olarak ekle…",
                                     self.page_add_images)
        self.act_split = A("split", "PDF'i böl…", self.page_split)
        self.act_reverse = A("layers", "Sayfa sırasını ters çevir", self.page_reverse)

        # ekleme
        self.act_watermark = A("watermark", "Filigran…", self.insert_watermark)
        self.act_pagenum = A("number", "Sayfa numarası / üst-alt bilgi…", self.insert_pagenum)
        self.act_attach = A("import", "Dosya eki ekle…", self.insert_attachment)

        # form
        self.act_form_export = A("export", "Form değerlerini dışa aktar…",
                                 self.form_export)
        self.act_form_import = A("import", "Form değerlerini içe aktar…", self.form_import)
        self.act_form_flatten = A("layers", "Formu düzleştir", self.form_flatten)

        # araçlar
        self.act_apply_redactions = A("redact", "Karartmaları uygula",
                                      self.apply_redactions, "Ctrl+Shift+R")
        self.act_flatten = A("layers", "Açıklamaları düzleştir", self.flatten_annots)
        self.act_clear_annots = A("trash", "Tüm açıklamaları kaldır", self.clear_annots)
        self.act_ocr = A("ocr", "OCR uygula…", self.tools_ocr)
        self.act_compress = A("compress", "Boyut küçült…", self.tools_compress)
        self.act_sanitize = A("lock", "Gizlilik temizliği…", self.tools_sanitize)
        self.act_encrypt = A("lock", "Şifrele / izinler…", self.tools_encrypt)
        self.act_decrypt = A("unlock", "Şifrelemeyi kaldır…", self.tools_decrypt)
        self.act_doc_info = A("info", "Belge bilgisi…", self.tools_doc_info)
        self.act_rescan_fonts = A("text-edit", "Yazı tiplerini yeniden tara",
                                  self.tools_rescan_fonts)

        # dışa aktarma
        self.act_export_images = A("image", "Sayfaları görüntü olarak…", self.export_images)
        self.act_export_text = A("text-edit", "Metin / HTML olarak…", self.export_text)
        self.act_export_pages = A("extract", "Seçili sayfaları PDF olarak…",
                                  self.page_extract)
        self.act_export_all_images = A("image", "Gömülü görüntüleri çıkar…",
                                       self.export_embedded_images)

        self.act_about = A("info", "Hakkında", self.help_about)
        self.act_shortcuts = A("info", "Klavye kısayolları", self.help_shortcuts)

        # ---- araç grubu
        self.tool_actions: dict[Tool, QAction] = {}
        self.tool_group = QActionGroup(self)
        self.tool_group.setExclusive(True)
        tool_defs = [
            (Tool.SELECT, "select", "V"),
            (Tool.PAN, "hand", "H"),
            (Tool.TEXT_EDIT, "text-edit", "E"),
            (Tool.TEXT_ADD, "text-add", "T"),
            (Tool.HIGHLIGHT, "highlight", "Ctrl+Alt+H"),
            (Tool.UNDERLINE, "underline", None),
            (Tool.STRIKEOUT, "strikeout", None),
            (Tool.SQUIGGLY, "squiggly", None),
            (Tool.NOTE, "note", "N"),
            (Tool.FREETEXT, "comment", None),
            (Tool.INK, "pen", "D"),
            (Tool.RECT, "rect", "R"),
            (Tool.ELLIPSE, "ellipse", None),
            (Tool.LINE, "line", "L"),
            (Tool.ARROW, "arrow", "A"),
            (Tool.POLYGON, "polygon", None),
            (Tool.IMAGE, "image", "I"),
            (Tool.SIGNATURE, "signature", "S"),
            (Tool.STAMP, "stamp", None),
            (Tool.LINK, "link", "K"),
            (Tool.MEASURE, "measure", "M"),
            (Tool.ERASE_AREA, "eraser", None),
            (Tool.REDACT, "redact", None),
            (Tool.ERASER, "trash", None),
            (Tool.CROP, "crop", "C"),
            (Tool.FORM_TEXT, "form", None),
            (Tool.FORM_CHECK, "check", None),
        ]
        for tool, icon_name, shortcut in tool_defs:
            a = self._act(icon_name, TOOL_LABELS[tool],
                          lambda checked=False, t=tool: self.set_tool(t), shortcut, True)
            self.tool_group.addAction(a)
            self.tool_actions[tool] = a
        self.tool_actions[Tool.SELECT].setChecked(True)

    def _build_toolbars(self):
        tb = QToolBar("Ana")
        tb.setObjectName("mainToolbar")
        tb.setIconSize(QSize(21, 21))
        tb.setMovable(False)
        self.addToolBar(tb)
        for a in (self.act_open, self.act_save, self.act_print):
            tb.addAction(a)
        tb.addSeparator()
        tb.addAction(self.act_undo)
        tb.addAction(self.act_redo)
        tb.addSeparator()
        tb.addAction(self.act_zoom_out)

        self.zoom_box = QComboBox()
        self.zoom_box.setEditable(True)
        self.zoom_box.addItems(["%25", "%50", "%75", "%100", "%125", "%150", "%200",
                                "%400", "Genişliğe sığdır", "Sayfaya sığdır"])
        self.zoom_box.setCurrentText("%100")
        self.zoom_box.setFixedWidth(140)
        self.zoom_box.activated.connect(self._zoom_box_changed)
        self.zoom_box.lineEdit().returnPressed.connect(
            lambda: self._zoom_box_changed(-1))
        tb.addWidget(self.zoom_box)
        tb.addAction(self.act_zoom_in)
        tb.addAction(self.act_fit_width)
        tb.addAction(self.act_fit_page)
        tb.addSeparator()
        tb.addAction(self.act_rot_left)
        tb.addAction(self.act_rot_right)
        tb.addSeparator()
        tb.addAction(self.act_first)
        tb.addAction(self.act_prev)

        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 1)
        self.page_spin.setFixedWidth(66)
        self.page_spin.setAlignment(Qt.AlignCenter)
        self.page_spin.valueChanged.connect(self._page_spin_changed)
        tb.addWidget(self.page_spin)
        self.page_total = QLabel(" / 0 ")
        tb.addWidget(self.page_total)
        tb.addAction(self.act_next)
        tb.addAction(self.act_last)
        tb.addSeparator()

        self.layout_box = QComboBox()
        self.layout_box.addItems(["Sürekli", "Tek sayfa", "Çift sayfa",
                                  "Çift sayfa (kapaklı)"])
        self.layout_box.setFixedWidth(150)
        self.layout_box.currentIndexChanged.connect(self._layout_changed)
        tb.addWidget(self.layout_box)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tb.addWidget(spacer)
        tb.addAction(self.act_find)
        tb.addAction(self.act_sidebar)
        tb.addAction(self.act_inspector)
        tb.addAction(self.act_theme)

        # ---------------- araç çubuğu
        tt = QToolBar("Araçlar")
        tt.setObjectName("toolsToolbar")
        tt.setIconSize(QSize(20, 20))
        tt.setMovable(False)
        self.addToolBarBreak()
        self.addToolBar(tt)
        order = [Tool.SELECT, Tool.PAN, None, Tool.TEXT_EDIT, Tool.TEXT_ADD, None,
                 Tool.HIGHLIGHT, Tool.UNDERLINE, Tool.STRIKEOUT, Tool.SQUIGGLY,
                 Tool.NOTE, Tool.FREETEXT, None,
                 Tool.INK, Tool.RECT, Tool.ELLIPSE, Tool.LINE, Tool.ARROW, Tool.POLYGON,
                 None, Tool.IMAGE, Tool.SIGNATURE, Tool.STAMP, Tool.LINK, Tool.MEASURE,
                 None, Tool.ERASE_AREA, Tool.REDACT, Tool.ERASER, Tool.CROP,
                 None, Tool.FORM_TEXT, Tool.FORM_CHECK]
        for tool in order:
            if tool is None:
                tt.addSeparator()
            else:
                tt.addAction(self.tool_actions[tool])
        tt.addSeparator()
        tt.addAction(self.act_apply_redactions)
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tt.addWidget(spacer2)
        self.tool_hint = QLabel("")
        self.tool_hint.setProperty("hint", True)
        self.tool_hint.setContentsMargins(14, 0, 10, 0)
        self.tool_hint.setMinimumWidth(0)
        self.tool_hint.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        tt.addWidget(self.tool_hint)

    def _build_menu(self):
        mb = self.menuBar()

        m = mb.addMenu("&Dosya")
        m.addAction(self.act_new)
        m.addAction(self.act_new_images)
        m.addAction(self.act_open)
        self.recent_menu = m.addMenu("Son kullanılanlar")
        m.addSeparator()
        m.addAction(self.act_save)
        m.addAction(self.act_save_as)
        m.addAction(self.act_encrypt)
        m.addSeparator()
        ex = m.addMenu(icons.icon("export", self.colors["icon"], 18), "Dışa aktar")
        ex.addAction(self.act_export_images)
        ex.addAction(self.act_export_text)
        ex.addAction(self.act_export_pages)
        ex.addAction(self.act_export_all_images)
        m.addSeparator()
        m.addAction(self.act_print_preview)
        m.addAction(self.act_print)
        m.addSeparator()
        m.addAction(self.act_close)
        m.addAction(self.act_quit)

        m = mb.addMenu("Dü&zen")
        m.addAction(self.act_undo)
        m.addAction(self.act_redo)
        m.addSeparator()
        m.addAction(self.act_copy)
        m.addAction(self.act_find)
        m.addAction(self.act_find_next)
        m.addAction(self.act_find_prev)
        m.addSeparator()
        m.addAction(self.act_props)

        m = mb.addMenu("&Görünüm")
        m.addAction(self.act_zoom_in)
        m.addAction(self.act_zoom_out)
        m.addAction(self.act_zoom_100)
        m.addAction(self.act_fit_width)
        m.addAction(self.act_fit_page)
        m.addSeparator()
        m.addAction(self.act_rot_left)
        m.addAction(self.act_rot_right)
        m.addSeparator()
        m.addAction(self.act_sidebar)
        m.addAction(self.act_inspector)
        m.addAction(self.act_text_boxes)
        m.addAction(self.act_fullscreen)
        m.addAction(self.act_theme)

        m = mb.addMenu("&Sayfa")
        m.addAction(self.act_page_insert)
        m.addAction(self.act_images_as_pages)
        m.addAction(self.act_page_dup)
        m.addAction(self.act_page_delete)
        m.addSeparator()
        m.addAction(self.act_rot_left)
        m.addAction(self.act_rot_right)
        m.addAction(self.act_reverse)
        m.addSeparator()
        m.addAction(self.act_page_crop)
        m.addAction(self.act_page_crop_reset)
        m.addAction(self.act_page_resize)
        m.addSeparator()
        m.addAction(self.act_merge)
        m.addAction(self.act_split)
        m.addAction(self.act_page_extract)

        m = mb.addMenu("&Metin")
        m.addAction(self.tool_actions[Tool.TEXT_EDIT])
        m.addAction(self.tool_actions[Tool.TEXT_ADD])
        m.addAction(self.tool_actions[Tool.ERASE_AREA])
        m.addSeparator()
        m.addAction(self.act_find)
        m.addAction(self.act_export_text)

        m = mb.addMenu("&Ekle")
        for t in (Tool.IMAGE, Tool.SIGNATURE, Tool.STAMP, Tool.LINK, Tool.NOTE,
                  Tool.FREETEXT):
            m.addAction(self.tool_actions[t])
        m.addSeparator()
        m.addAction(self.act_watermark)
        m.addAction(self.act_pagenum)
        m.addAction(self.act_attach)

        m = mb.addMenu("&Form")
        m.addAction(self.tool_actions[Tool.FORM_TEXT])
        m.addAction(self.tool_actions[Tool.FORM_CHECK])
        m.addSeparator()
        m.addAction(self.act_form_export)
        m.addAction(self.act_form_import)
        m.addAction(self.act_form_flatten)

        m = mb.addMenu("&Araçlar")
        m.addAction(self.tool_actions[Tool.REDACT])
        m.addAction(self.act_apply_redactions)
        m.addSeparator()
        m.addAction(self.act_flatten)
        m.addAction(self.act_clear_annots)
        m.addSeparator()
        m.addAction(self.act_ocr)
        m.addAction(self.act_compress)
        m.addAction(self.act_sanitize)
        m.addAction(self.act_decrypt)
        m.addSeparator()
        m.addAction(self.act_doc_info)
        m.addAction(self.act_rescan_fonts)

        m = mb.addMenu("&Yardım")
        m.addAction(self.act_shortcuts)
        m.addAction(self.act_about)
        self._refresh_recent()

    def _build_statusbar(self):
        sb = self.statusBar()
        self.status_file = QLabel("Belge açık değil")
        self.status_zoom = QLabel("")
        self.status_tool = QLabel("")
        sb.addWidget(self.status_file, 1)
        sb.addPermanentWidget(self.status_tool)
        sb.addPermanentWidget(self.status_zoom)

    def _connect(self):
        v = self.view
        v.pageChanged.connect(self._on_page_changed)
        v.zoomChanged.connect(self._on_zoom_changed)
        v.statusMessage.connect(lambda t: self.statusBar().showMessage(t, 6000))
        v.editTextRequested.connect(self.on_edit_text)
        v.rectToolFinished.connect(self.on_rect_tool)
        v.lineToolFinished.connect(self.on_line_tool)
        v.pointToolFinished.connect(self.on_point_tool)
        v.inkFinished.connect(self.on_ink)
        v.polygonFinished.connect(self.on_polygon)
        v.selectionChanged.connect(self.on_selection)
        v.objectSelected.connect(self.inspector.set_object)
        v.contextRequested.connect(self.on_context_menu)

        self.document.structureChanged.connect(self.on_structure_changed)
        self.document.pagesChanged.connect(self.on_pages_changed)
        self.document.dirtyChanged.connect(lambda _d: self._update_title())
        self.document.historyChanged.connect(self._update_actions)

        self.thumbs.pageActivated.connect(lambda p: self.view.goto_page(p, center=False))
        self.thumbs.reorderRequested.connect(self.on_reorder)
        self.thumbs.commandRequested.connect(self.on_thumb_command)
        self.outline.navigate.connect(lambda p: self.view.goto_page(p, center=False))
        self.annots_panel.navigate.connect(self._goto_rect)
        self.annots_panel.deleteRequested.connect(self.on_delete_annots)
        self.search_panel.searchRequested.connect(self.do_search)
        self.search_panel.hitActivated.connect(self.view.goto_hit)
        self.search_panel.replaceRequested.connect(self.do_replace_all)
        self.forms_panel.navigate.connect(lambda p: self.view.goto_page(p, center=False))
        self.forms_panel.valueChanged.connect(self.on_form_value)
        self.images_panel.navigate.connect(self._goto_rect)
        self.images_panel.commandRequested.connect(self.on_image_command)

        self.inspector.actionRequested.connect(self.on_inspector_action)
        self.inspector.objectChanged.connect(self.on_object_changed)

    # ================================================================= tema
    def apply_theme(self, name: str):
        self.theme_name = name
        self.colors = THEMES.get(name, THEMES["dark"])
        self.settings_store.setValue("theme", name)
        app = QApplication.instance()
        app.setStyleSheet(stylesheet(self.colors))
        icons.clear_cache()
        self.view.set_palette_colors(self.colors)
        c = self.colors["icon"]
        for a, name_ in self._icon_map().items():
            a.setIcon(icons.icon(name_, c, 20))
        for i, n in enumerate(["thumbnails", "bookmark", "comment", "search", "form",
                               "image"]):
            self.side_tabs.setTabIcon(i, icons.icon(n, c, 18))
        # tema değişiminde tüm alt bileşenleri yeniden biçimlendir
        for w in self.findChildren(QWidget):
            w.style().unpolish(w)
            w.style().polish(w)
            w.update()
        self.update()

    def _icon_map(self) -> dict:
        mapping = {}
        pairs = [
            (self.act_new, "new"), (self.act_open, "open"), (self.act_save, "save"),
            (self.act_save_as, "save-as"), (self.act_print, "print"),
            (self.act_undo, "undo"), (self.act_redo, "redo"),
            (self.act_zoom_in, "zoom-in"), (self.act_zoom_out, "zoom-out"),
            (self.act_fit_width, "fit-width"), (self.act_fit_page, "fit-page"),
            (self.act_rot_left, "rotate-left"), (self.act_rot_right, "rotate-right"),
            (self.act_first, "first"), (self.act_prev, "prev"),
            (self.act_next, "next"), (self.act_last, "last"),
            (self.act_find, "search"), (self.act_sidebar, "sidebar"),
            (self.act_inspector, "settings"), (self.act_theme, "palette"),
            (self.act_apply_redactions, "redact"),
        ]
        for a, n in pairs:
            mapping[a] = n
        tool_icons = {
            Tool.SELECT: "select", Tool.PAN: "hand", Tool.TEXT_EDIT: "text-edit",
            Tool.TEXT_ADD: "text-add", Tool.HIGHLIGHT: "highlight",
            Tool.UNDERLINE: "underline", Tool.STRIKEOUT: "strikeout",
            Tool.SQUIGGLY: "squiggly", Tool.NOTE: "note", Tool.FREETEXT: "comment",
            Tool.INK: "pen", Tool.RECT: "rect", Tool.ELLIPSE: "ellipse",
            Tool.LINE: "line", Tool.ARROW: "arrow", Tool.POLYGON: "polygon",
            Tool.IMAGE: "image", Tool.SIGNATURE: "signature", Tool.STAMP: "stamp",
            Tool.LINK: "link", Tool.MEASURE: "measure", Tool.ERASE_AREA: "eraser",
            Tool.REDACT: "redact", Tool.ERASER: "trash", Tool.CROP: "crop",
            Tool.FORM_TEXT: "form", Tool.FORM_CHECK: "check",
        }
        for tool, n in tool_icons.items():
            mapping[self.tool_actions[tool]] = n
        return mapping

    def toggle_theme(self):
        self.apply_theme("light" if self.theme_name == "dark" else "dark")

    # ============================================================ durum güncelleme
    def _update_title(self):
        if not self.document.is_open:
            self.setWindowTitle(APP_NAME)
            return
        star = "•  " if self.document.dirty else ""
        self.setWindowTitle(f"{star}{self.document.display_name} — {APP_NAME}")
        self.status_file.setText(self.document.path or "Kaydedilmemiş belge")

    def _update_actions(self):
        opened = self.document.is_open
        for a in (self.act_save, self.act_save_as, self.act_close, self.act_print,
                  self.act_print_preview, self.act_find, self.act_props,
                  self.act_page_insert, self.act_page_delete, self.act_page_dup,
                  self.act_page_extract, self.act_merge, self.act_split,
                  self.act_watermark, self.act_pagenum, self.act_ocr,
                  self.act_compress, self.act_encrypt, self.act_decrypt,
                  self.act_doc_info, self.act_export_images, self.act_export_text,
                  self.act_flatten, self.act_clear_annots, self.act_sanitize,
                  self.act_reverse, self.act_page_resize, self.act_page_crop_reset,
                  self.act_form_export, self.act_form_import, self.act_form_flatten,
                  self.act_attach, self.act_images_as_pages, self.act_export_all_images):
            a.setEnabled(opened)
        self.act_undo.setEnabled(opened and self.document.history.can_undo())
        self.act_redo.setEnabled(opened and self.document.history.can_redo())
        if opened and self.document.history.can_undo():
            self.act_undo.setToolTip(f"Geri al: {self.document.history.undo_label()}")
        self.act_apply_redactions.setEnabled(bool(self.view.pending_redactions))
        self._update_title()

    def _on_page_changed(self, pno: int):
        self._suppress_page_signal = True
        self.page_spin.setValue(pno + 1)
        self._suppress_page_signal = False
        self.thumbs.set_current(pno)
        self.inspector.update_page_info(pno)

    def _on_zoom_changed(self, zoom: float):
        self.status_zoom.setText(f"%{zoom * 100:.0f}")
        self.zoom_box.blockSignals(True)
        if self.view.fit_mode == "width":
            self.zoom_box.setCurrentText("Genişliğe sığdır")
        elif self.view.fit_mode == "page":
            self.zoom_box.setCurrentText("Sayfaya sığdır")
        else:
            self.zoom_box.setCurrentText(f"%{zoom * 100:.0f}")
        self.zoom_box.blockSignals(False)

    def _page_spin_changed(self, value: int):
        if not self._suppress_page_signal:
            self.view.goto_page(value - 1, center=False)

    def _zoom_box_changed(self, _index: int):
        text = self.zoom_box.currentText().strip()
        if "genişl" in text.lower():
            self.view.fit("width")
            return
        if "sayfa" in text.lower():
            self.view.fit("page")
            return
        digits = "".join(ch for ch in text if ch.isdigit() or ch == ".")
        try:
            self.view.set_zoom(float(digits) / 100.0)
        except ValueError:
            pass

    def _layout_changed(self, index: int):
        modes = [LAYOUT_CONTINUOUS, LAYOUT_SINGLE, LAYOUT_FACING, LAYOUT_FACING_COVER]
        self.view.set_layout_mode(modes[index])

    def on_structure_changed(self):
        self.page_spin.setRange(1, max(1, self.document.page_count))
        self.page_total.setText(f" / {self.document.page_count} ")
        self.thumbs.reload()
        self.outline.reload()
        self.annots_panel.reload()
        self.forms_panel.reload()
        self.images_panel.reload()
        self._update_actions()
        self.inspector.update_page_info(self.view.current_page)

    def on_pages_changed(self, pages: list):
        self.thumbs.refresh_pages(pages)
        self.annots_panel.reload()
        self.images_panel.reload()
        self._update_actions()
        self.inspector.update_page_info(self.view.current_page)

    # ================================================================== dosya
    def _confirm_discard(self) -> bool:
        if not self.document.is_open or not self.document.dirty:
            return True
        res = QMessageBox.question(
            self, "Kaydedilmemiş değişiklikler",
            f"“{self.document.display_name}” kaydedilmedi. Ne yapmak istersiniz?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save)
        if res == QMessageBox.Save:
            return self.file_save()
        return res == QMessageBox.Discard

    def _load_startup_file(self):
        for arg in sys.argv[1:]:
            if arg.lower().endswith(".pdf") and os.path.exists(arg):
                self.open_path(arg)
                return

    def file_new(self):
        if not self._confirm_discard():
            return
        self.document.new_blank()
        self.view.fit("width")

    def file_new_from_images(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Görüntü seç", "", IMAGE_FILTER)
        if not paths or not self._confirm_discard():
            return
        self.document.new_from_images(paths)
        self.view.fit("width")

    def file_open(self):
        start = self.settings_store.value("last_dir", "")
        path, _ = QFileDialog.getOpenFileName(self, "PDF aç", start, PDF_FILTER)
        if path:
            self.open_path(path)

    def open_path(self, path: str):
        if not self._confirm_discard():
            return
        password = None
        while True:
            try:
                self.document.open(path, password)
                break
            except PasswordRequired:
                d = dlg.PasswordDialog(path, self)
                if not d.exec():
                    return
                password = d.password()
            except Exception as exc:
                QMessageBox.critical(self, "Açılamadı", f"{path}\n\n{exc}")
                return
        self.settings_store.setValue("last_dir", os.path.dirname(path))
        self._push_recent(path)
        self.view.fit("width")
        self.statusBar().showMessage(f"Açıldı: {path}", 5000)

    def file_save(self) -> bool:
        if not self.document.is_open:
            return False
        if not self.document.path:
            return self.file_save_as()
        try:
            self.document.save()
        except Exception as exc:
            QMessageBox.critical(self, "Kaydedilemedi", str(exc))
            return False
        self.statusBar().showMessage(f"Kaydedildi: {self.document.path}", 4000)
        return True

    def file_save_as(self) -> bool:
        if not self.document.is_open:
            return False
        start = self.document.path or os.path.join(
            self.settings_store.value("last_dir", ""), "belge.pdf")
        path, _ = QFileDialog.getSaveFileName(self, "Farklı kaydet", start, PDF_FILTER)
        if not path:
            return False
        if not path.lower().endswith(".pdf"):
            path += ".pdf"
        try:
            self.document.save(path)
        except Exception as exc:
            QMessageBox.critical(self, "Kaydedilemedi", str(exc))
            return False
        self._push_recent(path)
        self.statusBar().showMessage(f"Kaydedildi: {path}", 4000)
        self._update_title()
        return True

    def file_close(self):
        if not self._confirm_discard():
            return
        self.document.close()
        self._update_actions()

    def _push_recent(self, path: str):
        items = list(self.settings_store.value("recent", []) or [])
        if path in items:
            items.remove(path)
        items.insert(0, path)
        self.settings_store.setValue("recent", items[:12])
        self._refresh_recent()

    def _refresh_recent(self):
        self.recent_menu.clear()
        items = [p for p in (self.settings_store.value("recent", []) or [])
                 if os.path.exists(p)]
        if not items:
            a = QAction("(boş)", self)
            a.setEnabled(False)
            self.recent_menu.addAction(a)
            return
        for p in items:
            a = QAction(os.path.basename(p), self)
            a.setToolTip(p)
            a.triggered.connect(lambda _c=False, path=p: self.open_path(path))
            self.recent_menu.addAction(a)
        self.recent_menu.addSeparator()
        clear = QAction("Listeyi temizle", self)
        clear.triggered.connect(lambda: (self.settings_store.setValue("recent", []),
                                         self._refresh_recent()))
        self.recent_menu.addAction(clear)

    # ----------------------------------------------------------------- yazdırma
    def _print_render(self, printer: QPrinter):
        painter = QPainter()
        if not painter.begin(printer):
            return
        pages = range(self.document.page_count)
        first = True
        for pno in pages:
            if not first:
                printer.newPage()
            first = False
            page = self.document.page(pno)
            res = printer.resolution() or 300
            zoom = res / 72.0
            pm = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
            img = QImage(pm.samples, pm.width, pm.height, pm.stride,
                         QImage.Format_RGB888).copy()
            rect = painter.viewport()
            scaled = img.size()
            scaled.scale(rect.size(), Qt.KeepAspectRatio)
            x = rect.x() + (rect.width() - scaled.width()) // 2
            y = rect.y() + (rect.height() - scaled.height()) // 2
            painter.drawImage(
                type(rect)(x, y, scaled.width(), scaled.height()), img)
        painter.end()

    def file_print(self):
        if not self.document.is_open:
            return
        printer = QPrinter(QPrinter.HighResolution)
        d = QPrintDialog(printer, self)
        d.setWindowTitle("Yazdır")
        if d.exec():
            self._print_render(printer)

    def file_print_preview(self):
        if not self.document.is_open:
            return
        printer = QPrinter(QPrinter.HighResolution)
        d = QPrintPreviewDialog(printer, self)
        d.resize(1000, 800)
        d.paintRequested.connect(self._print_render)
        d.exec()

    # ================================================================== düzen
    def edit_undo(self):
        label = self.document.undo()
        if label:
            self.statusBar().showMessage(f"Geri alındı: {label}", 3000)

    def edit_redo(self):
        label = self.document.redo()
        if label:
            self.statusBar().showMessage(f"Yinelendi: {label}", 3000)

    def edit_copy(self):
        text = self.view.selected_text()
        if text:
            QGuiApplication.clipboard().setText(text)
            self.statusBar().showMessage(f"{len(text)} karakter kopyalandı", 3000)
        else:
            self.statusBar().showMessage("Önce metin seçin (Seç aracı ile sürükleyin)",
                                         4000)

    def edit_find(self):
        self.side_dock.show()
        self.act_sidebar.setChecked(True)
        self.side_tabs.setCurrentWidget(self.search_panel)
        self.search_panel.focus_query()

    def edit_metadata(self):
        if not self.document.is_open:
            return
        d = dlg.MetadataDialog(self.document.metadata(), self)
        if d.exec():
            meta = self.document.metadata()
            meta.update(d.metadata())
            self.document.set_metadata(meta)
            self.statusBar().showMessage("Belge özellikleri güncellendi", 3000)

    # ================================================================== arama
    def do_search(self, needle: str, case: bool, whole: bool):
        if not self.document.is_open or not needle:
            self.view.set_search_hits([])
            self.search_panel.show_results([], [])
            return
        hits = te.find_all(self.document, needle, case_sensitive=case, whole_words=whole)
        self._search_hits = hits
        snippets = []
        for pno, r in hits[:400]:
            big = pymupdf.Rect(max(0, r.x0 - 90), r.y0 - 1, r.x1 + 90, r.y1 + 1)
            try:
                snippets.append(self.document.page(pno).get_textbox(big)
                                .replace("\n", " ").strip()[:80])
            except Exception:
                snippets.append(needle)
        self.view.set_search_hits(hits, 0 if hits else None)
        self.search_panel.show_results(hits[:400], snippets)
        if hits:
            self.view.goto_hit(0)
        self.statusBar().showMessage(f"{len(hits)} sonuç bulundu", 4000)

    def _step_hit(self, delta: int):
        if not self._search_hits:
            return
        cur = self.view.current_hit or 0
        self.view.goto_hit(cur + delta)

    def do_replace_all(self, needle: str, repl: str, keep_style: bool):
        if not self.document.is_open or not needle:
            return
        res = QMessageBox.question(
            self, "Tümünü değiştir",
            f"'{needle}' → '{repl}' değişimi belgedeki tüm eşleşmelere uygulanacak.\n"
            "Bu işlem sayfa içeriğini kalıcı olarak değiştirir (geri alınabilir).",
            QMessageBox.Yes | QMessageBox.No)
        if res != QMessageBox.Yes:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            n = te.replace_all(self.document, needle, repl, match_style=keep_style)
        finally:
            QApplication.restoreOverrideCursor()
        self.statusBar().showMessage(f"{n} eşleşme değiştirildi", 5000)
        self.do_search(needle, False, False)

    def _goto_rect(self, pno: int, rect):
        self.view.goto_page(pno, center=False)
        if rect is not None:
            item = self.view.items[pno]
            qr = self.view.pdf_rect_to_item(pno, rect)
            self.view.centerOn(item.mapToScene(qr.center()))

    # ================================================================== araçlar
    def set_tool(self, tool: Tool):
        self.view.set_tool(tool)
        self.tool_actions[tool].setChecked(True)
        self.inspector.set_tool(tool)
        self.status_tool.setText(TOOL_LABELS.get(tool, ""))
        from .tools import TOOL_HINTS
        self.tool_hint.setText(TOOL_HINTS.get(tool, ""))
        if tool == Tool.IMAGE and not self.view.settings.image_path:
            self.on_inspector_action("pick_image")
        if tool == Tool.SIGNATURE and not self.view.settings.signature_bytes:
            self.on_inspector_action("make_signature")

    def on_inspector_action(self, name: str):
        if name == "pick_image":
            path, _ = QFileDialog.getOpenFileName(self, "Görüntü seç", "", IMAGE_FILTER)
            if path:
                self.view.settings.image_path = path
                self.statusBar().showMessage(
                    f"Görüntü hazır: {os.path.basename(path)} — sayfada bir kutu çizin", 6000)
        elif name == "make_signature":
            d = dlg.SignatureDialog(self)
            if d.exec():
                data = d.signature_bytes()
                if data:
                    self.view.settings.signature_bytes = data
                    self.statusBar().showMessage(
                        "İmza hazır — yerleştirmek için sayfada bir kutu çizin", 6000)
                else:
                    QMessageBox.information(self, "İmza", "İmza oluşturulamadı.")
        elif name == "delete_object":
            self.delete_selected_object()

    # ------------------------------------------------------ tuval geri çağrıları
    def on_edit_text(self, pno: int, rect, text: str, style):
        d = dlg.TextEditDialog(text, style, rect, self)
        if not d.exec():
            return
        new_text = d.result_text()
        st = d.result_style()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            ok = te.replace_region_text(self.document, pno, rect, new_text, st,
                                        background=d.background(), grow=d.grow())
        except Exception as exc:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Düzenlenemedi", str(exc))
            return
        QApplication.restoreOverrideCursor()
        if not ok:
            self.statusBar().showMessage(
                "Metin kutuya tam sığmadı; punto otomatik küçültüldü.", 6000)
        else:
            self.statusBar().showMessage("Metin güncellendi", 3000)

    def on_rect_tool(self, tool: Tool, payload):
        pno, rect = payload
        s = self.view.settings
        try:
            if tool == Tool.SELECT:
                self._apply_object_geometry(pno, rect)
            elif tool == Tool.TEXT_ADD:
                d = dlg.BatchTextDialog(
                    te.TextStyle(family=s.font_family, size=s.fontsize,
                                 color=s.text_color, bold=s.bold, italic=s.italic,
                                 align=s.align), self)
                if d.exec():
                    text, st = d.values()
                    if text.strip():
                        te.insert_text_box(self.document, pno, rect, text, st)
            elif tool == Tool.FREETEXT:
                text, ok = QInputDialog.getMultiLineText(self, "Metin kutusu", "Metin:")
                if ok and text:
                    an.add_free_text(self.document, pno, rect, text,
                                     fontsize=s.fontsize, text_color=s.text_color,
                                     fill_color=s.fill, border_color=s.color,
                                     border_width=s.width if s.fill else 0,
                                     align=s.align, opacity=s.opacity, author=s.author)
            elif tool in (Tool.RECT, Tool.ELLIPSE):
                an.add_shape(self.document, pno,
                             "rect" if tool == Tool.RECT else "ellipse",
                             (rect.x0, rect.y0), (rect.x1, rect.y1),
                             color=s.color, fill=s.fill, width=s.width,
                             opacity=s.opacity, author=s.author)
            elif tool == Tool.IMAGE:
                if not s.image_path:
                    self.on_inspector_action("pick_image")
                if s.image_path:
                    an.place_image(self.document, pno, rect, s.image_path)
            elif tool == Tool.SIGNATURE:
                if not s.signature_bytes:
                    self.on_inspector_action("make_signature")
                if s.signature_bytes:
                    an.place_image_bytes(self.document, pno, rect, s.signature_bytes)
            elif tool == Tool.STAMP:
                an.add_stamp(self.document, pno, rect, s.stamp_index, color=s.color,
                             opacity=s.opacity, author=s.author)
            elif tool == Tool.LINK:
                d = dlg.LinkDialog(self.document.page_count, self)
                if d.exec():
                    v = d.values()
                    an.add_link(self.document, pno, rect, uri=v["uri"],
                                target_page=v["target_page"])
            elif tool == Tool.REDACT:
                self.view.pending_redactions.append((pno, rect))
                self.view.viewport().update()
                self.act_apply_redactions.setEnabled(True)
                self.statusBar().showMessage(
                    f"{len(self.view.pending_redactions)} karartma bekliyor — "
                    "uygulamak için Ctrl+Shift+R", 6000)
            elif tool == Tool.ERASE_AREA:
                te.delete_text_region(self.document, pno, rect, remove_images=True,
                                      remove_graphics=True)
            elif tool == Tool.CROP:
                pageops.crop_page(self.document, [pno], rect)
                self.view.fit(self.view.fit_mode if self.view.fit_mode != "none"
                              else "width")
            elif tool == Tool.FORM_TEXT:
                name, ok = QInputDialog.getText(self, "Metin alanı", "Alan adı:",
                                                text=f"metin_{pno + 1}")
                if ok and name:
                    fm.add_field(self.document, pno, rect, kind="text", name=name,
                                 fontsize=s.fontsize)
            elif tool == Tool.FORM_CHECK:
                name, ok = QInputDialog.getText(self, "Onay kutusu", "Alan adı:",
                                                text=f"onay_{pno + 1}")
                if ok and name:
                    fm.add_field(self.document, pno, rect, kind="checkbox", name=name)
        except Exception as exc:
            QMessageBox.critical(self, "İşlem başarısız", str(exc))

    def on_line_tool(self, tool: Tool, payload):
        pno, p0, p1 = payload
        s = self.view.settings
        kind = "arrow" if tool == Tool.ARROW else "line"
        try:
            an.add_shape(self.document, pno, kind, p0, p1, color=s.color,
                         width=s.width, opacity=s.opacity, author=s.author)
        except Exception as exc:
            QMessageBox.critical(self, "İşlem başarısız", str(exc))

    def on_point_tool(self, tool: Tool, payload):
        pno, point = payload
        s = self.view.settings
        if tool == Tool.NOTE:
            text, ok = QInputDialog.getMultiLineText(self, "Yapışkan not", "Not:")
            if ok and text:
                an.add_sticky_note(self.document, pno, (point.x, point.y), text,
                                   icon=s.note_icon, color=s.color, author=s.author)
        elif tool == Tool.ERASER:
            page = self.document.page(pno)
            a = an.annot_at(page, point)
            if a is None:
                self.statusBar().showMessage("Bu noktada açıklama yok", 3000)
                return
            an.delete_annot(self.document, pno, a.xref)

    def on_ink(self, pno: int, strokes):
        if not strokes:
            return
        s = self.view.settings
        an.add_ink(self.document, pno, strokes, color=s.color, width=s.width,
                   opacity=s.opacity, author=s.author)

    def on_polygon(self, pno: int, points):
        if len(points) < 3:
            return
        s = self.view.settings
        an.add_polygon(self.document, pno, points, closed=True, color=s.color,
                       fill=s.fill, width=s.width, opacity=s.opacity, author=s.author)

    def on_selection(self, pno: int, quads):
        if pno < 0 or not quads:
            return
        tool = self.view.tool
        kinds = {Tool.HIGHLIGHT: "highlight", Tool.UNDERLINE: "underline",
                 Tool.STRIKEOUT: "strikeout", Tool.SQUIGGLY: "squiggly"}
        if tool in kinds:
            s = self.view.settings
            an.add_markup(self.document, pno, kinds[tool], quads,
                          color=s.markup_color(tool), opacity=s.opacity,
                          author=s.author)
            self.view.selection_quads = []
        else:
            text = self.view.selected_text()
            if text:
                self.statusBar().showMessage(
                    f"{len(text)} karakter seçildi (Ctrl+C ile kopyalayın)", 4000)

    def on_context_menu(self, pno: int, point, global_pos):
        m = QMenu(self)
        sel = self.view.selection_quads and self.view.selection_page == pno
        if sel:
            m.addAction("Kopyala", self.edit_copy)
            m.addAction("Vurgula", lambda: self.on_selection_apply(pno, "highlight"))
            m.addAction("Altını çiz", lambda: self.on_selection_apply(pno, "underline"))
            m.addAction("Üstünü çiz", lambda: self.on_selection_apply(pno, "strikeout"))
            m.addSeparator()
        obj = self.view._object_at(pno, self.view.pdf_to_item(pno, point))
        if obj:
            self.view.selected_object = obj
            self.inspector.set_object(obj)
            self.view.viewport().update()
            m.addAction("Bu nesneyi sil", self.delete_selected_object)
            if obj[1] == "image":
                m.addAction("Görüntüyü değiştir…",
                            lambda: self.on_image_command("replace",
                                                          (obj[0], obj[3], obj[2])))
                m.addAction("Görüntüyü kaydet…",
                            lambda: self.on_image_command("save",
                                                          (obj[0], obj[3], obj[2])))
            m.addSeparator()
        blocks = [b for b in self.view.blocks_for(pno) if pymupdf.Point(point) in b.bbox]
        if blocks:
            blk = min(blocks, key=lambda b: b.bbox.get_area())
            m.addAction("Bu metni düzenle…",
                        lambda: self.on_edit_text(pno, blk.bbox, blk.text, blk.style))
        m.addSeparator()
        m.addAction(self.act_page_insert)
        m.addAction("Bu sayfayı sil", lambda: self._delete_pages([pno]))
        m.addAction("Bu sayfayı çoğalt", lambda: pageops.duplicate_pages(self.document,
                                                                        [pno]))
        m.addSeparator()
        m.addAction(self.act_fit_width)
        m.addAction(self.act_fit_page)
        m.exec(global_pos)

    def on_selection_apply(self, pno: int, kind: str):
        quads = self.view.selection_quads
        if not quads:
            return
        s = self.view.settings
        color = s.highlight_color if kind == "highlight" else s.color
        an.add_markup(self.document, pno, kind, quads, color=color,
                      opacity=s.opacity, author=s.author)
        self.view.selection_quads = []

    # ------------------------------------------------------------- nesne düzenle
    def _apply_object_geometry(self, pno: int, rect):
        obj = self.view.selected_object
        if not obj:
            return
        _p, kind, _r, ref = obj
        try:
            if kind == "annot":
                an.update_annot(self.document, pno, ref, rect=rect)
            elif kind == "image":
                old = self._image_rect(pno, ref)
                if old:
                    im.move_resize_image(self.document, pno, old, rect)
            elif kind == "widget":
                with self.document.edit("Form alanını taşı", pages=[pno]) as doc:
                    for w in doc[pno].widgets():
                        if w.xref == ref:
                            w.rect = pymupdf.Rect(rect)
                            w.update()
                            break
        except Exception as exc:
            QMessageBox.critical(self, "Taşınamadı", str(exc))

    def _image_rect(self, pno: int, xref: int):
        for img in im.list_images(self.document, pno):
            if img.xref == xref:
                return img.rect
        return None

    def on_object_changed(self, data: dict):
        pno, kind, ref = data["pno"], data["kind"], data["xref"]
        try:
            if kind == "annot":
                an.update_annot(self.document, pno, ref, content=data["content"],
                                author=data["author"], color=data["color"],
                                fill=data["fill"], opacity=data["opacity"],
                                rect=data["rect"])
            elif kind == "widget":
                fm.set_value(self.document, pno, ref, data["content"])
                self.forms_panel.reload()
            elif kind == "image":
                old = self._image_rect(pno, ref)
                if old:
                    im.move_resize_image(self.document, pno, old, data["rect"])
        except Exception as exc:
            QMessageBox.critical(self, "Güncellenemedi", str(exc))

    def delete_selected_object(self):
        obj = self.view.selected_object
        if not obj:
            self.statusBar().showMessage("Önce bir nesne seçin", 3000)
            return
        pno, kind, rect, ref = obj
        try:
            if kind == "annot":
                an.delete_annot(self.document, pno, ref)
            elif kind == "widget":
                fm.delete_field(self.document, pno, ref)
            elif kind == "image":
                im.delete_image(self.document, pno, rect)
        except Exception as exc:
            QMessageBox.critical(self, "Silinemedi", str(exc))
            return
        self.view.selected_object = None
        self.inspector.set_object(None)

    def on_delete_annots(self, items):
        if not items:
            return
        an.delete_annots(self.document, items)

    # ================================================================== sayfalar
    def _target_pages(self) -> list[int]:
        sel = self.thumbs.selected_pages()
        return sel or [self.view.current_page]

    def page_rotate(self, delta: int):
        if not self.document.is_open:
            return
        pageops.rotate_pages(self.document, self._target_pages(), delta)

    def page_insert(self):
        if not self.document.is_open:
            return
        d = dlg.InsertPageDialog(self.document.page_count, self.view.current_page, self)
        if d.exec():
            v = d.values()
            pageops.insert_blank(self.document, v["index"], v["width"], v["height"],
                                 v["count"])

    def _delete_pages(self, pages):
        if not pages:
            return
        if self.document.page_count - len(pages) < 1:
            QMessageBox.warning(self, "Silinemez", "Belgede en az bir sayfa kalmalı.")
            return
        res = QMessageBox.question(
            self, "Sayfaları sil",
            f"{len(pages)} sayfa silinecek. Devam edilsin mi?",
            QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            pageops.delete_pages(self.document, pages)

    def page_delete(self):
        self._delete_pages(self._target_pages())

    def page_duplicate(self):
        pageops.duplicate_pages(self.document, self._target_pages())

    def page_reverse(self):
        pageops.reorder_pages(self.document,
                              list(reversed(range(self.document.page_count))))

    def page_reset_crop(self):
        pageops.reset_crop(self.document, self._target_pages())

    def page_resize(self):
        d = dlg.InsertPageDialog(self.document.page_count, self.view.current_page, self)
        d.setWindowTitle("Sayfa boyutunu değiştir")
        d.count.setEnabled(False)
        d.where.setEnabled(False)
        if d.exec():
            v = d.values()
            pageops.resize_pages(self.document, self._target_pages(), v["width"],
                                 v["height"])

    def page_extract(self):
        pages = self._target_pages()
        path, _ = QFileDialog.getSaveFileName(
            self, "Sayfaları PDF olarak kaydet",
            os.path.splitext(self.document.path or "belge")[0] + "_secim.pdf", PDF_FILTER)
        if not path:
            return
        pageops.extract_pages(self.document, pages, path)
        self.statusBar().showMessage(f"{len(pages)} sayfa kaydedildi: {path}", 5000)

    def page_merge(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Birleştirilecek PDF'ler", "",
                                                PDF_FILTER)
        if not paths:
            return
        where = QMessageBox.question(
            self, "Birleştir", "Seçilen dosyalar nereye eklensin?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if where == QMessageBox.Cancel:
            return
        at = self.document.page_count if where == QMessageBox.Yes \
            else self.view.current_page
        try:
            n = pageops.merge_files(self.document, paths, at)
        except Exception as exc:
            QMessageBox.critical(self, "Birleştirilemedi", str(exc))
            return
        self.statusBar().showMessage(f"{n} sayfa eklendi", 5000)

    def page_add_images(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Görüntü seç", "", IMAGE_FILTER)
        if paths:
            n = pageops.insert_images_as_pages(self.document, paths,
                                               self.view.current_page + 1)
            self.statusBar().showMessage(f"{n} sayfa eklendi", 4000)

    def page_split(self):
        d = dlg.SplitDialog(self.document.page_count, self)
        if not d.exec():
            return
        v = d.values()
        out_dir = v["out_dir"] or os.path.dirname(self.document.path or ".")
        stem = os.path.splitext(os.path.basename(self.document.path or "belge"))[0]
        try:
            if v["mode"] == "every":
                files = pageops.split_every(self.document, v["n"], out_dir, stem)
            else:
                files = pageops.split_by_ranges(self.document, v["ranges"], out_dir, stem)
        except Exception as exc:
            QMessageBox.critical(self, "Bölünemedi", str(exc))
            return
        QMessageBox.information(self, "Tamamlandı",
                                f"{len(files)} dosya oluşturuldu:\n{out_dir}")

    def on_reorder(self, order: list):
        if order == list(range(self.document.page_count)):
            return
        pageops.reorder_pages(self.document, order)

    def on_thumb_command(self, cmd: str, pages: list):
        try:
            if cmd == "rotate_left":
                pageops.rotate_pages(self.document, pages, -90)
            elif cmd == "rotate_right":
                pageops.rotate_pages(self.document, pages, 90)
            elif cmd == "duplicate":
                pageops.duplicate_pages(self.document, pages)
            elif cmd == "delete":
                self._delete_pages(pages)
            elif cmd in ("insert_before", "insert_after"):
                w, h = self.document.page_size(pages[0])
                idx = pages[0] if cmd == "insert_before" else pages[-1] + 1
                pageops.insert_blank(self.document, idx, w, h, 1)
            elif cmd == "extract":
                path, _ = QFileDialog.getSaveFileName(self, "PDF olarak kaydet",
                                                      "secim.pdf", PDF_FILTER)
                if path:
                    pageops.extract_pages(self.document, pages, path)
            elif cmd == "export_image":
                out = QFileDialog.getExistingDirectory(self, "Hedef klasör")
                if out:
                    files = exporting.export_images(self.document, out, pages=pages,
                                                    dpi=200)
                    self.statusBar().showMessage(f"{len(files)} görüntü kaydedildi", 4000)
        except Exception as exc:
            QMessageBox.critical(self, "İşlem başarısız", str(exc))

    # ================================================================== ekleme
    def insert_watermark(self):
        d = dlg.WatermarkDialog(self.document.page_count, self.view.current_page, self)
        if not d.exec():
            return
        v = d.values()
        try:
            if v["mode"] == "text":
                if not v["text"].strip():
                    return
                from ..core.fonts import resolve_insert_font
                name, fontfile = resolve_insert_font(v["family"], False, False, v["text"])
                if fontfile:
                    self._watermark_with_font(v, name, fontfile)
                else:
                    pageops.add_text_watermark(
                        self.document, v["text"], v["pages"], fontsize=v["size"],
                        color=v["color"], opacity=v["opacity"], angle=v["angle"],
                        fontname=name, behind=v["behind"])
            else:
                if not v["image"]:
                    return
                pageops.add_image_watermark(self.document, v["image"], v["pages"],
                                            opacity=v["image_opacity"],
                                            scale=v["scale"], behind=v["behind"])
        except Exception as exc:
            QMessageBox.critical(self, "Filigran eklenemedi", str(exc))

    def _watermark_with_font(self, v: dict, alias: str, fontfile: str):
        """Unicode yazı tipi gerektiren filigranlar için özel yol."""
        with self.document.edit("Filigran ekle", structural=True) as doc:
            font = pymupdf.Font(fontfile=fontfile)
            for pno in v["pages"]:
                page = doc[pno]
                r = page.rect
                width = font.text_length(v["text"], v["size"])
                cx, cy = r.width / 2, r.height / 2
                shape = page.new_shape()
                shape.insert_text(
                    pymupdf.Point(cx - width / 2, cy), v["text"], fontname=alias,
                    fontfile=fontfile, fontsize=v["size"], color=v["color"],
                    fill_opacity=v["opacity"], stroke_opacity=v["opacity"],
                    morph=(pymupdf.Point(cx, cy), pymupdf.Matrix(v["angle"])))
                shape.commit(overlay=not v["behind"])

    def insert_pagenum(self):
        d = dlg.PageNumberDialog(self.document.page_count, self.view.current_page, self)
        if not d.exec():
            return
        v = d.values()
        try:
            if v["fmt"].strip():
                pageops.add_page_numbers(
                    self.document, v["pages"], fmt=v["fmt"], position=v["position"],
                    fontsize=v["size"], color=v["color"], margin=v["margin"],
                    start_at=v["start"])
            if v["header"] or v["footer"]:
                pageops.add_header_footer(self.document, v["pages"], header=v["header"],
                                          footer=v["footer"], fontsize=v["size"],
                                          color=v["color"], margin=v["margin"] - 12)
        except Exception as exc:
            QMessageBox.critical(self, "Eklenemedi", str(exc))

    def insert_attachment(self):
        path, _ = QFileDialog.getOpenFileName(self, "Eklenecek dosya", "")
        if not path:
            return
        page = self.document.page(self.view.current_page)
        an.add_file_attachment(self.document, self.view.current_page,
                               (page.rect.width - 40, 40), path,
                               author=self.view.settings.author)

    # ================================================================== formlar
    def on_form_value(self, pno: int, xref: int, value):
        fm.set_value(self.document, pno, xref, value)

    def form_export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Form değerlerini kaydet",
                                              "form.json", "JSON (*.json)")
        if path:
            fm.export_json(self.document, path)
            self.statusBar().showMessage(f"Kaydedildi: {path}", 4000)

    def form_import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Form değerlerini yükle", "",
                                              "JSON (*.json)")
        if path:
            n = fm.import_json(self.document, path)
            self.forms_panel.reload()
            self.statusBar().showMessage(f"{n} alan dolduruldu", 4000)

    def form_flatten(self):
        res = QMessageBox.question(
            self, "Formu düzleştir",
            "Form alanları sayfa içeriğine gömülecek ve artık düzenlenemeyecek. Devam?",
            QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            fm.flatten_forms(self.document)

    # =================================================================== araçlar
    def apply_redactions(self):
        areas = self.view.pending_redactions
        if not areas:
            self.statusBar().showMessage(
                "Bekleyen karartma yok — önce Karart aracıyla alan çizin", 4000)
            return
        res = QMessageBox.warning(
            self, "Karartmaları uygula",
            f"{len(areas)} alandaki metin ve görüntüler KALICI olarak silinecek.\n"
            "Belgeyi kaydettikten sonra bu içerik geri getirilemez.",
            QMessageBox.Yes | QMessageBox.No)
        if res != QMessageBox.Yes:
            return
        try:
            te.redact_areas(self.document, areas,
                            fill=self.view.settings.redact_fill)
        except Exception as exc:
            QMessageBox.critical(self, "Uygulanamadı", str(exc))
            return
        self.view.clear_pending_redactions()
        self._update_actions()
        self.statusBar().showMessage("Karartmalar uygulandı", 5000)

    def flatten_annots(self):
        res = QMessageBox.question(
            self, "Açıklamaları düzleştir",
            "Tüm açıklamalar sayfa içeriğine gömülecek. Devam?",
            QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            an.flatten(self.document, annots=True, widgets=False)

    def clear_annots(self):
        res = QMessageBox.question(self, "Açıklamaları kaldır",
                                   "Belgedeki tüm açıklamalar silinecek. Devam?",
                                   QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            n = an.clear_annots(self.document)
            self.statusBar().showMessage(f"{n} açıklama silindi", 4000)

    def tools_ocr(self):
        d = dlg.OcrDialog(self.document.page_count, self.view.current_page, self)
        if not d.exec():
            return
        v = d.values()
        prog = QProgressDialog("OCR uygulanıyor…", "İptal", 0, len(v["pages"]), self)
        prog.setWindowModality(Qt.WindowModal)
        prog.setMinimumDuration(0)

        def cb(done, total):
            prog.setValue(done)
            QApplication.processEvents()

        try:
            exporting.ocr_pages(self.document, v["pages"], language=v["language"],
                                dpi=v["dpi"], progress=cb)
        except Exception as exc:
            prog.close()
            QMessageBox.critical(self, "OCR başarısız", str(exc))
            return
        prog.close()
        self.statusBar().showMessage("OCR tamamlandı", 5000)

    def tools_compress(self):
        d = dlg.CompressDialog(self)
        if not d.exec():
            return
        v = d.values()
        base = os.path.splitext(self.document.path or "belge")[0]
        path, _ = QFileDialog.getSaveFileName(self, "Küçültülmüş PDF",
                                              base + "_kucuk.pdf", PDF_FILTER)
        if not path:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            before, after = exporting.compress(self.document, path,
                                               image_dpi=v["image_dpi"],
                                               jpeg_quality=v["quality"],
                                               subset_fonts=v["subset"])
        except Exception as exc:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Küçültülemedi", str(exc))
            return
        QApplication.restoreOverrideCursor()
        pct = (1 - after / before) * 100 if before else 0
        QMessageBox.information(
            self, "Tamamlandı",
            f"Önce: {before / 1e6:.2f} MB\nSonra: {after / 1e6:.2f} MB\n"
            f"Kazanç: %{pct:.1f}\n\n{path}")

    def tools_sanitize(self):
        res = QMessageBox.question(
            self, "Gizlilik temizliği",
            "Meta veri, JavaScript ve otomatik eylemler kaldırılsın mı?",
            QMessageBox.Yes | QMessageBox.No)
        if res == QMessageBox.Yes:
            security.sanitize(self.document, remove_metadata=True, remove_js=True)
            self.statusBar().showMessage("Belge temizlendi", 4000)

    def tools_encrypt(self):
        d = dlg.SecurityDialog(security.current_permissions(self.document), self)
        if not d.exec():
            return
        v = d.values()
        base = os.path.splitext(self.document.path or "belge")[0]
        path, _ = QFileDialog.getSaveFileName(self, "Şifreli kaydet",
                                              base + "_korumali.pdf", PDF_FILTER)
        if not path:
            return
        try:
            security.save_encrypted(self.document, path, user_pw=v["user_pw"],
                                    owner_pw=v["owner_pw"], allowed=v["allowed"],
                                    method=v["method"])
        except Exception as exc:
            QMessageBox.critical(self, "Kaydedilemedi", str(exc))
            return
        QMessageBox.information(self, "Tamamlandı", f"Şifreli kopya kaydedildi:\n{path}")

    def tools_decrypt(self):
        base = os.path.splitext(self.document.path or "belge")[0]
        path, _ = QFileDialog.getSaveFileName(self, "Şifresiz kaydet",
                                              base + "_acik.pdf", PDF_FILTER)
        if not path:
            return
        try:
            security.save_decrypted(self.document, path)
        except Exception as exc:
            QMessageBox.critical(self, "Kaydedilemedi", str(exc))
            return
        QMessageBox.information(self, "Tamamlandı", f"Kaydedildi:\n{path}")

    def tools_doc_info(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            report = security.document_report(self.document)
        finally:
            QApplication.restoreOverrideCursor()
        dlg.DocumentInfoDialog(report, self).exec()

    def tools_rescan_fonts(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            FontManager.instance().load(force=True)
        finally:
            QApplication.restoreOverrideCursor()
        n = len(FontManager.instance().families())
        QMessageBox.information(self, "Yazı tipleri", f"{n} yazı tipi ailesi bulundu.")

    # ================================================================ dışa aktar
    def export_images(self):
        d = dlg.ExportImagesDialog(self.document.page_count, self.view.current_page, self)
        if not d.exec():
            return
        v = d.values()
        out = v["out_dir"] or QFileDialog.getExistingDirectory(self, "Hedef klasör")
        if not out:
            return
        stem = os.path.splitext(os.path.basename(self.document.path or "sayfa"))[0]
        prog = QProgressDialog("Dışa aktarılıyor…", "İptal", 0, len(v["pages"]), self)
        prog.setWindowModality(Qt.WindowModal)

        def cb(done, total):
            prog.setValue(done)
            QApplication.processEvents()

        try:
            files = exporting.export_images(self.document, out, pages=v["pages"],
                                            dpi=v["dpi"], fmt=v["fmt"], stem=stem,
                                            alpha=v["alpha"], gray=v["gray"],
                                            progress=cb)
        except Exception as exc:
            prog.close()
            QMessageBox.critical(self, "Dışa aktarılamadı", str(exc))
            return
        prog.close()
        QMessageBox.information(self, "Tamamlandı",
                                f"{len(files)} dosya kaydedildi:\n{out}")

    def export_text(self):
        mode_name, ok = QInputDialog.getItem(self, "Metin dışa aktar", "Biçim:",
                                             list(exporting.TEXT_MODES), 0, False)
        if not ok:
            return
        mode, ext = exporting.TEXT_MODES[mode_name]
        base = os.path.splitext(self.document.path or "belge")[0]
        path, _ = QFileDialog.getSaveFileName(self, "Kaydet", f"{base}.{ext}",
                                              f"*.{ext}")
        if not path:
            return
        try:
            exporting.export_text(self.document, path, mode=mode)
        except Exception as exc:
            QMessageBox.critical(self, "Dışa aktarılamadı", str(exc))
            return
        self.statusBar().showMessage(f"Kaydedildi: {path}", 5000)

    def export_embedded_images(self):
        out = QFileDialog.getExistingDirectory(self, "Görüntülerin kaydedileceği klasör")
        if not out:
            return
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            files = im.extract_all_images(self.document, out)
        finally:
            QApplication.restoreOverrideCursor()
        QMessageBox.information(self, "Tamamlandı",
                                f"{len(files)} görüntü kaydedildi:\n{out}")

    def on_image_command(self, cmd: str, data):
        try:
            if cmd == "export_all":
                self.export_embedded_images()
                return
            pno, xref, rect = data
            if cmd == "save":
                path, _ = QFileDialog.getSaveFileName(self, "Görüntüyü kaydet",
                                                      f"gorsel_{xref}.png",
                                                      "Görüntüler (*.png *.jpg)")
                if path:
                    real = im.extract_image(self.document, xref, path)
                    self.statusBar().showMessage(f"Kaydedildi: {real}", 4000)
            elif cmd == "replace":
                path, _ = QFileDialog.getOpenFileName(self, "Yeni görüntü", "",
                                                      IMAGE_FILTER)
                if path:
                    im.replace_image(self.document, pno, rect, path)
            elif cmd == "delete":
                im.delete_image(self.document, pno, rect)
        except Exception as exc:
            QMessageBox.critical(self, "İşlem başarısız", str(exc))

    # =================================================================== görünüm
    def toggle_sidebar(self):
        self.side_dock.setVisible(self.act_sidebar.isChecked())

    def toggle_inspector(self):
        self.inspector_dock.setVisible(self.act_inspector.isChecked())

    def toggle_fullscreen(self):
        if self.act_fullscreen.isChecked():
            self.showFullScreen()
        else:
            self.showNormal()

    def toggle_text_boxes(self):
        self.view.show_text_boxes = self.act_text_boxes.isChecked()
        self.view.viewport().update()

    # ==================================================================== yardım
    def help_about(self):
        QMessageBox.about(
            self, f"{APP_NAME} hakkında",
            f"<h3>{APP_NAME} {APP_VERSION}</h3>"
            "<p>Windows ve Linux üzerinde çalışan, ayrıntılı PDF düzenleme uygulaması.</p>"
            "<p>Motor: <b>PyMuPDF (MuPDF)</b> · Arayüz: <b>PySide6 (Qt 6)</b></p>"
            f"<p>PyMuPDF {pymupdf.__version__}</p>")

    def help_shortcuts(self):
        rows = [
            ("Ctrl+O / Ctrl+S", "Aç / Kaydet"),
            ("Ctrl+Shift+S", "Farklı kaydet"),
            ("Ctrl+Z / Ctrl+Y", "Geri al / Yinele"),
            ("Ctrl+F / F3", "Bul / sonraki sonuç"),
            ("Ctrl+P", "Yazdır"),
            ("Ctrl+= / Ctrl+-", "Yakınlaştır / uzaklaştır"),
            ("Ctrl+0 / 1 / 2", "%100 / genişliğe / sayfaya sığdır"),
            ("Ctrl+Fare tekerleği", "Sürekli yakınlaştırma"),
            ("PgUp / PgDn", "Sayfa değiştir"),
            ("V H E T", "Seç · El · Metni düzenle · Metin ekle"),
            ("D R L A", "Çizim · Dikdörtgen · Çizgi · Ok"),
            ("N S I K", "Not · İmza · Görüntü · Bağlantı"),
            ("C M", "Kırp · Ölç"),
            ("Ctrl+Shift+R", "Karartmaları uygula"),
            ("F9 / F10 / F11", "Kenar çubuğu / özellikler / tam ekran"),
            ("Shift+Sürükle", "Sayfayı kaydır"),
            ("Ok tuşları", "Seçili nesneyi taşı"),
            ("Esc", "Seçimi/çizimi iptal et"),
        ]
        html = "<table cellpadding=5>" + "".join(
            f"<tr><td><b>{k}</b></td><td>{v}</td></tr>" for k, v in rows) + "</table>"
        QMessageBox.information(self, "Klavye kısayolları", html)

    # ================================================================ sürükle-bırak
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf"):
                self.open_path(path)
                return
            if os.path.splitext(path)[1].lower() in (".png", ".jpg", ".jpeg", ".webp",
                                                     ".bmp", ".tif", ".tiff"):
                if self.document.is_open:
                    pageops.insert_images_as_pages(self.document, [path],
                                                   self.view.current_page + 1)
                else:
                    self.document.new_from_images([path])
                return

    # ==================================================================== durum
    def _restore_state(self):
        geo = self.settings_store.value("geometry")
        if geo:
            self.restoreGeometry(geo)
        state = self.settings_store.value("windowState")
        if state:
            self.restoreState(state)
        author = self.settings_store.value("author", "")
        if author:
            self.view.settings.author = author
            self.inspector.author_edit.setText(author)

    def closeEvent(self, event):
        if not self._confirm_discard():
            event.ignore()
            return
        self.settings_store.setValue("geometry", self.saveGeometry())
        self.settings_store.setValue("windowState", self.saveState())
        self.settings_store.setValue("author", self.view.settings.author)
        event.accept()
