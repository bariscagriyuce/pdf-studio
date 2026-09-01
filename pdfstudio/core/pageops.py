"""Sayfa düzeyi işlemler: ekle, sil, döndür, taşı, kırp, birleştir, böl, filigran."""
from __future__ import annotations

import os

import pymupdf

PAGE_PRESETS = {
    "A4 (595 x 842)": (595.0, 842.0),
    "A3 (842 x 1191)": (842.0, 1191.0),
    "A5 (420 x 595)": (420.0, 595.0),
    "Letter (612 x 792)": (612.0, 792.0),
    "Legal (612 x 1008)": (612.0, 1008.0),
    "Tabloid (792 x 1224)": (792.0, 1224.0),
}


# --------------------------------------------------------------------- ekleme
def insert_blank(document, index: int, width: float, height: float, count: int = 1) -> None:
    with document.edit("Boş sayfa ekle", structural=True) as doc:
        for i in range(count):
            doc.new_page(pno=index + i, width=width, height=height)


def duplicate_pages(document, indices: list[int]) -> None:
    indices = sorted(set(indices))
    with document.edit("Sayfayı çoğalt", structural=True) as doc:
        for offset, pno in enumerate(indices):
            src = pno + offset
            doc.fullcopy_page(src, src + 1)


def delete_pages(document, indices: list[int]) -> None:
    keep = [i for i in range(document.page_count) if i not in set(indices)]
    if not keep:
        raise ValueError("Belgede en az bir sayfa kalmalı")
    with document.edit("Sayfa sil", structural=True) as doc:
        doc.select(keep)


def reorder_pages(document, new_order: list[int]) -> None:
    with document.edit("Sayfaları yeniden sırala", structural=True) as doc:
        doc.select(new_order)


def move_pages(document, indices: list[int], target: int) -> None:
    """`indices` sayfalarını, taşımadan önceki `target` konumunun önüne getirir."""
    n = document.page_count
    sel = sorted(set(indices))
    rest = [i for i in range(n) if i not in set(sel)]
    before = [i for i in rest if i < target]
    after = [i for i in rest if i >= target]
    reorder_pages(document, before + sel + after)


def rotate_pages(document, indices: list[int], delta: int) -> None:
    with document.edit("Sayfayı döndür", structural=True) as doc:
        for pno in indices:
            page = doc[pno]
            page.set_rotation((page.rotation + delta) % 360)


def set_rotation(document, indices: list[int], value: int) -> None:
    with document.edit("Dönüşü ayarla", structural=True) as doc:
        for pno in indices:
            doc[pno].set_rotation(value % 360)


def crop_page(document, indices: list[int], rect: pymupdf.Rect) -> None:
    with document.edit("Sayfayı kırp", structural=True) as doc:
        for pno in indices:
            page = doc[pno]
            r = pymupdf.Rect(rect) & page.mediabox
            if r.is_empty:
                continue
            page.set_cropbox(r)


def reset_crop(document, indices: list[int]) -> None:
    with document.edit("Kırpmayı sıfırla", structural=True) as doc:
        for pno in indices:
            page = doc[pno]
            page.set_cropbox(page.mediabox)


def resize_pages(document, indices: list[int], width: float, height: float) -> None:
    """Sayfa içeriğini yeni boyuta ölçekleyerek yeniden oluşturur."""
    with document.edit("Sayfa boyutunu değiştir", structural=True) as doc:
        src = pymupdf.open("pdf", doc.tobytes())  # show_pdf_page kaynak != hedef ister
        targets = sorted(set(indices))
        for k, pno in enumerate(targets):
            cur = pno + k  # daha önce eklenen sayfalar kadar kayma
            newpage = doc.new_page(pno=cur + 1, width=width, height=height)
            newpage.show_pdf_page(newpage.rect, src, pno)
        drop = {pno + k for k, pno in enumerate(targets)}
        keep = [i for i in range(doc.page_count) if i not in drop]
        doc.select(keep)
        src.close()


# ------------------------------------------------------------------ birleştir
def merge_files(document, paths: list[str], at: int, passwords: dict[str, str] | None = None) -> int:
    added = 0
    passwords = passwords or {}
    with document.edit("PDF birleştir", structural=True) as doc:
        pos = at
        for p in paths:
            src = pymupdf.open(p)
            if src.needs_pass:
                src.authenticate(passwords.get(p, ""))
            if not src.is_pdf:
                data = src.convert_to_pdf()
                src.close()
                src = pymupdf.open("pdf", data)
            doc.insert_pdf(src, start_at=pos)
            pos += src.page_count
            added += src.page_count
            src.close()
    return added


