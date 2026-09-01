"""Açıklama (annotation) işlemleri: vurgu, not, çizim, şekil, damga, bağlantı."""
from __future__ import annotations

from dataclasses import dataclass

import pymupdf

MARKUP_ADDERS = {
    "highlight": "add_highlight_annot",
    "underline": "add_underline_annot",
    "strikeout": "add_strikeout_annot",
    "squiggly": "add_squiggly_annot",
}

TYPE_NAMES = {
    pymupdf.PDF_ANNOT_TEXT: "Yapışkan not",
    pymupdf.PDF_ANNOT_FREE_TEXT: "Serbest metin",
    pymupdf.PDF_ANNOT_LINE: "Çizgi",
    pymupdf.PDF_ANNOT_SQUARE: "Dikdörtgen",
    pymupdf.PDF_ANNOT_CIRCLE: "Elips",
    pymupdf.PDF_ANNOT_POLYGON: "Çokgen",
    pymupdf.PDF_ANNOT_POLY_LINE: "Çoklu çizgi",
    pymupdf.PDF_ANNOT_HIGHLIGHT: "Vurgu",
    pymupdf.PDF_ANNOT_UNDERLINE: "Altı çizili",
    pymupdf.PDF_ANNOT_SQUIGGLY: "Dalgalı",
    pymupdf.PDF_ANNOT_STRIKE_OUT: "Üstü çizili",
    pymupdf.PDF_ANNOT_STAMP: "Damga",
    pymupdf.PDF_ANNOT_CARET: "Şapka",
    pymupdf.PDF_ANNOT_INK: "Serbest çizim",
    pymupdf.PDF_ANNOT_FILE_ATTACHMENT: "Dosya eki",
    pymupdf.PDF_ANNOT_REDACT: "Karartma",
    pymupdf.PDF_ANNOT_WIDGET: "Form alanı",
}

STAMP_TEXTS = [
    "Approved", "AsIs", "Confidential", "Departmental", "Draft", "Experimental",
    "Expired", "Final", "ForComment", "ForPublicRelease", "NotApproved",
    "NotForPublicRelease", "Sold", "TopSecret",
]


@dataclass
class AnnotInfo:
    pno: int
    xref: int
    type_id: int
    type_name: str
    rect: pymupdf.Rect
    author: str
    content: str
    modified: str


def list_annots(document, pno: int) -> list[AnnotInfo]:
    out = []
    try:
        page = document.page(pno)
    except Exception:
        return out
    for a in page.annots():
        info = a.info or {}
        out.append(AnnotInfo(
            pno=pno, xref=a.xref, type_id=a.type[0],
            type_name=TYPE_NAMES.get(a.type[0], a.type[1]),
            rect=pymupdf.Rect(a.rect),
            author=info.get("title", ""), content=info.get("content", ""),
            modified=info.get("modDate", ""),
        ))
    return out


def all_annots(document) -> list[AnnotInfo]:
    out = []
    for pno in range(document.page_count):
        out.extend(list_annots(document, pno))
    return out


def annot_at(page: pymupdf.Page, point) -> pymupdf.Annot | None:
    p = pymupdf.Point(point)
    best = None
    for a in page.annots():
        if a.type[0] == pymupdf.PDF_ANNOT_WIDGET:
            continue
        r = pymupdf.Rect(a.rect)
        if p in r and (best is None or r.get_area() < pymupdf.Rect(best.rect).get_area()):
            best = a
    return best


def _finish(annot, *, color=None, fill=None, opacity=1.0, width=None,
            author="", content="", subject=""):
    if color is not None or fill is not None:
        colors = {}
        if color is not None:
            colors["stroke"] = tuple(color)
        if fill is not None:
            colors["fill"] = tuple(fill)
        try:
            annot.set_colors(**colors)
        except Exception:
            pass
    if width is not None:
        try:
            annot.set_border(width=width)
        except Exception:
            pass
    if opacity is not None and opacity < 1.0:
        try:
            annot.set_opacity(float(opacity))
        except Exception:
            pass
    if author or content or subject:
        try:
            annot.set_info(title=author or None, content=content or None,
                           subject=subject or None)
        except Exception:
            pass
    annot.update()
    return annot


# ------------------------------------------------------------------ işaretleme
def add_markup(document, pno: int, kind: str, quads, *, color=(1, 0.85, 0.2),
               opacity: float = 1.0, author: str = "", content: str = ""):
    method = MARKUP_ADDERS[kind]
    with document.edit({"highlight": "Vurgu", "underline": "Altını çiz",
                        "strikeout": "Üstünü çiz", "squiggly": "Dalgalı çizgi"}[kind],
                       pages=[pno]) as doc:
        page = doc[pno]
        annot = getattr(page, method)(list(quads))
        _finish(annot, color=color, opacity=opacity, author=author, content=content)


