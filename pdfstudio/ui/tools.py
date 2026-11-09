"""Araç tanımları ve etkin araç ayarları."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..i18n import N_


class Tool(str, Enum):
    SELECT = "select"
    PAN = "pan"
    TEXT_EDIT = "text_edit"
    TEXT_ADD = "text_add"
    HIGHLIGHT = "highlight"
    UNDERLINE = "underline"
    STRIKEOUT = "strikeout"
    SQUIGGLY = "squiggly"
    NOTE = "note"
    FREETEXT = "freetext"
    INK = "ink"
    ERASER = "eraser"
    RECT = "rect"
    ELLIPSE = "ellipse"
    LINE = "line"
    ARROW = "arrow"
    POLYGON = "polygon"
    IMAGE = "image"
    SIGNATURE = "signature"
    STAMP = "stamp"
    LINK = "link"
    REDACT = "redact"
    ERASE_AREA = "erase_area"
    CROP = "crop"
    FORM_TEXT = "form_text"
    FORM_CHECK = "form_check"
    MEASURE = "measure"
    PRINT_AREA = "print_area"


#: Sürükleyerek dikdörtgen çizen araçlar
RECT_TOOLS = {
    Tool.FREETEXT, Tool.RECT, Tool.ELLIPSE, Tool.IMAGE, Tool.SIGNATURE, Tool.STAMP,
    Tool.LINK, Tool.REDACT, Tool.CROP, Tool.TEXT_ADD, Tool.ERASE_AREA,
    Tool.FORM_TEXT, Tool.FORM_CHECK, Tool.PRINT_AREA,
}
#: İki nokta arasında çizgi çizen araçlar
LINE_TOOLS = {Tool.LINE, Tool.ARROW, Tool.MEASURE}
#: Metin seçimi gerektiren araçlar
MARKUP_TOOLS = {Tool.HIGHLIGHT, Tool.UNDERLINE, Tool.STRIKEOUT, Tool.SQUIGGLY}

TOOL_LABELS = {
    Tool.SELECT: N_("Seç / Düzenle"),
    Tool.PAN: N_("Kaydır (el)"),
    Tool.TEXT_EDIT: N_("Metni düzenle"),
    Tool.TEXT_ADD: N_("Metin ekle"),
    Tool.HIGHLIGHT: N_("Vurgula"),
    Tool.UNDERLINE: N_("Altını çiz"),
    Tool.STRIKEOUT: N_("Üstünü çiz"),
    Tool.SQUIGGLY: N_("Dalgalı çiz"),
    Tool.NOTE: N_("Yapışkan not"),
    Tool.FREETEXT: N_("Metin kutusu (açıklama)"),
    Tool.INK: N_("Serbest çizim"),
    Tool.ERASER: N_("Açıklama sil"),
    Tool.RECT: N_("Dikdörtgen"),
    Tool.ELLIPSE: N_("Elips"),
    Tool.LINE: N_("Çizgi"),
    Tool.ARROW: N_("Ok"),
    Tool.POLYGON: N_("Çokgen"),
    Tool.IMAGE: N_("Görüntü ekle"),
    Tool.SIGNATURE: N_("İmza yerleştir"),
    Tool.STAMP: N_("Damga"),
    Tool.LINK: N_("Bağlantı"),
    Tool.REDACT: N_("Karart (redaksiyon)"),
    Tool.ERASE_AREA: N_("Alanı sil"),
    Tool.CROP: N_("Kırp"),
    Tool.FORM_TEXT: N_("Form: metin kutusu"),
    Tool.FORM_CHECK: N_("Form: onay kutusu"),
    Tool.MEASURE: N_("Ölç"),
    Tool.PRINT_AREA: N_("Alanı yazdır"),
}

TOOL_HINTS = {
    Tool.SELECT: N_("Metin seçmek için sürükleyin; açıklamaya tıklayıp taşıyın/boyutlandırın."),
    Tool.TEXT_EDIT: N_("Bir metin bloğuna tıklayın; içeriği, punto ve rengi düzenleyin."),
    Tool.TEXT_ADD: N_("Sayfada bir kutu çizin ve yeni metni yazın (sayfa içeriğine işlenir)."),
    Tool.HIGHLIGHT: N_("Vurgulamak istediğiniz metnin üzerinde sürükleyin."),
    Tool.INK: N_("Fare ile serbestçe çizin; bırakınca açıklama olarak eklenir."),
    Tool.REDACT: N_("Alanları işaretleyin, sonra 'Karartmaları uygula' deyin — içerik kalıcı silinir."),
    Tool.CROP: N_("Yeni sayfa sınırını çizin."),
    Tool.ERASE_AREA: N_("Silinecek alanı çizin; o alandaki metin/grafik kalıcı kaldırılır."),
    Tool.PRINT_AREA: N_("Yazdırmak istediğiniz alanı çizin; yalnızca o bölge basılır."),
}


@dataclass
class ToolSettings:
    color: tuple = (0.90, 0.16, 0.16)
    fill: tuple | None = None
    text_color: tuple = (0.0, 0.0, 0.0)
    highlight_color: tuple = (1.0, 0.90, 0.25)
    width: float = 2.0
    opacity: float = 1.0
    fontsize: float = 12.0
    font_family: str = "Helvetica"
    bold: bool = False
    italic: bool = False
    align: int = 0
    line_spacing: float = 1.15
    author: str = ""
    note_icon: str = "Note"
    stamp_index: int = 0
    image_path: str = ""
    signature_path: str = ""
    signature_bytes: bytes | None = None
    redact_fill: tuple = (0.0, 0.0, 0.0)
    pending: dict = field(default_factory=dict)

    def markup_color(self, tool: Tool) -> tuple:
        return self.highlight_color if tool == Tool.HIGHLIGHT else self.color
