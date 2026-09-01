"""Küçük yeniden kullanılabilir arayüz bileşenleri."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (QColorDialog, QComboBox, QFormLayout, QFrame, QHBoxLayout,
                               QLabel, QPushButton, QSizePolicy, QSlider, QToolButton,
                               QVBoxLayout, QWidget)

from . import icons


def rgb_to_qcolor(rgb) -> QColor:
    if rgb is None:
        return QColor(0, 0, 0, 0)
    return QColor.fromRgbF(float(rgb[0]), float(rgb[1]), float(rgb[2]))


def qcolor_to_rgb(c: QColor) -> tuple:
    return (c.redF(), c.greenF(), c.blueF())


class ColorButton(QPushButton):
    """Renk seçici düğme; None (şeffaf) desteği isteğe bağlı."""

    colorChanged = Signal(object)

    def __init__(self, color=(0, 0, 0), allow_none: bool = False, parent=None):
        super().__init__(parent)
        self._color = color
        self.allow_none = allow_none
        self.setFixedSize(QSize(34, 26))
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._pick)
        self._refresh()

    def color(self):
        return self._color

    def set_color(self, rgb):
        self._color = rgb
        self._refresh()

    def _refresh(self):
        px = QPixmap(28, 18)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        if self._color is None:
            p.setPen(QColor("#888"))
            p.setBrush(QColor("#ffffff"))
            p.drawRoundedRect(0, 0, 27, 17, 4, 4)
            p.setPen(QColor("#e5484d"))
            p.drawLine(3, 15, 24, 2)
        else:
            p.setPen(QColor("#00000055"))
            p.setBrush(rgb_to_qcolor(self._color))
            p.drawRoundedRect(0, 0, 27, 17, 4, 4)
        p.end()
        self.setIcon(QIcon(px))
        self.setIconSize(QSize(28, 18))

    def _pick(self):
        start = rgb_to_qcolor(self._color) if self._color else QColor("#ffffff")
        dlg = QColorDialog(start, self)
        dlg.setWindowTitle("Renk seç")
        if self.allow_none:
            dlg.setOption(QColorDialog.ShowAlphaChannel, False)
        if dlg.exec():
            self._color = qcolor_to_rgb(dlg.currentColor())
            self._refresh()
            self.colorChanged.emit(self._color)

    def contextMenuEvent(self, event):
        if self.allow_none:
            self._color = None
            self._refresh()
            self.colorChanged.emit(None)


class Section(QWidget):
    """Başlıklı, katlanabilir bölüm."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._open = True
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.header = QToolButton()
        self.header.setText("  " + title)
        self.header.setCheckable(True)
        self.header.setChecked(True)
        self.header.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.header.setArrowType(Qt.DownArrow)
        self.header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.header.setProperty("section", True)
        self.header.setStyleSheet(
            "QToolButton { text-align: left; font-weight: 600; padding: 6px 4px;"
            " background: transparent; border: none; }"
            "QToolButton:checked { background: transparent; }"
            "QToolButton:hover { background: rgba(127,127,127,0.12); }")
        self.header.toggled.connect(self._toggle)
        outer.addWidget(self.header)

        self.body = QWidget()
        self.form = QFormLayout(self.body)
        self.form.setContentsMargins(8, 2, 4, 8)
        self.form.setSpacing(7)
        self.form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        outer.addWidget(self.body)

    def _toggle(self, checked: bool):
        self.body.setVisible(checked)
        self.header.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

    def add_row(self, label: str, widget):
        self.form.addRow(label, widget)
        return widget

    def add_widget(self, widget):
        self.form.addRow(widget)
        return widget


class LabeledSlider(QWidget):
    valueChanged = Signal(float)

    def __init__(self, minimum=0, maximum=100, value=100, suffix="%", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(7)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(value)
        self.label = QLabel(f"{value}{suffix}")
        self.label.setMinimumWidth(38)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.suffix = suffix
        lay.addWidget(self.slider, 1)
        lay.addWidget(self.label)
        self.slider.valueChanged.connect(self._changed)

    def _changed(self, v):
        self.label.setText(f"{v}{self.suffix}")
        self.valueChanged.emit(float(v))

    def value(self) -> int:
        return self.slider.value()

    def setValue(self, v):
        self.slider.setValue(int(v))


class HLine(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        self.setFixedHeight(1)


def tool_button(name: str, tooltip: str, color: str, checkable: bool = False,
                size: int = 20) -> QToolButton:
    b = QToolButton()
    b.setIcon(icons.icon(name, color, size))
    b.setIconSize(QSize(size, size))
    b.setToolTip(tooltip)
    b.setCheckable(checkable)
    b.setCursor(Qt.PointingHandCursor)
    return b


def font_combo(current: str = "Helvetica") -> QComboBox:
    from ..core.fonts import FontManager
    cb = QComboBox()
    cb.setEditable(True)
    fams = FontManager.instance().families()
    base = ["Helvetica", "Times-Roman", "Courier"]
    cb.addItems(base + ["──────────"] + fams)
    cb.setCurrentText(current)
    cb.setMaxVisibleItems(24)
    cb.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    cb.setMinimumContentsLength(8)
    cb.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
    return cb