# ------------------------------------------------------------------ metin notu
def add_sticky_note(document, pno: int, point, text: str, *, icon: str = "Note",
                    color=(1, 0.85, 0.3), author: str = ""):
    with document.edit("Yapışkan not", pages=[pno]) as doc:
        annot = doc[pno].add_text_annot(pymupdf.Point(point), text, icon=icon)
        _finish(annot, color=color, author=author, content=text)


def add_free_text(document, pno: int, rect, text: str, *, fontsize: float = 12,
                  fontname: str = "helv", text_color=(0, 0, 0), fill_color=None,
                  border_color=None, border_width: float = 0.0, align: int = 0,
                  opacity: float = 1.0, author: str = "", rotate: int = 0):
    with document.edit("Serbest metin kutusu", pages=[pno]) as doc:
        annot = doc[pno].add_freetext_annot(
            pymupdf.Rect(rect), text, fontsize=fontsize, fontname=fontname,
            text_color=text_color, fill_color=fill_color, border_color=border_color,
            border_width=border_width, align=align, rotate=rotate,
        )
        if opacity < 1.0:
            annot.set_opacity(opacity)
        if author:
            annot.set_info(title=author, content=text)
        annot.update()


# -------------------------------------------------------------------- çizimler
def add_ink(document, pno: int, strokes: list[list[tuple]], *, color=(0.9, 0.1, 0.1),
            width: float = 2.0, opacity: float = 1.0, author: str = ""):
    hand = [[(float(p[0]), float(p[1])) for p in stroke]
            for stroke in strokes if len(stroke) > 1]
    if not hand:
        return
    with document.edit("Serbest çizim", pages=[pno]) as doc:
        annot = doc[pno].add_ink_annot(hand)
        _finish(annot, color=color, width=width, opacity=opacity, author=author)


def add_shape(document, pno: int, kind: str, p0, p1, *, color=(0.85, 0.1, 0.1),
              fill=None, width: float = 1.5, opacity: float = 1.0, author: str = "",
              content: str = ""):
    """kind: rect | ellipse | line | arrow | double_arrow"""
    r = pymupdf.Rect(min(p0[0], p1[0]), min(p0[1], p1[1]),
                     max(p0[0], p1[0]), max(p0[1], p1[1]))
    label = {"rect": "Dikdörtgen", "ellipse": "Elips", "line": "Çizgi",
             "arrow": "Ok", "double_arrow": "Çift ok"}.get(kind, "Şekil")
    with document.edit(label, pages=[pno]) as doc:
        page = doc[pno]
        if kind == "rect":
            annot = page.add_rect_annot(r)
        elif kind == "ellipse":
            annot = page.add_circle_annot(r)
        else:
            annot = page.add_line_annot(pymupdf.Point(p0), pymupdf.Point(p1))
            if kind == "arrow":
                annot.set_line_ends(pymupdf.PDF_ANNOT_LE_NONE,
                                    pymupdf.PDF_ANNOT_LE_OPEN_ARROW)
            elif kind == "double_arrow":
                annot.set_line_ends(pymupdf.PDF_ANNOT_LE_OPEN_ARROW,
                                    pymupdf.PDF_ANNOT_LE_OPEN_ARROW)
        _finish(annot, color=color, fill=fill, width=width, opacity=opacity,
                author=author, content=content)


def add_polygon(document, pno: int, points: list[tuple], *, closed: bool = True,
                color=(0.85, 0.1, 0.1), fill=None, width: float = 1.5,
                opacity: float = 1.0, author: str = ""):
    pts = [pymupdf.Point(p) for p in points]
    if len(pts) < 2:
        return
    with document.edit("Çokgen" if closed else "Çoklu çizgi", pages=[pno]) as doc:
        page = doc[pno]
        annot = page.add_polygon_annot(pts) if closed else page.add_polyline_annot(pts)
        _finish(annot, color=color, fill=fill, width=width, opacity=opacity, author=author)


def add_stamp(document, pno: int, rect, stamp_index: int = 0, *, color=(0.1, 0.4, 0.1),
              opacity: float = 1.0, author: str = ""):
    with document.edit("Damga", pages=[pno]) as doc:
        annot = doc[pno].add_stamp_annot(pymupdf.Rect(rect), stamp=stamp_index)
        _finish(annot, color=color, opacity=opacity, author=author)


def add_caret(document, pno: int, rect, *, color=(0.1, 0.3, 0.9), author: str = ""):
    with document.edit("Şapka işareti", pages=[pno]) as doc:
        _finish(doc[pno].add_caret_annot(pymupdf.Rect(rect).tl), color=color, author=author)


