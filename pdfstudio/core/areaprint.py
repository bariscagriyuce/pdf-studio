"""Sayfanın seçili bir alanını yazdırma / ayrı PDF olarak çıkarma.

Koordinat notu: Uygulama içinde alanlar PDF'in döndürülmemiş koordinatlarında
tutulur (metin ve açıklama API'leriyle aynı düzlem). PyMuPDF ise
``get_pixmap(clip=...)`` için ekranda görünen (döndürülmüş) düzlemi,
``show_pdf_page(clip=...)`` için döndürülmemiş düzlemi bekler. Döndürülmüş
sayfalarda bu ayrım gözetilmezse boş kâğıt basılır.
"""
from __future__ import annotations

import pymupdf

from ..i18n import _

FIT = "fit"          # kâğıda sığdır (büyüt/küçült)
ACTUAL = "actual"    # gerçek boyut (%100)
CUSTOM = "custom"    # özel ölçek


def display_rect(page: pymupdf.Page, rect) -> pymupdf.Rect:
    """Döndürülmemiş PDF dikdörtgenini ekranda görünen düzleme çevirir."""
    r = pymupdf.Rect(rect) * page.rotation_matrix
    r.normalize()
    return r & page.rect


def clamp_to_page(page: pymupdf.Page, rect) -> pymupdf.Rect:
    """Alanı sayfa sınırlarıyla (döndürülmemiş düzlemde) kırpar."""
    unrot = page.rect * page.derotation_matrix
    unrot.normalize()
    r = pymupdf.Rect(rect)
    r.normalize()
    return r & unrot


def area_size_pt(page: pymupdf.Page, rect) -> tuple[float, float]:
    """Alanın kâğıt üzerindeki (görünen) boyutu, nokta cinsinden."""
    r = display_rect(page, rect)
    return r.width, r.height


def render_area(page: pymupdf.Page, rect, dpi: float, *, alpha: bool = False,
                gray: bool = False) -> pymupdf.Pixmap:
    """Alanı ekranda göründüğü yönde, istenen çözünürlükte görüntüye çevirir."""
    clip = display_rect(page, rect)
    if clip.is_empty:
        raise ValueError(_("Seçili alan sayfanın dışında kalıyor"))
    return page.get_pixmap(
        dpi=int(dpi), clip=clip, alpha=alpha, annots=True,
        colorspace=pymupdf.csGRAY if gray else pymupdf.csRGB,
    )


def export_area_pdf(src_doc: pymupdf.Document, items: list[tuple[int, pymupdf.Rect]],
                    path: str, *, margin: float = 0.0) -> str:
    """Alanları vektör kalitesinde (metin seçilebilir kalır) yeni bir PDF'e yazar.

    ``items``: (sayfa_no, döndürülmemiş_dikdörtgen) listesi; her biri bir sayfa olur.
    """
    # show_pdf_page yalnızca sayfa içeriğini taşır; açıklamalar (vurgu, not,
    # çizim) ve form alanları ayrı nesnelerdir ve kaybolur. Ekranda görüneni
    # birebir almak için geçici bir kopyada onları içeriğe gömüyoruz.
    baked = pymupdf.open("pdf", src_doc.tobytes())
    try:
        baked.bake(annots=True, widgets=True)
    except Exception:
        pass
    src_doc = baked

    out = pymupdf.open()
    for pno, rect in items:
        page = src_doc[pno]
        clip = clamp_to_page(page, rect)
        if clip.is_empty:
            continue
        w, h = area_size_pt(page, clip)
        newpage = out.new_page(width=w + 2 * margin, height=h + 2 * margin)
        target = pymupdf.Rect(margin, margin, margin + w, margin + h)
        # show_pdf_page kaynağın dönüşünü uygulamaz; görünen yönü korumak için
        # sayfa dönüşünü tersine çevirerek veriyoruz.
        newpage.show_pdf_page(target, src_doc, pno, clip=clip,
                              rotate=-page.rotation % 360)
    baked.close()
    if out.page_count == 0:
        out.close()
        raise ValueError(_("Yazdırılacak geçerli bir alan yok"))
    out.save(path, garbage=4, deflate=True)
    out.close()
    return path


def placement(area_w: float, area_h: float, paper_w: float, paper_h: float, *,
              mode: str = FIT, scale: float = 1.0, center: bool = True,
              allow_upscale: bool = True) -> tuple[float, float, float, float]:
    """Alanın kâğıt üzerindeki konumunu hesaplar → (x, y, genişlik, yükseklik).

    Tüm değerler aynı birimde (nokta) verilir ve döner.
    """
    if area_w <= 0 or area_h <= 0:
        return 0.0, 0.0, 0.0, 0.0
    if mode == FIT:
        s = min(paper_w / area_w, paper_h / area_h)
        if not allow_upscale:
            s = min(s, 1.0)
    elif mode == CUSTOM:
        s = max(0.01, scale)
    else:
        s = 1.0
    w, h = area_w * s, area_h * s
    if center:
        x, y = (paper_w - w) / 2, (paper_h - h) / 2
    else:
        x, y = 0.0, 0.0
    return x, y, w, h
