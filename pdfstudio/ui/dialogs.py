"""Uygulama iletişim kutuları."""
from __future__ import annotations

import os

import pymupdf
from PySide6.QtCore import QBuffer, QPointF, QSize, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QDoubleSpinBox, QFileDialog, QFormLayout, QGroupBox,
                               QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QPlainTextEdit, QPushButton,
                               QRadioButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from ..i18n import N_, _
from ..core import exporting, pageops, security
from ..core.fonts import FontManager
from ..core.textedit import TextStyle
from .widgets import ColorButton, LabeledSlider, font_combo


# --------------------------------------------------------------------- yardımcı
def parse_page_range(text: str, total: int) -> list[int]:
    """'1-5, 8, 11-' -> [0,1,2,3,4,7,10,...]"""
    text = (text or "").strip()
    if not text or text.lower() in ("tümü", "hepsi", "all", "*"):
        return list(range(total))
    out: list[int] = []
    for part in text.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, _x, b = part.partition("-")
            try:
                start = int(a) if a.strip() else 1
                end = int(b) if b.strip() else total
            except ValueError:
                continue
            for i in range(max(1, start), min(total, end) + 1):
                out.append(i - 1)
        else:
            try:
                i = int(part)
            except ValueError:
                continue
            if 1 <= i <= total:
                out.append(i - 1)
    seen, res = set(), []
    for i in out:
        if i not in seen:
            seen.add(i)
            res.append(i)
    return res


class PageRangeBox(QWidget):
    def __init__(self, total: int, current: int = 0, parent=None):
        super().__init__(parent)
        self.total = total
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        self.all_rb = QRadioButton(_("Tüm sayfalar (1–{total})").format(total=total))
        self.cur_rb = QRadioButton(_("Geçerli sayfa ({0})").format(current + 1))
        self.rng_rb = QRadioButton(_("Aralık:"))
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(_("örn. 1-3, 5, 9-"))
        self.edit.textEdited.connect(lambda _t: self.rng_rb.setChecked(True))
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(self.rng_rb)
        row.addWidget(self.edit, 1)
        self.all_rb.setChecked(True)
        self._current = current
        lay.addWidget(self.all_rb)
        lay.addWidget(self.cur_rb)
        lay.addLayout(row)

    def pages(self) -> list[int]:
        if self.cur_rb.isChecked():
            return [self._current]
        if self.rng_rb.isChecked():
            return parse_page_range(self.edit.text(), self.total)
        return list(range(self.total))


def _buttons(dialog: QDialog, ok_text: str = N_("Tamam")) -> QDialogButtonBox:
    box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    box.button(QDialogButtonBox.Ok).setText(_(ok_text))
    box.button(QDialogButtonBox.Ok).setProperty("accent", True)
    box.button(QDialogButtonBox.Cancel).setText(_("Vazgeç"))
    box.accepted.connect(dialog.accept)
    box.rejected.connect(dialog.reject)
    return box