def add_file_attachment(document, pno: int, point, path: str, *, author: str = ""):
    import os
    with open(path, "rb") as fh:
        data = fh.read()
    name = os.path.basename(path)
    with document.edit("Dosya eki", pages=[pno]) as doc:
        annot = doc[pno].add_file_annot(pymupdf.Point(point), data, name, desc=name)
        _finish(annot, author=author, content=name)


# ------------------------------------------------------------------ bağlantı
def add_link(document, pno: int, rect, *, uri: str = "", target_page: int | None = None):
    with document.edit("Bağlantı ekle", pages=[pno]) as doc:
        page = doc[pno]
        if uri:
            page.insert_link({"kind": pymupdf.LINK_URI, "from": pymupdf.Rect(rect), "uri": uri})
        elif target_page is not None:
            page.insert_link({
                "kind": pymupdf.LINK_GOTO, "from": pymupdf.Rect(rect),
                "page": target_page, "to": pymupdf.Point(0, 0),
            })


def list_links(document, pno: int) -> list[dict]:
    try:
        return document.page(pno).get_links()
    except Exception:
        return []


def delete_link(document, pno: int, rect) -> None:
    with document.edit("Bağlantıyı sil", pages=[pno]) as doc:
        page = doc[pno]
        target = pymupdf.Rect(rect)
        for link in page.get_links():
            if pymupdf.Rect(link["from"]).intersects(target):
                page.delete_link(link)


# ------------------------------------------------------------------ düzenleme
def delete_annot(document, pno: int, xref: int) -> None:
    with document.edit("Açıklamayı sil", pages=[pno]) as doc:
        page = doc[pno]
        for a in page.annots():
            if a.xref == xref:
                page.delete_annot(a)
                break


def delete_annots(document, items: list[tuple[int, int]]) -> None:
    by_page: dict[int, set[int]] = {}
    for pno, xref in items:
        by_page.setdefault(pno, set()).add(xref)
    with document.edit("Açıklamaları sil", structural=True) as doc:
        for pno, xrefs in by_page.items():
            page = doc[pno]
            for a in list(page.annots()):
                if a.xref in xrefs:
                    page.delete_annot(a)


def clear_annots(document, pages: list[int] | None = None) -> int:
    rng = pages if pages is not None else range(document.page_count)
    n = 0
    with document.edit("Tüm açıklamaları kaldır", structural=True) as doc:
        for pno in rng:
            page = doc[pno]
            for a in list(page.annots()):
                page.delete_annot(a)
                n += 1
    return n


def update_annot(document, pno: int, xref: int, *, content=None, author=None,
                 color=None, fill=None, opacity=None, width=None, rect=None) -> None:
    with document.edit("Açıklamayı düzenle", pages=[pno]) as doc:
        page = doc[pno]
        for a in page.annots():
            if a.xref != xref:
                continue
            if rect is not None:
                a.set_rect(pymupdf.Rect(rect))
            _finish(a, color=color, fill=fill,
                    opacity=1.0 if opacity is None else opacity,
                    width=width, author=author or "", content=content or "")
            break


def move_annot(document, pno: int, xref: int, dx: float, dy: float) -> None:
    with document.edit("Açıklamayı taşı", pages=[pno]) as doc:
        for a in doc[pno].annots():
            if a.xref == xref:
                r = pymupdf.Rect(a.rect) + (dx, dy, dx, dy)
                a.set_rect(r)
                a.update()
                break


def flatten(document, *, annots: bool = True, widgets: bool = True) -> None:
    """Açıklamaları/form alanlarını sayfa içeriğine gömer (düzenlenemez hale getirir)."""
    with document.edit("Düzleştir", structural=True) as doc:
        doc.bake(annots=annots, widgets=widgets)


# ---------------------------------------------------------------------- imza
def place_image(document, pno: int, rect, image_path: str, *, label: str = "Görüntü ekle",
                keep_proportion: bool = True, overlay: bool = True, rotate: int = 0):
    with document.edit(label, pages=[pno]) as doc:
        doc[pno].insert_image(pymupdf.Rect(rect), filename=image_path,
                              keep_proportion=keep_proportion, overlay=overlay,
                              rotate=rotate, alpha=-1)


def place_image_bytes(document, pno: int, rect, data: bytes, *, label: str = "İmza ekle",
                      keep_proportion: bool = True, overlay: bool = True):
    with document.edit(label, pages=[pno]) as doc:
        doc[pno].insert_image(pymupdf.Rect(rect), stream=data,
                              keep_proportion=keep_proportion, overlay=overlay, alpha=-1)
