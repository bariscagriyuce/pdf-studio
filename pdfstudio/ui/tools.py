"""Araç tanımları ve etkin araç ayarları."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


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


#: Sürükleyerek dikdörtgen çizen araçlar
RECT_TOOLS = {
    Tool.FREETEXT, Tool.RECT, Tool.ELLIPSE, Tool.IMAGE, Tool.SIGNATURE, Tool.STAMP,
    Tool.LINK, Tool.REDACT, Tool.CROP, Tool.TEXT_ADD, Tool.ERASE_AREA,
    Tool.FORM_TEXT, Tool.FORM_CHECK,
}
#: İki nokta arasında çizgi çizen araçlar
LINE_TOOLS = {Tool.LINE, Tool.ARROW, Tool.MEASURE}
#: Metin seçimi gerektiren araçlar
MARKUP_TOOLS = {Tool.HIGHLIGHT, Tool.UNDERLINE, Tool.STRIKEOUT, Tool.SQUIGGLY}

TOOL_LABELS = {
    Tool.SELECT: "Seç / Düzenle",
    Tool.PAN: "Kaydır (el)",
    Tool.TEXT_EDIT: "Metni düzenle",
    Tool.TEXT_ADD: "Metin ekle",
    Tool.HIGHLIGHT: "Vurgula",
    Tool.UNDERLINE: "Altını çiz",
    Tool.STRIKEOUT: "Üstünü çiz",
    Tool.SQUIGGLY: "Dalgalı çiz",
    Tool.NOTE: "Yapışkan not",
    Tool.FREETEXT: "Metin kutusu (açıklama)",
    Tool.INK: "Serbest çizim",
    Tool.ERASER: "Açıklama sil",
    Tool.RECT: "Dikdörtgen",
    Tool.ELLIPSE: "Elips",
    Tool.LINE: "Çizgi",
    Tool.ARROW: "Ok",
    Tool.POLYGON: "Çokgen",
    Tool.IMAGE: "Görüntü ekle",
    Tool.SIGNATURE: "İmza yerleştir",
    Tool.STAMP: "Damga",
    Tool.LINK: "Bağlantı",
    Tool.REDACT: "Karart (redaksiyon)",
    Tool.ERASE_AREA: "Alanı sil",
    Tool.CROP: "Kırp",
    Tool.FORM_TEXT: "Form: metin kutusu",
    Tool.FORM_CHECK: "Form: onay kutusu",
    Tool.MEASURE: "Ölç",
}

TOOL_HINTS = {
    Tool.SELECT: "Metin seçmek için sürükleyin; açıklamaya tıklayıp taşıyın/boyutlandırın.",
    Tool.TEXT_EDIT: "Bir metin bloğuna tıklayın; içeriği, punto ve rengi düzenleyin.",
    Tool.TEXT_ADD: "Sayfada bir kutu çizin ve yeni metni yazın (sayfa içeriğine işlenir).",
    Tool.HIGHLIGHT: "Vurgulamak istediğiniz metnin üzerinde sürükleyin.",
    Tool.INK: "Fare ile serbestçe çizin; bırakınca açıklama olarak eklenir.",
    Tool.REDACT: "Alanları işaretleyin, sonra 'Karartmaları uygula' deyin — içerik kalıcı silinir.",
    Tool.CROP: "Yeni sayfa sınırını çizin.",
    Tool.ERASE_AREA: "Silinecek alanı çizin; o alandaki metin/grafik kalıcı kaldırılır.",
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
