"""Dışa aktarma: görüntü, metin, HTML, sıkıştırma ve OCR."""
from __future__ import annotations

import os
import shutil

import pymupdf

TEXT_MODES = {
    "Düz metin (.txt)": ("text", "txt"),
    "HTML (.html)": ("html", "html"),
    "XHTML (.xhtml)": ("xhtml", "xhtml"),
    "XML (.xml)": ("xml", "xml"),
    "JSON (.json)": ("json", "json"),
    "Markdown benzeri (.md)": ("text", "md"),
}

IMAGE_FORMATS = ["png", "jpg", "webp", "ppm", "pnm"]


def export_images(document, out_dir: str, *, pages: list[int] | None = None, dpi: int = 200,
                  fmt: str = "png", stem: str = "sayfa", alpha: bool = False,
                  gray: bool = False, progress=None) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    rng = list(pages if pages is not None else range(document.page_count))
    zoom = dpi / 72.0
    mat = pymupdf.Matrix(zoom, zoom)
    cs = pymupdf.csGRAY if gray else pymupdf.csRGB
    written = []
    for i, pno in enumerate(rng):
        page = document.page(pno)
        pm = page.get_pixmap(matrix=mat, alpha=alpha, colorspace=cs)
        ext = "jpg" if fmt == "jpg" else fmt
        path = os.path.join(out_dir, f"{stem}_{pno + 1:03d}.{ext}")
        if fmt == "jpg":
            pm.save(path, jpg_quality=92)
        else:
            pm.save(path)
        written.append(path)
        if progress:
            progress(i + 1, len(rng))
    return written


def export_text(document, path: str, *, mode: str = "text", pages: list[int] | None = None,
                separator: bool = True) -> str:
    rng = list(pages if pages is not None else range(document.page_count))
    if mode == "json":
        import json
        data = [{"page": p + 1, "content": document.page(p).get_text("dict")} for p in rng]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1, default=str)
        return path
    chunks = []
    for pno in rng:
        txt = document.page(pno).get_text(mode)
        if separator and mode in ("text",):
            chunks.append(f"\n----- Sayfa {pno + 1} -----\n{txt}")
        else:
            chunks.append(txt)
    body = "".join(chunks)
    if mode in ("html", "xhtml"):
        body = ("<!doctype html><html><head><meta charset='utf-8'>"
                f"<title>{os.path.basename(path)}</title></head><body>{body}</body></html>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def export_pdf_subset(document, path: str, pages: list[int]) -> str:
    out = pymupdf.open()
    for pno in pages:
        out.insert_pdf(document.doc, from_page=pno, to_page=pno)
    out.save(path, garbage=4, deflate=True)
    out.close()
    return path


def compress(document, path: str, *, image_dpi: int = 0, jpeg_quality: int = 70,
             subset_fonts: bool = True, clean: bool = True) -> tuple[int, int]:
    """Belgeyi küçültür. (önceki_boyut, yeni_boyut) döndürür."""
    before = len(document.export_bytes())
    doc = pymupdf.open("pdf", document.export_bytes())
    if image_dpi > 0:
        try:
            doc.rewrite_images(dpi_target=image_dpi, quality=jpeg_quality,
                               set_to_gray=False)
        except Exception:
            pass
    if subset_fonts:
        try:
            doc.subset_fonts(verbose=False)
        except Exception:
            pass
    doc.save(path, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True,
             clean=clean, linear=False)
    doc.close()
    return before, os.path.getsize(path)


# ------------------------------------------------------------------------- OCR
def tesseract_available() -> tuple[bool, str]:
    exe = shutil.which("tesseract")
    tessdata = os.environ.get("TESSDATA_PREFIX", "")
    if not exe:
        return False, "tesseract bulunamadı (Linux: 'tesseract' + 'tesseract-data-tur', Windows: Tesseract-OCR kurulumu)"
    if not tessdata:
        for cand in ("/usr/share/tessdata", "/usr/share/tesseract-ocr/5/tessdata",
                     "/usr/local/share/tessdata",
                     r"C:\Program Files\Tesseract-OCR\tessdata"):
            if os.path.isdir(cand):
                os.environ["TESSDATA_PREFIX"] = cand
                tessdata = cand
                break
    if not tessdata:
        return False, "TESSDATA_PREFIX ayarlanmamış"
    return True, tessdata


def available_languages() -> list[str]:
    """Kurulu Tesseract dil verilerini listeler."""
    ok, tessdata = tesseract_available()
    if not ok or not os.path.isdir(tessdata):
        return []
    langs = sorted(
        os.path.splitext(f)[0] for f in os.listdir(tessdata)
        if f.endswith(".traineddata")
    )
    return [l for l in langs if l != "osd"]


def check_languages(language: str) -> list[str]:
    """İstenen dillerden kurulu olmayanları döndürür."""
    have = set(available_languages()) | {"osd"}
    return [l for l in language.split("+") if l.strip() and l.strip() not in have]


def ocr_pages(document, pages: list[int] | None = None, *, language: str = "tur+eng",
              dpi: int = 300, progress=None) -> int:
    """Taranmış sayfalara aranabilir metin katmanı ekler."""
    ok, msg = tesseract_available()
    if not ok:
        raise RuntimeError(msg)
    missing = check_languages(language)
    if missing:
        have = ", ".join(available_languages()) or "(hiçbiri)"
        raise RuntimeError(
            f"Dil verisi eksik: {', '.join(missing)}.\nKurulu diller: {have}\n\n"
            "Linux: sudo pacman -S tesseract-data-tur tesseract-data-eng\n"
            "  (Debian/Ubuntu: sudo apt install tesseract-ocr-tur tesseract-ocr-eng)\n"
            "Windows: Tesseract kurulumunda ilgili dil paketlerini seçin.")
    rng = list(pages if pages is not None else range(document.page_count))
    done = 0
    with document.edit("OCR uygula", structural=True) as doc:
        src = pymupdf.open("pdf", doc.tobytes())
        for i, pno in enumerate(rng):
            page = src[pno]
            pm = page.get_pixmap(matrix=pymupdf.Matrix(dpi / 72, dpi / 72), alpha=False)
            pdfbytes = pm.pdfocr_tobytes(language=language, tessdata=os.environ["TESSDATA_PREFIX"])
            ocr = pymupdf.open("pdf", pdfbytes)
            target = doc[pno]
            target.show_pdf_page(target.rect, ocr, 0, overlay=False)
            ocr.close()
            done += 1
            if progress:
                progress(i + 1, len(rng))
        src.close()
    return done


def ocr_page_text(document, pno: int, *, language: str = "tur+eng", dpi: int = 300) -> str:
    ok, msg = tesseract_available()
    if not ok:
        raise RuntimeError(msg)
    missing = check_languages(language)
    if missing:
        raise RuntimeError(f"Dil verisi eksik: {', '.join(missing)}")
    page = document.page(pno)
    tp = page.get_textpage_ocr(language=language, dpi=dpi, full=True,
                               tessdata=os.environ["TESSDATA_PREFIX"])
    return page.get_text(textpage=tp)
