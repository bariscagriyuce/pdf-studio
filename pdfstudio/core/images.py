"""Sayfa içindeki görüntüleri listeleme, çıkarma, değiştirme ve silme."""
from __future__ import annotations

import os
from dataclasses import dataclass

import pymupdf


@dataclass
class ImageInfo:
    pno: int
    xref: int
    rect: pymupdf.Rect
    width: int
    height: int
    colorspace: str
    bpc: int
    size: int


def list_images(document, pno: int) -> list[ImageInfo]:
    out: list[ImageInfo] = []
    try:
        page = document.page(pno)
    except Exception:
        return out
    seen: set[tuple] = set()
    for info in page.get_image_info(xrefs=True):
        xref = info.get("xref", 0)
        rect = pymupdf.Rect(info["bbox"])
        key = (xref, round(rect.x0, 1), round(rect.y0, 1))
        if key in seen:
            continue
        seen.add(key)
        out.append(ImageInfo(
            pno=pno, xref=xref, rect=rect,
            width=info.get("width", 0), height=info.get("height", 0),
            colorspace=str(info.get("cs-name", info.get("colorspace", ""))),
            bpc=info.get("bpc", 8), size=info.get("size", 0),
        ))
    return out


def image_at(document, pno: int, point) -> ImageInfo | None:
    p = pymupdf.Point(point)
    best = None
    for img in list_images(document, pno):
        if p in img.rect and (best is None or img.rect.get_area() < best.rect.get_area()):
            best = img
    return best


def extract_image(document, xref: int, out_path: str) -> str:
    data = document.doc.extract_image(xref)
    ext = data.get("ext", "png")
    root, cur = os.path.splitext(out_path)
    if cur.lower().lstrip(".") != ext:
        out_path = f"{root}.{ext}"
    with open(out_path, "wb") as fh:
        fh.write(data["image"])
    return out_path


def extract_all_images(document, out_dir: str, *, min_side: int = 8) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    written: list[str] = []
    seen: set[int] = set()
    for pno in range(document.page_count):
        for img in list_images(document, pno):
            if img.xref in seen or not img.xref:
                continue
            seen.add(img.xref)
            try:
                data = document.doc.extract_image(img.xref)
            except Exception:
                continue
            if data.get("width", 0) < min_side or data.get("height", 0) < min_side:
                continue
            path = os.path.join(out_dir, f"s{pno + 1:03d}_x{img.xref}.{data.get('ext', 'png')}")
            with open(path, "wb") as fh:
                fh.write(data["image"])
            written.append(path)
    return written


def delete_image(document, pno: int, rect) -> None:
    """Görüntüyü sayfadan gerçekten kaldırır (redaksiyon ile)."""
    with document.edit("Görüntüyü sil", pages=[pno]) as doc:
        page = doc[pno]
        page.add_redact_annot(pymupdf.Rect(rect) + (-0.5, -0.5, 0.5, 0.5), fill=None,
                              cross_out=False)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                              text=pymupdf.PDF_REDACT_TEXT_NONE)


def replace_image(document, pno: int, rect, new_path: str, *, keep_proportion: bool = True) -> None:
    with document.edit("Görüntüyü değiştir", pages=[pno]) as doc:
        page = doc[pno]
        box = pymupdf.Rect(rect)
        page.add_redact_annot(box + (-0.5, -0.5, 0.5, 0.5), fill=None, cross_out=False)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                              text=pymupdf.PDF_REDACT_TEXT_NONE)
        doc[pno].insert_image(box, filename=new_path, keep_proportion=keep_proportion,
                              overlay=True, alpha=-1)


def move_resize_image(document, pno: int, old_rect, new_rect, *,
                      keep_proportion: bool = True) -> None:
    """Görüntüyü kaldırıp yeni konum/boyutta yeniden yerleştirir."""
    old = pymupdf.Rect(old_rect)
    try:
        data = document.doc.extract_image(_xref_for(document, pno, old))
        blob = data["image"]
    except Exception:
        blob = None
    if blob is None:
        return
    with document.edit("Görüntüyü taşı/boyutlandır", pages=[pno]) as doc:
        page = doc[pno]
        page.add_redact_annot(old + (-0.5, -0.5, 0.5, 0.5), fill=None, cross_out=False)
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                              text=pymupdf.PDF_REDACT_TEXT_NONE)
        doc[pno].insert_image(pymupdf.Rect(new_rect), stream=blob,
                              keep_proportion=keep_proportion, overlay=True, alpha=-1)


def _xref_for(document, pno: int, rect: pymupdf.Rect) -> int:
    best, area = 0, -1.0
    for img in list_images(document, pno):
        inter = img.rect & rect
        if not inter.is_empty and inter.get_area() > area:
            best, area = img.xref, inter.get_area()
    return best