def insert_images_as_pages(document, paths: list[str], at: int) -> int:
    added = 0
    with document.edit("Görüntüyü sayfa olarak ekle", structural=True) as doc:
        pos = at
        for p in paths:
            img = pymupdf.open(p)
            data = img.convert_to_pdf()
            img.close()
            src = pymupdf.open("pdf", data)
            doc.insert_pdf(src, start_at=pos)
            pos += src.page_count
            added += src.page_count
            src.close()
    return added


# ------------------------------------------------------------------- çıkarma
def extract_pages(document, indices: list[int], out_path: str) -> str:
    out = pymupdf.open()
    for pno in indices:
        out.insert_pdf(document.doc, from_page=pno, to_page=pno)
    out.save(out_path, garbage=4, deflate=True)
    out.close()
    return out_path


def split_by_ranges(document, ranges: list[tuple[int, int]], out_dir: str, stem: str) -> list[str]:
    files = []
    for idx, (a, b) in enumerate(ranges, 1):
        out = pymupdf.open()
        out.insert_pdf(document.doc, from_page=a, to_page=b)
        path = os.path.join(out_dir, f"{stem}_{idx:02d}_{a + 1}-{b + 1}.pdf")
        out.save(path, garbage=4, deflate=True)
        out.close()
        files.append(path)
    return files


def split_every(document, n: int, out_dir: str, stem: str) -> list[str]:
    total = document.page_count
    ranges = [(i, min(i + n - 1, total - 1)) for i in range(0, total, n)]
    return split_by_ranges(document, ranges, out_dir, stem)


# ------------------------------------------------------------------ filigran
def add_text_watermark(
    document,
    text: str,
    indices: list[int],
    *,
    fontsize: int = 48,
    color=(0.6, 0.6, 0.6),
    opacity: float = 0.25,
    angle: int = 45,
    fontname: str = "helv",
    behind: bool = False,
) -> None:
    with document.edit("Filigran ekle", structural=True) as doc:
        for pno in indices:
            page = doc[pno]
            rect = page.rect
            font = pymupdf.Font(fontname)
            width = font.text_length(text, fontsize)
            cx, cy = rect.width / 2, rect.height / 2
            shape = page.new_shape()
            shape.insert_text(
                pymupdf.Point(cx - width / 2, cy),
                text,
                fontname=fontname,
                fontsize=fontsize,
                color=color,
                fill_opacity=opacity,
                stroke_opacity=opacity,
                rotate=0,
                morph=(pymupdf.Point(cx, cy), pymupdf.Matrix(angle)),
            )
            shape.commit(overlay=not behind)


def add_image_watermark(
    document, image_path: str, indices: list[int], *, opacity: float = 0.2, scale: float = 0.5,
    behind: bool = False
) -> None:
    with document.edit("Görüntü filigranı", structural=True) as doc:
        for pno in indices:
            page = doc[pno]
            r = page.rect
            w, h = r.width * scale, r.height * scale
            box = pymupdf.Rect(
                (r.width - w) / 2, (r.height - h) / 2, (r.width + w) / 2, (r.height + h) / 2
            )
            page.insert_image(box, filename=image_path, overlay=not behind, alpha=-1,
                              keep_proportion=True)


# --------------------------------------------------------------- sayfa numarası
def add_page_numbers(
    document,
    indices: list[int],
    *,
    fmt: str = "{n} / {total}",
    position: str = "alt-orta",
    fontsize: int = 10,
    color=(0, 0, 0),
    margin: float = 28.0,
    start_at: int = 1,
    fontname: str = "helv",
) -> None:
    total = document.page_count
    font = pymupdf.Font(fontname)
    with document.edit("Sayfa numarası ekle", structural=True) as doc:
        for i, pno in enumerate(indices):
            page = doc[pno]
            r = page.rect
            text = fmt.format(n=start_at + i, total=total, N=start_at + i, page=pno + 1)
            tw = font.text_length(text, fontsize)
            vert, horiz = position.split("-")
            y = margin if vert == "üst" else r.height - margin
            if horiz == "sol":
                x = margin
            elif horiz == "sağ":
                x = r.width - margin - tw
            else:
                x = (r.width - tw) / 2
            page.insert_text((x, y), text, fontname=fontname, fontsize=fontsize, color=color)


def add_header_footer(
    document, indices: list[int], *, header: str = "", footer: str = "", fontsize: int = 9,
    color=(0.2, 0.2, 0.2), margin: float = 24.0, fontname: str = "helv"
) -> None:
    font = pymupdf.Font(fontname)
    with document.edit("Üst/alt bilgi", structural=True) as doc:
        for pno in indices:
            page = doc[pno]
            r = page.rect
            for text, y in ((header, margin), (footer, r.height - margin)):
                if not text:
                    continue
                tw = font.text_length(text, fontsize)
                page.insert_text(((r.width - tw) / 2, y), text, fontname=fontname,
                                 fontsize=fontsize, color=color)
