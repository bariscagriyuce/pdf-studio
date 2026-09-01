"""Metin düzenleme motoru: blok tespiti, yerinde değiştirme, ara-değiştir."""
from __future__ import annotations

from dataclasses import dataclass, field

import pymupdf

from .fonts import normalize_pdf_fontname, resolve_insert_font

ALIGN = {"sol": 0, "orta": 1, "sağ": 2, "iki yana": 3}
ALIGN_REV = {v: k for k, v in ALIGN.items()}


def srgb_to_rgb(value: int) -> tuple[float, float, float]:
    try:
        return tuple(pymupdf.sRGB_to_pdf(int(value)))
    except Exception:
        v = int(value)
        return ((v >> 16 & 255) / 255, (v >> 8 & 255) / 255, (v & 255) / 255)


@dataclass
class TextStyle:
    family: str = "Helvetica"
    size: float = 11.0
    color: tuple = (0.0, 0.0, 0.0)
    bold: bool = False
    italic: bool = False
    align: int = 0
    line_spacing: float = 1.15

    def copy(self) -> "TextStyle":
        return TextStyle(self.family, self.size, tuple(self.color), self.bold,
                         self.italic, self.align, self.line_spacing)


@dataclass
class TextSpan:
    text: str
    bbox: pymupdf.Rect
    style: TextStyle


@dataclass
class TextLine:
    text: str
    bbox: pymupdf.Rect
    spans: list[TextSpan] = field(default_factory=list)


@dataclass
class TextBlock:
    pno: int
    bbox: pymupdf.Rect
    lines: list[TextLine] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n".join(l.text for l in self.lines)

    @property
    def style(self) -> TextStyle:
        for line in self.lines:
            for span in line.spans:
                return span.style.copy()
        return TextStyle()


# ------------------------------------------------------------------ okuma
def _span_style(span: dict) -> TextStyle:
    family, bold, italic = normalize_pdf_fontname(span.get("font", ""))
    flags = span.get("flags", 0)
    bold = bold or bool(flags & 2 ** 4)
    italic = italic or bool(flags & 2 ** 1)
    return TextStyle(
        family=family,
        size=round(float(span.get("size", 11.0)), 2),
        color=srgb_to_rgb(span.get("color", 0)),
        bold=bold,
        italic=italic,
    )


def text_blocks(page: pymupdf.Page) -> list[TextBlock]:
    """Sayfadaki metin bloklarını stil bilgisiyle döndürür."""
    out: list[TextBlock] = []
    try:
        data = page.get_text("dict")
    except Exception:
        return out
    for block in data.get("blocks", []):
        if block.get("type") != 0:
            continue
        lines: list[TextLine] = []
        for line in block.get("lines", []):
            spans = [
                TextSpan(s.get("text", ""), pymupdf.Rect(s["bbox"]), _span_style(s))
                for s in line.get("spans", [])
            ]
            txt = "".join(s.text for s in spans)
            lines.append(TextLine(txt, pymupdf.Rect(line["bbox"]), spans))
        if lines:
            out.append(TextBlock(page.number, pymupdf.Rect(block["bbox"]), lines))
    return out


def block_at(page: pymupdf.Page, point) -> TextBlock | None:
    p = pymupdf.Point(point)
    best = None
    for blk in text_blocks(page):
        if p in blk.bbox:
            if best is None or blk.bbox.get_area() < best.bbox.get_area():
                best = blk
    return best


def line_at(page: pymupdf.Page, point) -> tuple[TextBlock, TextLine] | None:
    p = pymupdf.Point(point)
    for blk in text_blocks(page):
        if p not in blk.bbox:
            continue
        for line in blk.lines:
            r = pymupdf.Rect(line.bbox)
            r.y0 -= 1
            r.y1 += 1
            if p in r:
                return blk, line
    return None


def words_in_rect(page: pymupdf.Page, rect: pymupdf.Rect) -> list[tuple]:
    out = []
    for w in page.get_text("words"):
        r = pymupdf.Rect(w[:4])
        inter = r & rect
        if not inter.is_empty and inter.get_area() > r.get_area() * 0.35:
            out.append(w)
    return out