# ------------------------------------------------------------------ metin düzenle
class TextEditDialog(QDialog):
    """Sayfa içeriğindeki bir metin bloğunu düzenler (gerçek PDF metni)."""

    def __init__(self, text: str, style: TextStyle, rect: pymupdf.Rect, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Metni düzenle"))
        self.setMinimumWidth(720)
        self.rect = pymupdf.Rect(rect)
        self.style = style.copy()
        self.deleted = False

        lay = QVBoxLayout(self)
        lay.setSpacing(10)

        info = QLabel(_("Blok: {0:.0f} × {1:.0f} pt — değişiklik doğrudan sayfa içeriğine işlenir.").format(rect.width, rect.height))
        info.setProperty("hint", True)
        lay.addWidget(info)

        body = QHBoxLayout()
        body.setSpacing(12)

        left = QVBoxLayout()
        self.editor = QPlainTextEdit(text)
        self.editor.setMinimumHeight(180)
        left.addWidget(self.editor, 1)

        form = QFormLayout()
        form.setSpacing(7)
        self.font_box = font_combo(style.family)
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(3, 300)
        self.size_spin.setValue(style.size)
        self.size_spin.setSuffix(" pt")
        self.color_btn = ColorButton(style.color)
        self.align_box = QComboBox()
        self.align_box.addItems([_("Sola"), _("Ortala"), _("Sağa"), _("İki yana")])
        self.align_box.setCurrentIndex(style.align)
        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.7, 3.0)
        self.spacing_spin.setSingleStep(0.05)
        self.spacing_spin.setValue(style.line_spacing)
        style_row = QWidget()
        srl = QHBoxLayout(style_row)
        srl.setContentsMargins(0, 0, 0, 0)
        self.bold_cb = QCheckBox(_("Kalın"))
        self.bold_cb.setChecked(style.bold)
        self.italic_cb = QCheckBox(_("İtalik"))
        self.italic_cb.setChecked(style.italic)
        srl.addWidget(self.bold_cb)
        srl.addWidget(self.italic_cb)
        srl.addStretch(1)
        self.grow_cb = QCheckBox(_("Sığmazsa kutuyu büyüt"))
        self.grow_cb.setChecked(True)
        self.bg_btn = ColorButton(None, allow_none=True)
        form.addRow(_("Yazı tipi"), self.font_box)
        form.addRow(_("Punto"), self.size_spin)
        form.addRow(_("Renk"), self.color_btn)
        form.addRow(_("Hizalama"), self.align_box)
        form.addRow(_("Satır aralığı"), self.spacing_spin)
        form.addRow(_("Stil"), style_row)
        form.addRow(_("Arka plan"), self.bg_btn)
        form.addRow(self.grow_cb)
        left.addLayout(form)
        body.addLayout(left, 3)

        right = QVBoxLayout()
        right.addWidget(QLabel(_("Önizleme")))
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(QSize(280, 260))
        self.preview.setStyleSheet(
            "background:#ffffff; border:1px solid #4443; border-radius:6px;")
        right.addWidget(self.preview, 1)
        body.addLayout(right, 2)
        lay.addLayout(body)

        row = QHBoxLayout()
        del_btn = QPushButton(_("Metni sil"))
        del_btn.setProperty("danger", True)
        del_btn.clicked.connect(self._delete)
        row.addWidget(del_btn)
        row.addStretch(1)
        box = _buttons(self, _("Uygula"))
        row.addWidget(box)
        lay.addLayout(row)

        for w in (self.editor,):
            w.textChanged.connect(self._refresh)
        self.font_box.currentTextChanged.connect(self._refresh)
        self.size_spin.valueChanged.connect(self._refresh)
        self.color_btn.colorChanged.connect(self._refresh)
        self.align_box.currentIndexChanged.connect(self._refresh)
        self.spacing_spin.valueChanged.connect(self._refresh)
        self.bold_cb.toggled.connect(self._refresh)
        self.italic_cb.toggled.connect(self._refresh)
        self._refresh()

    def _delete(self):
        self.deleted = True
        self.accept()

    def result_style(self) -> TextStyle:
        fam = self.font_box.currentText()
        if fam.startswith("──"):
            fam = self.style.family
        return TextStyle(
            family=fam, size=self.size_spin.value(),
            color=self.color_btn.color() or (0, 0, 0),
            bold=self.bold_cb.isChecked(), italic=self.italic_cb.isChecked(),
            align=self.align_box.currentIndex(), line_spacing=self.spacing_spin.value(),
        )

    def result_text(self) -> str:
        return "" if self.deleted else self.editor.toPlainText()

    def background(self):
        return self.bg_btn.color()

    def grow(self) -> bool:
        return self.grow_cb.isChecked()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self):
        from ..core.textedit import _insert_fitted
        st = self.result_style()
        pad = 10.0
        w = max(60.0, self.rect.width) + pad * 2
        h = max(40.0, self.rect.height * 1.6) + pad * 2
        try:
            doc = pymupdf.open()
            page = doc.new_page(width=w, height=h)
            box = pymupdf.Rect(pad, pad, w - pad, h - pad)
            page.draw_rect(box, color=(0.85, 0.85, 0.9), width=0.5, dashes="[2 2] 0")
            _insert_fitted(page, box, self.editor.toPlainText(), st)
            pm = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
            img = QImage(pm.samples, pm.width, pm.height, pm.stride,
                         QImage.Format_RGB888).copy()
            doc.close()
            target = self.preview.size()
            pix = QPixmap.fromImage(img)
            if target.width() > 20 and target.height() > 20:
                pix = pix.scaled(target - QSize(8, 8), Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation)
            self.preview.setPixmap(pix)
        except Exception as exc:
            self.preview.setText(_("Önizleme yok\n{exc}").format(exc=exc))


# ------------------------------------------------------------------------ parola
class PasswordDialog(QDialog):
    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Parola gerekli"))
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(_("<b>{0}</b> korumalı.").format(os.path.basename(filename))))
        self.edit = QLineEdit()
        self.edit.setEchoMode(QLineEdit.Password)
        self.edit.setPlaceholderText(_("Parola"))
        lay.addWidget(self.edit)
        lay.addWidget(_buttons(self, _("Aç")))
        self.edit.returnPressed.connect(self.accept)

    def password(self) -> str:
        return self.edit.text()


