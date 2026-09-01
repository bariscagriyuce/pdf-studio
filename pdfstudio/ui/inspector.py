"""Sağ panel: araç seçenekleri, seçili nesne özellikleri ve sayfa bilgisi."""
from __future__ import annotations

import pymupdf
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QComboBox, QDoubleSpinBox, QHBoxLayout, QLabel,
                               QLineEdit, QPlainTextEdit, QPushButton, QScrollArea,
                               QSizePolicy, QToolButton, QVBoxLayout, QWidget)

from ..core import annots as an
from .tools import TOOL_HINTS, TOOL_LABELS, LINE_TOOLS, MARKUP_TOOLS, RECT_TOOLS, Tool
from .widgets import ColorButton, LabeledSlider, Section, font_combo


class Inspector(QScrollArea):
    settingsChanged = Signal()
    objectChanged = Signal(dict)     # seçili nesne için düzenleme isteği
    actionRequested = Signal(str)

    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view
        self.settings = view.settings
        self._object = None
        self._loading = False

        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        host = QWidget()
        host.setMinimumWidth(0)
        self.setWidget(host)
        lay = QVBoxLayout(host)
        lay.setContentsMargins(9, 9, 9, 9)
        lay.setSpacing(9)

        self.title = QLabel("Seç / Düzenle")
        self.title.setProperty("title", True)
        lay.addWidget(self.title)
        self.hint = QLabel("")
        self.hint.setWordWrap(True)
        self.hint.setProperty("hint", True)
        lay.addWidget(self.hint)

        # ---------------- görünüm ayarları
        self.appearance = Section("Görünüm")
        self.color_btn = ColorButton(self.settings.color)
        self.fill_btn = ColorButton(self.settings.fill, allow_none=True)
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.2, 30.0)
        self.width_spin.setSingleStep(0.5)
        self.width_spin.setValue(self.settings.width)
        self.width_spin.setSuffix(" pt")
        self.opacity = LabeledSlider(5, 100, 100)
        self.appearance.add_row("Çizgi rengi", self.color_btn)
        self.appearance.add_row("Dolgu", self.fill_btn)
        self.appearance.add_row("Kalınlık", self.width_spin)
        self.appearance.add_row("Saydamlık", self.opacity)
        lay.addWidget(self.appearance)

        # ---------------- yazı ayarları
        self.typography = Section("Yazı")
        self.font_box = font_combo(self.settings.font_family)
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(3.0, 300.0)
        self.size_spin.setValue(self.settings.fontsize)
        self.size_spin.setSuffix(" pt")
        style_row = QWidget()
        srl = QHBoxLayout(style_row)
        srl.setContentsMargins(0, 0, 0, 0)
        srl.setSpacing(4)
        self.bold_btn = QToolButton()
        self.bold_btn.setText("B")
        self.bold_btn.setCheckable(True)
        self.bold_btn.setStyleSheet("font-weight:800; min-width:26px;")
        self.italic_btn = QToolButton()
        self.italic_btn.setText("I")
        self.italic_btn.setCheckable(True)
        self.italic_btn.setStyleSheet("font-style:italic; min-width:26px;")
        self.align_box = QComboBox()
        self.align_box.addItems(["Sola", "Ortala", "Sağa", "İki yana"])
        srl.addWidget(self.bold_btn)
        srl.addWidget(self.italic_btn)
        srl.addWidget(self.align_box, 1)
        self.text_color = ColorButton(self.settings.text_color)
        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.7, 3.0)
        self.spacing_spin.setSingleStep(0.05)
        self.spacing_spin.setValue(self.settings.line_spacing)
        self.typography.add_row("Yazı tipi", self.font_box)
        self.typography.add_row("Punto", self.size_spin)
        self.typography.add_row("Stil", style_row)
        self.typography.add_row("Metin rengi", self.text_color)
        self.typography.add_row("Satır aralığı", self.spacing_spin)
        lay.addWidget(self.typography)

        # ---------------- araca özel
        self.extra = Section("Araç ayarları")
        self.note_icon = QComboBox()
        self.note_icon.addItems(["Note", "Comment", "Help", "Insert", "Key", "NewParagraph",
                                 "Paragraph"])
        self.stamp_box = QComboBox()
        self.stamp_box.addItems(an.STAMP_TEXTS)
        self.author_edit = QLineEdit(self.settings.author)
        self.author_edit.setPlaceholderText("Adınız")
        self.image_btn = QPushButton("Görüntü seç…")
        self.sign_btn = QPushButton("İmza oluştur / seç…")
        self.extra.add_row("Not simgesi", self.note_icon)
        self.extra.add_row("Damga", self.stamp_box)
        self.extra.add_row("Yazar", self.author_edit)
        self.extra.add_widget(self.image_btn)
        self.extra.add_widget(self.sign_btn)
        lay.addWidget(self.extra)

        # ---------------- seçili nesne
        self.object_box = Section("Seçili nesne")
        self.obj_type = QLabel("—")
        self.obj_content = QPlainTextEdit()
        self.obj_content.setPlaceholderText("Açıklama içeriği / not metni")
        self.obj_content.setMaximumHeight(90)
        self.obj_author = QLineEdit()
        self.obj_color = ColorButton((1, 0, 0))
        self.obj_fill = ColorButton(None, allow_none=True)
        self.obj_opacity = LabeledSlider(5, 100, 100)
        self.obj_x = QDoubleSpinBox()
        self.obj_y = QDoubleSpinBox()
        self.obj_w = QDoubleSpinBox()
        self.obj_h = QDoubleSpinBox()
        for sp in (self.obj_x, self.obj_y, self.obj_w, self.obj_h):
            sp.setRange(-20000, 20000)
            sp.setDecimals(1)
            sp.setSuffix(" pt")
        pos_row = QWidget()
        prl = QHBoxLayout(pos_row)
        prl.setContentsMargins(0, 0, 0, 0)
        prl.setSpacing(4)
        prl.addWidget(self.obj_x)
        prl.addWidget(self.obj_y)
        size_row = QWidget()
        srl2 = QHBoxLayout(size_row)
        srl2.setContentsMargins(0, 0, 0, 0)
        srl2.setSpacing(4)
        srl2.addWidget(self.obj_w)
        srl2.addWidget(self.obj_h)
        self.apply_btn = QPushButton("Değişiklikleri uygula")
        self.apply_btn.setProperty("accent", True)
        self.delete_btn = QPushButton("Nesneyi sil")
        self.delete_btn.setProperty("danger", True)
        self.object_box.add_row("Tür", self.obj_type)
        self.object_box.add_row("İçerik", self.obj_content)
        self.object_box.add_row("Yazar", self.obj_author)
        self.object_box.add_row("Renk", self.obj_color)
        self.object_box.add_row("Dolgu", self.obj_fill)
        self.object_box.add_row("Saydamlık", self.obj_opacity)
        self.object_box.add_row("Konum X/Y", pos_row)
        self.object_box.add_row("Boyut G/Y", size_row)
        self.object_box.add_widget(self.apply_btn)
        self.object_box.add_widget(self.delete_btn)
        lay.addWidget(self.object_box)

        # ---------------- sayfa bilgisi
        self.page_box = Section("Sayfa")
        self.page_info = QLabel("—")
        self.page_info.setWordWrap(True)
        self.page_box.add_widget(self.page_info)
        lay.addWidget(self.page_box)

        lay.addStretch(1)

        for w in (self.font_box, self.align_box, self.note_icon, self.stamp_box,
                  self.author_edit, self.size_spin, self.width_spin, self.spacing_spin,
                  self.obj_author, self.obj_x, self.obj_y, self.obj_w, self.obj_h):
            w.setMinimumWidth(60)
            w.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        self._connect()
        self.set_tool(Tool.SELECT)
        self.set_object(None)

    # ------------------------------------------------------------------ bağlar
    def _connect(self):
        self.color_btn.colorChanged.connect(self._push)
        self.fill_btn.colorChanged.connect(self._push)
        self.text_color.colorChanged.connect(self._push)
        self.width_spin.valueChanged.connect(self._push)
        self.opacity.valueChanged.connect(self._push)
        self.font_box.currentTextChanged.connect(self._push)
        self.size_spin.valueChanged.connect(self._push)
        self.bold_btn.toggled.connect(self._push)
        self.italic_btn.toggled.connect(self._push)
        self.align_box.currentIndexChanged.connect(self._push)
        self.spacing_spin.valueChanged.connect(self._push)
        self.note_icon.currentTextChanged.connect(self._push)
        self.stamp_box.currentIndexChanged.connect(self._push)
        self.author_edit.textChanged.connect(self._push)
        self.image_btn.clicked.connect(lambda: self.actionRequested.emit("pick_image"))
        self.sign_btn.clicked.connect(lambda: self.actionRequested.emit("make_signature"))
        self.apply_btn.clicked.connect(self._apply_object)
        self.delete_btn.clicked.connect(lambda: self.actionRequested.emit("delete_object"))

    def _push(self, *_):
        if self._loading:
            return
        s = self.settings
        tool = self.view.tool
        if tool == Tool.HIGHLIGHT:
            s.highlight_color = self.color_btn.color() or (1, 0.9, 0.25)
        else:
            s.color = self.color_btn.color() or (0, 0, 0)
        s.fill = self.fill_btn.color()
        s.text_color = self.text_color.color() or (0, 0, 0)
        s.width = self.width_spin.value()
        s.opacity = self.opacity.value() / 100.0
        family = self.font_box.currentText()
        if not family.startswith("──"):
            s.font_family = family
        s.fontsize = self.size_spin.value()
        s.bold = self.bold_btn.isChecked()
        s.italic = self.italic_btn.isChecked()
        s.align = self.align_box.currentIndex()
        s.line_spacing = self.spacing_spin.value()
        s.note_icon = self.note_icon.currentText()
        s.stamp_index = self.stamp_box.currentIndex()
        s.author = self.author_edit.text()
        self.settingsChanged.emit()

    # ------------------------------------------------------------------ araç
    def set_tool(self, tool: Tool):
        self._loading = True
        self.title.setText(TOOL_LABELS.get(tool, "Araç"))
        self.hint.setText(TOOL_HINTS.get(tool, ""))
        self.hint.setVisible(bool(TOOL_HINTS.get(tool)))

        show_appearance = tool in (RECT_TOOLS | LINE_TOOLS | MARKUP_TOOLS |
                                   {Tool.INK, Tool.POLYGON, Tool.NOTE})
        show_type = tool in {Tool.TEXT_ADD, Tool.FREETEXT, Tool.TEXT_EDIT, Tool.FORM_TEXT}
        self.appearance.setVisible(show_appearance)
        self.typography.setVisible(show_type)
        self.extra.setVisible(True)
        self.note_icon.setVisible(tool == Tool.NOTE)
        self.stamp_box.setVisible(tool == Tool.STAMP)
        self.image_btn.setVisible(tool == Tool.IMAGE)
        self.sign_btn.setVisible(tool == Tool.SIGNATURE)
        for w, vis in ((self.note_icon, tool == Tool.NOTE),
                       (self.stamp_box, tool == Tool.STAMP)):
            label = self.extra.form.labelForField(w)
            if label:
                label.setVisible(vis)

        if tool == Tool.HIGHLIGHT:
            self.color_btn.set_color(self.settings.highlight_color)
        else:
            self.color_btn.set_color(self.settings.color)
        self.width_spin.setValue(self.settings.width)
        self.opacity.setValue(int(self.settings.opacity * 100))
        self._loading = False

    # -------------------------------------------------------------- nesne
    def set_object(self, obj):
        self._object = obj
        self.object_box.setVisible(obj is not None)
        if obj is None:
            return
        self._loading = True
        pno, kind, rect, ref = obj
        names = {"annot": "Açıklama", "image": "Görüntü", "widget": "Form alanı"}
        detail = names.get(kind, kind)
        content = author = ""
        color = (1, 0, 0)
        fill = None
        opacity = 100
        if kind == "annot":
            for a in an.list_annots(self.view.document, pno):
                if a.xref == ref:
                    detail = f"Açıklama · {a.type_name}"
                    content, author = a.content, a.author
                    break
            try:
                page = self.view.document.page(pno)
                for a in page.annots():
                    if a.xref == ref:
                        colors = a.colors or {}
                        if colors.get("stroke"):
                            color = tuple(colors["stroke"])[:3]
                        if colors.get("fill"):
                            fill = tuple(colors["fill"])[:3]
                        opacity = int(round((a.opacity if a.opacity >= 0 else 1.0) * 100))
                        break
            except Exception:
                pass
        elif kind == "widget":
            from ..core import forms as fm
            for f in fm.list_fields(self.view.document, pno):
                if f.xref == ref:
                    detail = f"Form · {f.type_name}"
                    content = f.value
                    break
        self.obj_type.setText(detail)
        self.obj_content.setPlainText(content)
        self.obj_author.setText(author)
        self.obj_color.set_color(color)
        self.obj_fill.set_color(fill)
        self.obj_opacity.setValue(opacity)
        self.obj_x.setValue(rect.x0)
        self.obj_y.setValue(rect.y0)
        self.obj_w.setValue(rect.width)
        self.obj_h.setValue(rect.height)
        self.obj_content.setEnabled(kind in ("annot", "widget"))
        self.obj_author.setEnabled(kind == "annot")
        self.obj_color.setEnabled(kind == "annot")
        self.obj_fill.setEnabled(kind == "annot")
        self.obj_opacity.setEnabled(kind == "annot")
        self._loading = False

    def _apply_object(self):
        if not self._object:
            return
        pno, kind, _rect, ref = self._object
        rect = pymupdf.Rect(self.obj_x.value(), self.obj_y.value(),
                            self.obj_x.value() + self.obj_w.value(),
                            self.obj_y.value() + self.obj_h.value())
        self.objectChanged.emit({
            "pno": pno, "kind": kind, "xref": ref, "rect": rect,
            "content": self.obj_content.toPlainText(),
            "author": self.obj_author.text(),
            "color": self.obj_color.color(),
            "fill": self.obj_fill.color(),
            "opacity": self.obj_opacity.value() / 100.0,
        })

    # ------------------------------------------------------------- sayfa bilgisi
    def update_page_info(self, pno: int):
        doc = self.view.document
        if not doc.is_open:
            self.page_info.setText("—")
            return
        try:
            page = doc.page(pno)
        except Exception:
            return
        r = page.rect
        mm = 25.4 / 72
        self.page_info.setText(
            f"Sayfa {pno + 1} / {doc.page_count}\n"
            f"Boyut: {r.width:.0f} × {r.height:.0f} pt "
            f"({r.width * mm:.0f} × {r.height * mm:.0f} mm)\n"
            f"Dönüş: {page.rotation}°\n"
            f"Açıklama: {sum(1 for _ in page.annots())} · "
            f"Görüntü: {len(page.get_images())}"
        )