def selection_quads(page: pymupdf.Page, start, end) -> list[pymupdf.Quad]:
    """İki nokta arasındaki kelimeleri okuma sırasına göre seçer."""
    words = page.get_text("words")
    if not words:
        return []
    words.sort(key=lambda w: (w[5], w[6], w[7]))
    p0, p1 = pymupdf.Point(start), pymupdf.Point(end)
    if (p1.y, p1.x) < (p0.y, p0.x):
        p0, p1 = p1, p0

    def idx_for(pt, prefer_first: bool):
        best_i, best_d = None, None
        for i, w in enumerate(words):
            r = pymupdf.Rect(w[:4])
            if r.y0 - 2 <= pt.y <= r.y1 + 2:
                if r.x0 <= pt.x <= r.x1:
                    return i
                d = abs(r.x0 - pt.x) if pt.x < r.x0 else abs(pt.x - r.x1)
                if best_d is None or d < best_d:
                    best_i, best_d = i, d
        if best_i is not None:
            return best_i
        # aynı satırda kelime yoksa dikey olarak en yakın
        cands = [(abs((w[1] + w[3]) / 2 - pt.y), i) for i, w in enumerate(words)]
        cands.sort()
        return cands[0][1] if cands else (0 if prefer_first else len(words) - 1)

    i0 = idx_for(p0, True)
    i1 = idx_for(p1, False)
    if i0 > i1:
        i0, i1 = i1, i0
    return [pymupdf.Rect(w[:4]).quad for w in words[i0:i1 + 1]]


def rect_text(page: pymupdf.Page, rect: pymupdf.Rect) -> str:
    try:
        return page.get_textbox(rect)
    except Exception:
        return ""


# ------------------------------------------------------------- yazma / silme
def _insert_fitted(page: pymupdf.Page, rect: pymupdf.Rect, text: str, style: TextStyle,
                   shrink: bool = True) -> float:
    """Metni kutuya sığdırır; gerekiyorsa punto küçültür. Kalan yeri döndürür."""
    fontname, fontfile = resolve_insert_font(style.family, style.bold, style.italic, text)
    size = float(style.size)
    box = pymupdf.Rect(rect)
    for _ in range(48):
        rc = page.insert_textbox(
            box, text, fontname=fontname, fontfile=fontfile, fontsize=size,
            color=tuple(style.color), align=style.align,
            lineheight=style.line_spacing, rotate=0,
        )
        if rc >= 0 or not shrink or size <= 3.0:
            return rc
        size = max(3.0, size - max(0.4, size * 0.06))
    return -1.0


def _measured_height(text: str, width: float, style: TextStyle) -> float:
    """Metnin verilen genişlikte kaplayacağı yaklaşık yüksekliği hesaplar."""
    fontname, fontfile = resolve_insert_font(style.family, style.bold, style.italic, text)
    try:
        font = pymupdf.Font(fontfile=fontfile) if fontfile else pymupdf.Font(fontname)
    except Exception:
        font = pymupdf.Font("helv")
    lines = 0
    for para in text.split("\n"):
        if not para:
            lines += 1
            continue
        cur = ""
        n = 1
        for word in para.split(" "):
            trial = (cur + " " + word).strip()
            if font.text_length(trial, style.size) > width and cur:
                n += 1
                cur = word
            else:
                cur = trial
        lines += n
    return max(1, lines) * style.size * style.line_spacing + style.size * 0.5


def erase_region(page: pymupdf.Page, rect: pymupdf.Rect, *, fill=None,
                 remove_images: bool = False, remove_graphics: bool = False) -> None:
    """Bir alandaki içeriği gerçekten kaldırır (redaksiyon)."""
    page.add_redact_annot(pymupdf.Rect(rect), fill=fill, cross_out=False)
    page.apply_redactions(
        images=pymupdf.PDF_REDACT_IMAGE_REMOVE if remove_images else pymupdf.PDF_REDACT_IMAGE_NONE,
        graphics=(pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED if remove_graphics
                  else pymupdf.PDF_REDACT_LINE_ART_NONE),
        text=pymupdf.PDF_REDACT_TEXT_REMOVE,
    )


def replace_region_text(document, pno: int, rect: pymupdf.Rect, new_text: str,
                        style: TextStyle, *, background=None, grow: bool = True,
                        expand_width: bool = True, right_margin: float = 32.0,
                        label: str = "Metni düzenle") -> bool:
    """Bir alandaki metni siler ve yerine yeni metni aynı stille yazar.

    grow=True ise kutu, metin sığmadığında aşağı doğru büyür; expand_width=True
    ise tek satırlık bloklar sayfa sağ kenarına kadar genişleyebilir (böylece
    uzayan metin gereksiz yere alt satıra kaymaz).
    """
    with document.edit(label, pages=[pno]) as doc:
        page = doc[pno]
        box = pymupdf.Rect(rect)
        erase_region(page, box + (-0.6, -0.6, 0.6, 0.6), fill=background)
        page = doc[pno]  # redaksiyondan sonra sayfa nesnesini tazele
        if not new_text.strip():
            return True
        target = pymupdf.Rect(box)
        limit = max(target.x0 + 20.0, page.rect.x1 - right_margin)
        if expand_width and "\n" not in new_text.strip():
            target.x1 = max(target.x1, limit)
        target.x1 = min(page.rect.x1 - 2, target.x1)
        if grow:
            need = _measured_height(new_text, max(8.0, target.width), style)
            if need > target.height:
                target.y1 = min(page.rect.y1 - 2, target.y0 + need)
        target.y0 -= style.size * 0.22  # ilk satırın taban çizgisini hizala
        rc = _insert_fitted(page, target, new_text, style)
        return rc >= 0