# ---------------------------------------------------------------------- meta veri
class MetadataDialog(QDialog):
    FIELDS = [("title", N_("Başlık")), ("author", N_("Yazar")), ("subject", N_("Konu")),
              ("keywords", N_("Anahtar kelimeler")), ("creator", N_("Oluşturan")),
              ("producer", N_("Üretici"))]

    def __init__(self, meta: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Belge özellikleri"))
        self.setMinimumWidth(480)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.edits = {}
        for key, label in self.FIELDS:
            e = QLineEdit(str(meta.get(key) or ""))
            form.addRow(_(label), e)
            self.edits[key] = e
        lay.addLayout(form)
        lay.addWidget(_buttons(self, _("Kaydet")))

    def metadata(self) -> dict:
        return {k: e.text() for k, e in self.edits.items()}


# --------------------------------------------------------------------- güvenlik
class SecurityDialog(QDialog):
    def __init__(self, current: set[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Şifreleme ve izinler"))
        self.setMinimumWidth(470)
        lay = QVBoxLayout(self)

        form = QFormLayout()
        self.user_pw = QLineEdit()
        self.user_pw.setEchoMode(QLineEdit.Password)
        self.user_pw.setPlaceholderText(_("Belgeyi açmak için (boş = parolasız açılır)"))
        self.owner_pw = QLineEdit()
        self.owner_pw.setEchoMode(QLineEdit.Password)
        self.owner_pw.setPlaceholderText(_("İzinleri değiştirmek için"))
        self.method = QComboBox()
        for name, value in security.METHODS.items():
            self.method.addItem(_(name), value)
        form.addRow(_("Kullanıcı parolası"), self.user_pw)
        form.addRow(_("Sahip parolası"), self.owner_pw)
        form.addRow(_("Yöntem"), self.method)
        lay.addLayout(form)

        group = QGroupBox(_("İzin verilen işlemler"))
        gl = QVBoxLayout(group)
        self.checks = {}
        for key, _flag, label in security.PERMISSIONS:
            cb = QCheckBox(_(label))
            cb.setChecked(key in current if current else True)
            gl.addWidget(cb)
            self.checks[key] = cb
        lay.addWidget(group)
        lay.addWidget(_buttons(self, _("Şifreli kaydet")))

    def values(self) -> dict:
        return {
            "user_pw": self.user_pw.text(),
            "owner_pw": self.owner_pw.text(),
            "method": self.method.currentData(),
            "allowed": {k for k, cb in self.checks.items() if cb.isChecked()},
        }


# --------------------------------------------------------------------- filigran
class WatermarkDialog(QDialog):
    def __init__(self, total: int, current: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Filigran"))
        self.setMinimumWidth(460)
        lay = QVBoxLayout(self)

        self.tabs = QTabWidget()
        # metin sekmesi
        tw = QWidget()
        tf = QFormLayout(tw)
        self.text = QLineEdit(_("TASLAK"))
        self.font_box = font_combo("Helvetica")
        self.size = QSpinBox()
        self.size.setRange(6, 400)
        self.size.setValue(64)
        self.color = ColorButton((0.6, 0.6, 0.6))
        self.angle = QSpinBox()
        self.angle.setRange(-180, 180)
        self.angle.setValue(45)
        self.opacity = LabeledSlider(5, 100, 25)
        tf.addRow(_("Metin"), self.text)
        tf.addRow(_("Yazı tipi"), self.font_box)
        tf.addRow(_("Punto"), self.size)
        tf.addRow(_("Renk"), self.color)
        tf.addRow(_("Açı"), self.angle)
        tf.addRow(_("Saydamlık"), self.opacity)
        self.tabs.addTab(tw, _("Metin"))

        # görüntü sekmesi
        iw = QWidget()
        _if = QFormLayout(iw)
        self.image_path = QLineEdit()
        pick = QPushButton(_("Seç…"))
        pick.clicked.connect(self._pick)
        row = QHBoxLayout()
        row.addWidget(self.image_path, 1)
        row.addWidget(pick)
        holder = QWidget()
        holder.setLayout(row)
        self.img_scale = LabeledSlider(10, 100, 50)
        self.img_opacity = LabeledSlider(5, 100, 20)
        _if.addRow(_("Dosya"), holder)
        _if.addRow(_("Ölçek"), self.img_scale)
        _if.addRow(_("Saydamlık"), self.img_opacity)
        self.tabs.addTab(iw, _("Görüntü"))
        lay.addWidget(self.tabs)

        self.behind = QCheckBox(_("İçeriğin arkasına yerleştir"))
        lay.addWidget(self.behind)
        lay.addWidget(QLabel(_("Uygulanacak sayfalar")))
        self.range_box = PageRangeBox(total, current)
        lay.addWidget(self.range_box)
        lay.addWidget(_buttons(self, _("Uygula")))

    def _pick(self):
        path, _x = QFileDialog.getOpenFileName(self, _("Filigran görüntüsü"), "",
                                              _("Görüntüler (*.png *.jpg *.jpeg *.webp)"))
        if path:
            self.image_path.setText(path)

    def values(self) -> dict:
        return {
            "mode": "text" if self.tabs.currentIndex() == 0 else "image",
            "text": self.text.text(), "family": self.font_box.currentText(),
            "size": self.size.value(), "color": self.color.color(),
            "angle": self.angle.value(), "opacity": self.opacity.value() / 100,
            "image": self.image_path.text(), "scale": self.img_scale.value() / 100,
            "image_opacity": self.img_opacity.value() / 100,
            "behind": self.behind.isChecked(), "pages": self.range_box.pages(),
        }


# --------------------------------------------------------------- sayfa numarası
class PageNumberDialog(QDialog):
    def __init__(self, total: int, current: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Sayfa numarası / üst-alt bilgi"))
        self.setMinimumWidth(460)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.fmt = QComboBox()
        self.fmt.setEditable(True)
        self.fmt.addItems(["{n}", "{n} / {total}", "- {n} -", _("Sayfa {n}"),
                           _("Sayfa {n} / {total}")])
        self.fmt.setCurrentIndex(1)
        self.position = QComboBox()
        for value, label in (("alt-orta", _("Alt orta")), ("alt-sağ", _("Alt sağ")),
                             ("alt-sol", _("Alt sol")), ("üst-orta", _("Üst orta")),
                             ("üst-sağ", _("Üst sağ")), ("üst-sol", _("Üst sol"))):
            self.position.addItem(label, value)
        self.size = QSpinBox()
        self.size.setRange(5, 48)
        self.size.setValue(10)
        self.color = ColorButton((0.1, 0.1, 0.1))
        self.start = QSpinBox()
        self.start.setRange(1, 100000)
        self.start.setValue(1)
        self.margin = QSpinBox()
        self.margin.setRange(6, 200)
        self.margin.setValue(28)
        self.header = QLineEdit()
        self.header.setPlaceholderText(_("Üst bilgi (isteğe bağlı)"))
        self.footer = QLineEdit()
        self.footer.setPlaceholderText(_("Alt bilgi (isteğe bağlı)"))
        form.addRow(_("Numara biçimi"), self.fmt)
        form.addRow(_("Konum"), self.position)
        form.addRow(_("Punto"), self.size)
        form.addRow(_("Renk"), self.color)
        form.addRow(_("Başlangıç no"), self.start)
        form.addRow(_("Kenar boşluğu"), self.margin)
        form.addRow(_("Üst bilgi"), self.header)
        form.addRow(_("Alt bilgi"), self.footer)
        lay.addLayout(form)
        self.range_box = PageRangeBox(total, current)
        lay.addWidget(self.range_box)
        lay.addWidget(_buttons(self, _("Uygula")))

    def values(self) -> dict:
        return {
            "fmt": self.fmt.currentText(), "position": self.position.currentData(),
            "size": self.size.value(), "color": self.color.color(),
            "start": self.start.value(), "margin": self.margin.value(),
            "header": self.header.text(), "footer": self.footer.text(),
            "pages": self.range_box.pages(),
        }


# ------------------------------------------------------------------ sayfa ekleme
class InsertPageDialog(QDialog):
    def __init__(self, total: int, current: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Boş sayfa ekle"))
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.preset = QComboBox()
        self.preset.addItems(list(pageops.PAGE_PRESETS) + [_("Özel")])
        self.width = QDoubleSpinBox()
        self.width.setRange(20, 5000)
        self.width.setValue(595)
        self.height = QDoubleSpinBox()
        self.height.setRange(20, 5000)
        self.height.setValue(842)
        self.count = QSpinBox()
        self.count.setRange(1, 500)
        self.where = QComboBox()
        self.where.addItems([_("Geçerli sayfadan sonra ({0})").format(current + 1),
                             _("Geçerli sayfadan önce ({0})").format(current + 1),
                             _("Belgenin başına"), _("Belgenin sonuna")])
        self.landscape = QCheckBox(_("Yatay"))
        form.addRow(_("Boyut"), self.preset)
        form.addRow(_("Genişlik"), self.width)
        form.addRow(_("Yükseklik"), self.height)
        form.addRow("", self.landscape)
        form.addRow(_("Adet"), self.count)
        form.addRow(_("Konum"), self.where)
        lay.addLayout(form)
        lay.addWidget(_buttons(self, _("Ekle")))
        self.preset.currentTextChanged.connect(self._preset)
        self._current = current
        self._total = total

    def _preset(self, name):
        size = pageops.PAGE_PRESETS.get(name)
        if size:
            self.width.setValue(size[0])
            self.height.setValue(size[1])

    def values(self) -> dict:
        w, h = self.width.value(), self.height.value()
        if self.landscape.isChecked() and w < h:
            w, h = h, w
        idx = {0: self._current + 1, 1: self._current, 2: 0, 3: self._total}
        return {"width": w, "height": h, "count": self.count.value(),
                "index": idx[self.where.currentIndex()]}


# ---------------------------------------------------------------------- bölme
class SplitDialog(QDialog):
    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("PDF'i böl"))
        self.setMinimumWidth(430)
        lay = QVBoxLayout(self)
        self.every_rb = QRadioButton(_("Her N sayfada bir böl"))
        self.every_rb.setChecked(True)
        self.every = QSpinBox()
        self.every.setRange(1, max(1, total))
        self.every.setValue(1)
        row = QHBoxLayout()
        row.addWidget(self.every_rb)
        row.addWidget(self.every)
        row.addStretch(1)
        lay.addLayout(row)
        self.ranges_rb = QRadioButton(_("Aralıklara göre böl (örn. 1-3, 4-8, 9-)"))
        self.ranges = QLineEdit()
        self.ranges.setPlaceholderText("1-3, 4-8, 9-")
        self.ranges.textEdited.connect(lambda _t: self.ranges_rb.setChecked(True))
        lay.addWidget(self.ranges_rb)
        lay.addWidget(self.ranges)
        lay.addWidget(QLabel(_("Hedef klasör")))
        row2 = QHBoxLayout()
        self.out_dir = QLineEdit()
        pick = QPushButton(_("Seç…"))
        pick.clicked.connect(self._pick)
        row2.addWidget(self.out_dir, 1)
        row2.addWidget(pick)
        lay.addLayout(row2)
        lay.addWidget(_buttons(self, _("Böl")))
        self.total = total

    def _pick(self):
        d = QFileDialog.getExistingDirectory(self, _("Hedef klasör"))
        if d:
            self.out_dir.setText(d)

    def values(self) -> dict:
        if self.ranges_rb.isChecked():
            parts = []
            for chunk in self.ranges.text().split(","):
                pages = parse_page_range(chunk, self.total)
                if pages:
                    parts.append((pages[0], pages[-1]))
            return {"mode": "ranges", "ranges": parts, "out_dir": self.out_dir.text()}
        return {"mode": "every", "n": self.every.value(), "out_dir": self.out_dir.text()}


# ------------------------------------------------------------ görüntü dışa aktar
class ExportImagesDialog(QDialog):
    def __init__(self, total: int, current: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Sayfaları görüntü olarak dışa aktar"))
        self.setMinimumWidth(430)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.fmt = QComboBox()
        self.fmt.addItems(exporting.IMAGE_FORMATS)
        self.dpi = QSpinBox()
        self.dpi.setRange(36, 1200)
        self.dpi.setValue(200)
        self.dpi.setSuffix(" DPI")
        self.gray = QCheckBox(_("Gri tonlama"))
        self.alpha = QCheckBox(_("Saydam arka plan (PNG)"))
        form.addRow(_("Biçim"), self.fmt)
        form.addRow(_("Çözünürlük"), self.dpi)
        form.addRow("", self.gray)
        form.addRow("", self.alpha)
        lay.addLayout(form)
        self.range_box = PageRangeBox(total, current)
        lay.addWidget(self.range_box)
        row = QHBoxLayout()
        self.out_dir = QLineEdit()
        pick = QPushButton(_("Klasör…"))
        pick.clicked.connect(self._pick)
        row.addWidget(self.out_dir, 1)
        row.addWidget(pick)
        lay.addLayout(row)
        lay.addWidget(_buttons(self, _("Dışa aktar")))

    def _pick(self):
        d = QFileDialog.getExistingDirectory(self, _("Hedef klasör"))
        if d:
            self.out_dir.setText(d)

    def values(self) -> dict:
        return {"fmt": self.fmt.currentText(), "dpi": self.dpi.value(),
                "gray": self.gray.isChecked(), "alpha": self.alpha.isChecked(),
                "pages": self.range_box.pages(), "out_dir": self.out_dir.text()}


# -------------------------------------------------------------------- sıkıştırma
class CompressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Boyut küçült"))
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.image_dpi = QSpinBox()
        self.image_dpi.setRange(0, 600)
        self.image_dpi.setValue(150)
        self.image_dpi.setSpecialValueText(_("Değiştirme"))
        self.image_dpi.setSuffix(" DPI")
        self.quality = QSpinBox()
        self.quality.setRange(20, 100)
        self.quality.setValue(72)
        self.subset = QCheckBox(_("Yazı tiplerini alt kümele"))
        self.subset.setChecked(True)
        form.addRow(_("Görüntü çözünürlüğü"), self.image_dpi)
        form.addRow(_("JPEG kalitesi"), self.quality)
        form.addRow("", self.subset)
        lay.addLayout(form)
        lay.addWidget(_buttons(self, _("Küçült ve kaydet")))

    def values(self) -> dict:
        return {"image_dpi": self.image_dpi.value(), "quality": self.quality.value(),
                "subset": self.subset.isChecked()}


# -------------------------------------------------------------------------- OCR
class OcrDialog(QDialog):
    def __init__(self, total: int, current: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("OCR — aranabilir metin katmanı"))
        self.setMinimumWidth(420)
        lay = QVBoxLayout(self)
        ok, msg = exporting.tesseract_available()
        langs = exporting.available_languages() if ok else []
        if ok and langs:
            text = _("✔ Tesseract hazır — kurulu diller: {0}").format(', '.join(langs))
        elif ok:
            text = (_("⚠ Tesseract bulundu ama hiç dil verisi kurulu değil.\n"
                    "Linux: sudo pacman -S tesseract-data-tur tesseract-data-eng\n"
                    "(Debian/Ubuntu: sudo apt install tesseract-ocr-tur tesseract-ocr-eng)"))
        else:
            text = "✖ " + msg
        state = QLabel(text)
        state.setWordWrap(True)
        lay.addWidget(state)
        form = QFormLayout()
        self.lang = QComboBox()
        self.lang.setEditable(True)
        options = []
        if "tur" in langs and "eng" in langs:
            options.append("tur+eng")
        options += langs or ["tur+eng", "tur", "eng"]
        self.lang.addItems(options)
        self.dpi = QSpinBox()
        self.dpi.setRange(72, 600)
        self.dpi.setValue(300)
        self.dpi.setSuffix(" DPI")
        form.addRow(_("Dil"), self.lang)
        form.addRow(_("Çözünürlük"), self.dpi)
        lay.addLayout(form)
        self.range_box = PageRangeBox(total, current)
        lay.addWidget(self.range_box)
        box = _buttons(self, _("OCR uygula"))
        box.button(QDialogButtonBox.Ok).setEnabled(ok and bool(langs))
        lay.addWidget(box)

    def values(self) -> dict:
        return {"language": self.lang.currentText(), "dpi": self.dpi.value(),
                "pages": self.range_box.pages()}


# --------------------------------------------------------------------- bağlantı
class LinkDialog(QDialog):
    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Bağlantı ekle"))
        lay = QVBoxLayout(self)
        self.uri_rb = QRadioButton(_("Web adresi"))
        self.uri_rb.setChecked(True)
        self.uri = QLineEdit("https://")
        self.page_rb = QRadioButton(_("Belge içi sayfa"))
        self.page = QSpinBox()
        self.page.setRange(1, max(1, total))
        lay.addWidget(self.uri_rb)
        lay.addWidget(self.uri)
        row = QHBoxLayout()
        row.addWidget(self.page_rb)
        row.addWidget(self.page)
        row.addStretch(1)
        lay.addLayout(row)
        lay.addWidget(_buttons(self, _("Ekle")))
        self.uri.textEdited.connect(lambda _t: self.uri_rb.setChecked(True))

    def values(self) -> dict:
        if self.page_rb.isChecked():
            return {"target_page": self.page.value() - 1, "uri": ""}
        return {"uri": self.uri.text(), "target_page": None}


# ----------------------------------------------------------------------- imza
class SignaturePad(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(460, 170)
        self.setStyleSheet("background:#ffffff; border:1px dashed #999; border-radius:8px;")
        self.strokes: list[list[QPointF]] = []
        self.pen_width = 2.6
        self.pen_color = QColor("#101828")

    def clear(self):
        self.strokes = []
        self.update()

    def mousePressEvent(self, e):
        self.strokes.append([e.position()])
        self.update()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and self.strokes:
            self.strokes[-1].append(e.position())
            self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor("#ffffff"))
        p.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap,
                      Qt.RoundJoin))
        for stroke in self.strokes:
            if len(stroke) < 2:
                continue
            path = QPainterPath(stroke[0])
            for pt in stroke[1:]:
                path.lineTo(pt)
            p.drawPath(path)
        if not self.strokes:
            p.setPen(QColor("#98a1b5"))
            p.drawText(self.rect(), Qt.AlignCenter, _("Buraya imzanızı çizin"))

    def to_png(self) -> bytes | None:
        if not self.strokes:
            return None
        xs = [pt.x() for s in self.strokes for pt in s]
        ys = [pt.y() for s in self.strokes for pt in s]
        pad = 12
        x0, x1 = max(0, min(xs) - pad), min(self.width(), max(xs) + pad)
        y0, y1 = max(0, min(ys) - pad), min(self.height(), max(ys) + pad)
        scale = 3
        img = QImage(int((x1 - x0) * scale), int((y1 - y0) * scale),
                     QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        p = QPainter(img)
        p.setRenderHint(QPainter.Antialiasing)
        p.scale(scale, scale)
        p.translate(-x0, -y0)
        p.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap,
                      Qt.RoundJoin))
        for stroke in self.strokes:
            if len(stroke) < 2:
                continue
            path = QPainterPath(stroke[0])
            for pt in stroke[1:]:
                path.lineTo(pt)
            p.drawPath(path)
        p.end()
        buf = QBuffer()
        buf.open(QBuffer.WriteOnly)
        img.save(buf, "PNG")
        return bytes(buf.data())


class SignatureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("İmza oluştur"))
        self.setMinimumWidth(520)
        self._bytes: bytes | None = None
        lay = QVBoxLayout(self)
        self.tabs = QTabWidget()

        draw = QWidget()
        dl = QVBoxLayout(draw)
        self.pad = SignaturePad()
        dl.addWidget(self.pad)
        clear = QPushButton(_("Temizle"))
        clear.clicked.connect(self.pad.clear)
        dl.addWidget(clear, 0, Qt.AlignLeft)
        self.tabs.addTab(draw, _("Çiz"))

        typed = QWidget()
        tl = QFormLayout(typed)
        self.typed_text = QLineEdit()
        self.typed_text.setPlaceholderText(_("Ad Soyad"))
        self.typed_font = font_combo("DejaVu Sans")
        self.typed_size = QSpinBox()
        self.typed_size.setRange(10, 120)
        self.typed_size.setValue(42)
        self.typed_color = ColorButton((0.06, 0.09, 0.16))
        tl.addRow(_("Metin"), self.typed_text)
        tl.addRow(_("Yazı tipi"), self.typed_font)
        tl.addRow(_("Punto"), self.typed_size)
        tl.addRow(_("Renk"), self.typed_color)
        self.tabs.addTab(typed, _("Yaz"))

        image = QWidget()
        il = QVBoxLayout(image)
        row = QHBoxLayout()
        self.image_path = QLineEdit()
        pick = QPushButton(_("Seç…"))
        pick.clicked.connect(self._pick)
        row.addWidget(self.image_path, 1)
        row.addWidget(pick)
        il.addLayout(row)
        il.addWidget(QLabel(_("Saydam arka planlı PNG önerilir.")))
        il.addStretch(1)
        self.tabs.addTab(image, _("Görüntü"))

        lay.addWidget(self.tabs)
        lay.addWidget(_buttons(self, _("İmzayı hazırla")))

    def _pick(self):
        path, _x = QFileDialog.getOpenFileName(self, _("İmza görüntüsü"), "",
                                              _("Görüntüler (*.png *.jpg *.jpeg *.webp)"))
        if path:
            self.image_path.setText(path)

    def signature_bytes(self) -> bytes | None:
        idx = self.tabs.currentIndex()
        if idx == 0:
            return self.pad.to_png()
        if idx == 1:
            text = self.typed_text.text().strip()
            if not text:
                return None
            fam = self.typed_font.currentText()
            path = FontManager.instance().path_for(fam)
            size = self.typed_size.value()
            doc = pymupdf.open()
            try:
                font = pymupdf.Font(fontfile=path) if path else pymupdf.Font("helv")
                w = font.text_length(text, size) + 24
            except Exception:
                w = len(text) * size * 0.6 + 24
            h = size * 1.8
            page = doc.new_page(width=w, height=h)
            page.insert_text((12, h * 0.68), text, fontname="sig", fontfile=path,
                             fontsize=size, color=self.typed_color.color())
            pm = page.get_pixmap(matrix=pymupdf.Matrix(3, 3), alpha=True)
            data = pm.tobytes("png")
            doc.close()
            return data
        p = self.image_path.text()
        if p and os.path.exists(p):
            with open(p, "rb") as fh:
                return fh.read()
        return None


# ------------------------------------------------------------------ belge bilgisi
class DocumentInfoDialog(QDialog):
    def __init__(self, report: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Belge bilgisi"))
        self.setMinimumWidth(520)
        lay = QVBoxLayout(self)
        listw = QListWidget()
        for k, v in report.items():
            listw.addItem(QListWidgetItem(f"{_(k)}:  {v}"))
        lay.addWidget(listw)
        box = QDialogButtonBox(QDialogButtonBox.Close)
        box.button(QDialogButtonBox.Close).setText(_("Kapat"))
        box.rejected.connect(self.reject)
        box.accepted.connect(self.accept)
        lay.addWidget(box)


# ---------------------------------------------------------------- toplu ekleme
class BatchTextDialog(QDialog):
    """Metin ekleme aracı için hızlı giriş."""

    def __init__(self, style: TextStyle, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Metin ekle"))
        self.setMinimumWidth(460)
        lay = QVBoxLayout(self)
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText(_("Eklenecek metin…"))
        self.editor.setMinimumHeight(120)
        lay.addWidget(self.editor)
        form = QFormLayout()
        self.font_box = font_combo(style.family)
        self.size = QDoubleSpinBox()
        self.size.setRange(3, 300)
        self.size.setValue(style.size)
        self.color = ColorButton(style.color)
        self.align = QComboBox()
        self.align.addItems([_("Sola"), _("Ortala"), _("Sağa"), _("İki yana")])
        self.bold = QCheckBox(_("Kalın"))
        self.italic = QCheckBox(_("İtalik"))
        row = QHBoxLayout()
        row.addWidget(self.bold)
        row.addWidget(self.italic)
        row.addStretch(1)
        holder = QWidget()
        holder.setLayout(row)
        form.addRow(_("Yazı tipi"), self.font_box)
        form.addRow(_("Punto"), self.size)
        form.addRow(_("Renk"), self.color)
        form.addRow(_("Hizalama"), self.align)
        form.addRow(_("Stil"), holder)
        lay.addLayout(form)
        lay.addWidget(_buttons(self, _("Ekle")))
        self.editor.setFocus()

    def values(self):
        fam = self.font_box.currentText()
        st = TextStyle(family=fam if not fam.startswith("──") else "Helvetica",
                       size=self.size.value(), color=self.color.color() or (0, 0, 0),
                       bold=self.bold.isChecked(), italic=self.italic.isChecked(),
                       align=self.align.currentIndex())
        return self.editor.toPlainText(), st


# ---------------------------------------------------------------- alan yazdır
class AreaPrintDialog(QDialog):
    """Seçili alanı yazdırma / PDF'e kaydetme seçenekleri."""

    PRINT = "print"
    PDF = "pdf"

    def __init__(self, total: int, pno: int, size_pt: tuple[float, float], parent=None):
        super().__init__(parent)
        from ..core import areaprint as ap
        self._ap = ap
        self.setWindowTitle(_("Seçili alanı yazdır"))
        self.setMinimumWidth(460)
        self.total = total
        self.pno = pno
        self.action = self.PRINT

        mm = 25.4 / 72
        w, h = size_pt
        lay = QVBoxLayout(self)
        info = QLabel(_("<b>Sayfa {0}</b> · seçili alan {1:.0f} × {2:.0f} mm").format(pno + 1, w * mm, h * mm))
        lay.addWidget(info)

        # --- ölçek
        scale_box = QGroupBox(_("Ölçek"))
        sl = QVBoxLayout(scale_box)
        self.fit_rb = QRadioButton(_("Kâğıda sığdır"))
        self.fit_rb.setChecked(True)
        self.no_upscale = QCheckBox(_("Küçük alanları büyütme (en fazla %100)"))
        self.no_upscale.setContentsMargins(22, 0, 0, 0)
        self.actual_rb = QRadioButton(_("Gerçek boyut (%100)"))
        custom_row = QHBoxLayout()
        self.custom_rb = QRadioButton(_("Özel:"))
        self.custom_pct = QSpinBox()
        self.custom_pct.setRange(10, 1000)
        self.custom_pct.setValue(150)
        self.custom_pct.setSuffix(" %")
        self.custom_pct.valueChanged.connect(lambda _v: self.custom_rb.setChecked(True))
        custom_row.addWidget(self.custom_rb)
        custom_row.addWidget(self.custom_pct)
        custom_row.addStretch(1)
        sl.addWidget(self.fit_rb)
        sl.addWidget(self.no_upscale)
        sl.addWidget(self.actual_rb)
        sl.addLayout(custom_row)
        self.fit_rb.toggled.connect(self.no_upscale.setEnabled)
        lay.addWidget(scale_box)

        # --- yerleşim
        place_box = QGroupBox(_("Yerleşim"))
        pl = QVBoxLayout(place_box)
        self.center_cb = QCheckBox(_("Kâğıdın ortasına yerleştir"))
        self.center_cb.setChecked(True)
        self.marks_cb = QCheckBox(_("Kesim işaretleri ekle (köşelere ince çizgi)"))
        pl.addWidget(self.center_cb)
        pl.addWidget(self.marks_cb)
        lay.addWidget(place_box)

        # --- sayfalar
        pages_box = QGroupBox(_("Sayfalar"))
        pgl = QVBoxLayout(pages_box)
        self.this_rb = QRadioButton(_("Yalnızca bu sayfa ({0})").format(pno + 1))
        self.this_rb.setChecked(True)
        row = QHBoxLayout()
        self.multi_rb = QRadioButton(_("Aynı alanı şu sayfalarda:"))
        self.range_edit = QLineEdit()
        self.range_edit.setPlaceholderText(_("örn. 1-{total} veya 2, 5, 8").format(total=total))
        self.range_edit.textEdited.connect(lambda _t: self.multi_rb.setChecked(True))
        row.addWidget(self.multi_rb)
        row.addWidget(self.range_edit, 1)
        hint = QLabel(_("Her sayfadaki aynı bölge ayrı bir kâğıda basılır "
                      "(etiket, fiş, form kesiti gibi)."))
        hint.setProperty("hint", True)
        hint.setWordWrap(True)
        pgl.addWidget(self.this_rb)
        pgl.addLayout(row)
        pgl.addWidget(hint)
        lay.addWidget(pages_box)

        # --- düğmeler
        buttons = QHBoxLayout()
        pdf_btn = QPushButton(_("PDF olarak kaydet…"))
        pdf_btn.setToolTip(_("Alanı gerçek boyutta, vektör kalitesinde ayrı bir PDF'e kaydeder;\n"
                           "metin seçilebilir kalır. Ölçek seçenekleri uygulanmaz."))
        pdf_btn.clicked.connect(self._choose_pdf)
        cancel = QPushButton(_("Vazgeç"))
        cancel.clicked.connect(self.reject)
        ok = QPushButton(_("Önizle ve yazdır…"))
        ok.setProperty("accent", True)
        ok.setDefault(True)
        ok.clicked.connect(self._choose_print)
        buttons.addWidget(pdf_btn)
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(ok)
        lay.addLayout(buttons)

    def _choose_print(self):
        if self._validate():
            self.action = self.PRINT
            self.accept()

    def _choose_pdf(self):
        if self._validate():
            self.action = self.PDF
            self.accept()

    def _validate(self) -> bool:
        if self.multi_rb.isChecked() and not self.pages():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, _("Sayfa aralığı"), _("Geçerli bir sayfa aralığı girin."))
            return False
        return True

    def pages(self) -> list[int]:
        if self.multi_rb.isChecked():
            return parse_page_range(self.range_edit.text(), self.total)
        return [self.pno]

    def options(self) -> dict:
        ap = self._ap
        if self.actual_rb.isChecked():
            mode = ap.ACTUAL
        elif self.custom_rb.isChecked():
            mode = ap.CUSTOM
        else:
            mode = ap.FIT
        return {
            "mode": mode,
            "scale": self.custom_pct.value() / 100.0,
            "upscale": not self.no_upscale.isChecked(),
            "center": self.center_cb.isChecked(),
            "marks": self.marks_cb.isChecked(),
        }