def insert_text_box(document, pno: int, rect: pymupdf.Rect, text: str,
                    style: TextStyle, *, label: str = "Metin ekle") -> bool:
    with document.edit(label, pages=[pno]) as doc:
        page = doc[pno]
        box = pymupdf.Rect(rect)
        if box.height < style.size * 1.4:
            box.y1 = box.y0 + style.size * 1.6
        if box.width < 12:
            box.x1 = box.x0 + 200
        rc = _insert_fitted(page, box, text, style)
        return rc >= 0


def delete_text_region(document, pno: int, rect: pymupdf.Rect, *, background=None,
                       remove_images: bool = False, remove_graphics: bool = False,
                       label: str = "Alanı sil") -> None:
    with document.edit(label, pages=[pno]) as doc:
        erase_region(doc[pno], pymupdf.Rect(rect), fill=background,
                     remove_images=remove_images, remove_graphics=remove_graphics)


def redact_areas(document, areas: list[tuple[int, pymupdf.Rect]], *, fill=(0, 0, 0),
                 remove_images: bool = True) -> None:
    """Gerçek karartma: içerik kaldırılır, üzerine dolgu çizilir."""
    by_page: dict[int, list[pymupdf.Rect]] = {}
    for pno, r in areas:
        by_page.setdefault(pno, []).append(pymupdf.Rect(r))
    with document.edit("Karart (redaksiyon)", structural=True) as doc:
        for pno, rects in by_page.items():
            page = doc[pno]
            for r in rects:
                page.add_redact_annot(r, fill=fill, cross_out=False)
            page.apply_redactions(
                images=(pymupdf.PDF_REDACT_IMAGE_REMOVE if remove_images
                        else pymupdf.PDF_REDACT_IMAGE_NONE),
                graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                text=pymupdf.PDF_REDACT_TEXT_REMOVE,
            )


# --------------------------------------------------------------- ara / değiştir
def find_all(document, needle: str, *, case_sensitive: bool = False,
             whole_words: bool = False, pages: list[int] | None = None) -> list[tuple[int, pymupdf.Rect]]:
    if not needle:
        return []
    hits: list[tuple[int, pymupdf.Rect]] = []
    rng = pages if pages is not None else range(document.page_count)
    for pno in rng:
        page = document.page(pno)
        try:
            rects = page.search_for(needle)  # PyMuPDF varsayılan olarak büyük/küçük harf duyarsız
        except Exception:
            continue
        for r in rects:
            if case_sensitive and page.get_textbox(r).strip() != needle:
                continue
            if whole_words:
                bigger = pymupdf.Rect(r.x0 - 2.5, r.y0, r.x1 + 2.5, r.y1)
                around = page.get_textbox(bigger).strip()
                if around and around.lower() != needle.lower():
                    continue
            hits.append((pno, r))
    return hits


def replace_all(document, needle: str, replacement: str, *, style: TextStyle | None = None,
                pages: list[int] | None = None, match_style: bool = True) -> int:
    """Belge genelinde metin değiştirir. Değiştirilen örnek sayısını döndürür."""
    if not needle:
        return 0
    rng = list(pages if pages is not None else range(document.page_count))
    count = 0
    with document.edit(f"'{needle}' değiştir", structural=True) as doc:
        for pno in rng:
            page = doc[pno]
            rects = page.search_for(needle)
            if not rects:
                continue
            styles: list[TextStyle] = []
            if match_style:
                blocks = text_blocks(page)
                for r in rects:
                    st = None
                    for blk in blocks:
                        for line in blk.lines:
                            for span in line.spans:
                                if not (span.bbox & r).is_empty:
                                    st = span.style.copy()
                                    break
                            if st:
                                break
                        if st:
                            break
                    styles.append(st or (style.copy() if style else TextStyle()))
            else:
                styles = [(style.copy() if style else TextStyle()) for _ in rects]

            for r in rects:
                page.add_redact_annot(r, fill=None, cross_out=False)
            page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                                  graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                                  text=pymupdf.PDF_REDACT_TEXT_REMOVE)
            page = doc[pno]
            for r, st in zip(rects, styles):
                box = pymupdf.Rect(r.x0, r.y0 - st.size * 0.25, page.rect.x1 - 2,
                                   r.y1 + st.size * 0.3)
                st2 = st.copy()
                st2.align = 0
                st2.line_spacing = 1.0
                _insert_fitted(page, box, replacement, st2, shrink=True)
                count += 1
    return count
