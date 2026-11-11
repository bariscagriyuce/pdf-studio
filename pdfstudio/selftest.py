"""Paketlenmiş yapıları doğrulamak için gömülü sınama (`PDFStudio --self-test`).

Gerçek bir belge oluşturur, çekirdek düzenleme yollarını çalıştırır ve sonucu
raporlar. CI ve kurulum sonrası doğrulama için kullanılır.
"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback


def run(screenshot: str | None = None, log_path: str | None = None) -> int:
    """Sınamayı çalıştırır. `log_path` verilirse çıktı dosyaya da yazılır
    (Windows'ta konsolsuz yapıların çıktısını görebilmek için)."""
    if not sys.platform.startswith("win"):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    lines: list[str] = []

    def out(text=""):
        lines.append(str(text))
        try:
            print(text, flush=True)
        except Exception:
            pass  # konsolsuz Windows yapısında stdout yok

    import pymupdf
    from PySide6.QtWidgets import QApplication

    failures: list[tuple[str, str]] = []

    def expect(condition, message):
        if not condition:
            raise AssertionError(message)

    def check(name, fn):
        try:
            fn()
            out(f"  ✔ {name}")
        except Exception as exc:
            failures.append((name, traceback.format_exc()))
            out(f"  ✘ {name}: {exc}")

    from .branding import app_name
    out(f"{app_name()} kendi kendini sınama")
    out(f"  Python   : {sys.version.split()[0]}")
    out(f"  PyMuPDF  : {pymupdf.__version__}")
    import PySide6
    out(f"  PySide6  : {PySide6.__version__}")
    out(f"  Platform : {sys.platform}")
    out(f"  Dondurulmuş: {getattr(sys, 'frozen', False)}")
    out()

    app = QApplication.instance() or QApplication([])

    from .core import annots as an
    from .core import exporting, forms, images as im, pageops, security
    from .core import textedit as te
    from .core.fonts import FontManager
    from .ui.mainwindow import MainWindow
    from .ui.tools import Tool

    tmp = tempfile.mkdtemp(prefix="pdfstudio-selftest-")
    src = os.path.join(tmp, "kaynak.pdf")

    # --- örnek belge üret (Türkçe karakterler dahil)
    fm = FontManager.instance()
    ttf = fm.path_for("DejaVu Sans") or fm.path_for("Noto Sans") or fm.path_for("Arial")
    doc = pymupdf.open()
    for i in range(3):
        page = doc.new_page(width=595, height=842)
        kw = dict(fontname="F0", fontfile=ttf) if ttf else dict(fontname="helv")
        page.insert_text((60, 90), f"Bölüm {i + 1} — Türkçe Başlık ığşçöü", fontsize=20, **kw)
        for k in range(12):
            page.insert_text((60, 140 + k * 20), f"{k + 1}. satır Lorem ipsum dolor.",
                             fontsize=11, **kw)
    doc.set_toc([[1, "Giriş", 1], [1, "Son", 3]])
    doc.save(src)
    doc.close()

    win = MainWindow()
    win.resize(1280, 860)
    win.show()
    app.processEvents()

    check("belge aç", lambda: win.open_path(src))
    check("sayfa sayısı", lambda: expect(win.document.page_count == 3,
                                        f"3 bekleniyordu, {win.document.page_count} bulundu"))
    check("sayfa görüntüleme", lambda: win.view.renderer.image(0, 1.0))
    check("küçük resim", lambda: win.view.renderer.thumbnail(0))
    check("yazı tipi taraması", lambda: expect(bool(fm.families()),
                                              "sistemde yazı tipi bulunamadı"))

    blocks = win.view.blocks_for(0)
    check("metin bloğu tespiti", lambda: expect(bool(blocks), "metin bloğu bulunamadı"))

    if blocks:
        blk = blocks[0]
        check("metni düzenle (Türkçe)", lambda: te.replace_region_text(
            win.document, 0, blk.bbox, "DÜZENLENDİ ığşçöü İĞŞÇÖÜ", blk.style))
        check("düzenleme doğrulama",
              lambda: expect("DÜZENLENDİ" in win.document.page(0).get_text(),
                             "yeni metin sayfaya yazılmadı"))
        check("geri al", win.edit_undo)
        check("yinele", win.edit_redo)

    check("ara", lambda: win.do_search("Lorem", False, False))
    check("bul-değiştir", lambda: te.replace_all(win.document, "Lorem", "LOREM"))
    check("vurgu", lambda: an.add_markup(
        win.document, 0, "highlight", win.document.page(0).search_for("ipsum")[:3]))
    check("serbest çizim", lambda: an.add_ink(
        win.document, 0, [[(60, 600), (150, 650), (240, 610)]]))
    check("şekil", lambda: an.add_shape(win.document, 0, "rect", (300, 600), (450, 700)))
    check("not", lambda: an.add_sticky_note(win.document, 0, (500, 100), "not"))
    check("metin seçimi", lambda: te.selection_quads(
        win.document.page(1), (60, 145), (400, 148)))
    check("sayfa döndür", lambda: pageops.rotate_pages(win.document, [0], 90))
    check("sayfa döndür (geri)", lambda: pageops.rotate_pages(win.document, [0], -90))
    check("sayfa ekle", lambda: pageops.insert_blank(win.document, 1, 595, 842))
    check("sayfa sil", lambda: pageops.delete_pages(win.document, [1]))
    check("filigran", lambda: pageops.add_text_watermark(
        win.document, "TASLAK", [0], fontsize=48))
    check("sayfa numarası", lambda: pageops.add_page_numbers(win.document, [0, 1, 2]))
    check("form alanı", lambda: forms.add_field(
        win.document, 0, pymupdf.Rect(60, 720, 300, 745), name="ad"))
    check("form doldur", lambda: forms.set_values(win.document, {"ad": "Test"}))
    check("karartma", lambda: te.redact_areas(
        win.document, [(1, pymupdf.Rect(60, 140, 400, 190))]))
    check("gömülü görüntü listesi", lambda: im.list_images(win.document, 0))
    check("PNG dışa aktar", lambda: exporting.export_images(
        win.document, os.path.join(tmp, "png"), pages=[0], dpi=72))
    check("metin dışa aktar", lambda: exporting.export_text(
        win.document, os.path.join(tmp, "cikti.txt")))
    check("HTML dışa aktar", lambda: exporting.export_text(
        win.document, os.path.join(tmp, "cikti.html"), mode="html"))
    check("sıkıştır", lambda: exporting.compress(win.document, os.path.join(tmp, "k.pdf")))
    check("şifreli kaydet", lambda: security.save_encrypted(
        win.document, os.path.join(tmp, "gizli.pdf"), user_pw="1234"))
    check("belge raporu", lambda: security.document_report(win.document))
    check("kaydet", lambda: win.document.save(os.path.join(tmp, "sonuc.pdf")))
    check("yeniden aç", lambda: win.open_path(os.path.join(tmp, "sonuc.pdf")))
    check("araçlar", lambda: [win.set_tool(t) for t in Tool
                              if t not in (Tool.IMAGE, Tool.SIGNATURE)])
    check("tema değiştir", lambda: (win.toggle_theme(), win.toggle_theme()))
    check("yazdırma altyapısı", lambda: __import__(
        "PySide6.QtPrintSupport", fromlist=["QPrinter"]).QPrinter())

    def _i18n():
        from . import i18n
        before = i18n.current()
        try:
            for code, word in (("en", "Save"), ("pt_BR", "Salvar"), ("tr", "Kaydet")):
                i18n.set_language(code)
                expect(i18n._("Kaydet") == word, f"{code}: {i18n._('Kaydet')!r}")
            i18n.set_language("en")
            expect(i18n._n("{0} sonuç", 1).format(1) == "1 result", "en tekil")
            expect(i18n._n("{0} sonuç", 3).format(3) == "3 results", "en çoğul")
        finally:
            i18n.set_language(before)
    check("çeviri katalogları (tr/en/pt_BR)", _i18n)

    def _qt_translations():
        # Qt'nin kendi pencereleri (Evet/Hayır, dosya seçici) için .qm dosyaları
        # pakette bulunmalı; yoksa bu pencereler İngilizce kalır.
        from . import i18n
        before = i18n.current()
        try:
            for code in ("tr", "pt_BR"):
                i18n.set_language(code)
                loaded = i18n.install_qt_translators(app)
                for t in loaded:
                    app.removeTranslator(t)
                expect(loaded, f"{code} için Qt çevirisi bulunamadı")
        finally:
            i18n.set_language(before)
    check("Qt çevirileri (tr/pt_BR)", _qt_translations)

    from .core import areaprint as ap
    area = pymupdf.Rect(55, 65, 420, 100)
    check("alanı görüntüye çevir", lambda: expect(
        ap.render_area(win.document.page(0), area, 72).width > 50, "boş görüntü"))

    def _area_pdf():
        out = os.path.join(tmp, "alan.pdf")
        ap.export_area_pdf(win.document.doc, [(0, area)], out)
        with pymupdf.open(out) as d:
            expect(d.page_count == 1 and d[0].get_text().strip(), "alan PDF'i boş")
    check("alanı PDF olarak kaydet", _area_pdf)

    def _area_print():
        from PySide6.QtPrintSupport import QPrinter
        pr = QPrinter(QPrinter.HighResolution)
        pr.setOutputFormat(QPrinter.PdfFormat)
        pr.setOutputFileName(os.path.join(tmp, "alan_baski.pdf"))
        n = win._print_area_render(pr, [(0, area), (1, area)],
                                   {"mode": ap.FIT, "marks": True})
        expect(n == 2, f"2 kâğıt bekleniyordu, {n} basıldı")
    check("seçili alanı yazdır", _area_print)

    def _nup_print():
        from PySide6.QtPrintSupport import QPrinter
        from .core import nup
        pr = QPrinter(QPrinter.HighResolution)
        pr.setOutputFormat(QPrinter.PdfFormat)
        pr.setOutputFileName(os.path.join(tmp, "nup_baski.pdf"))
        total = win.document.page_count
        opts = nup.NupOptions(rows=1, cols=2, gap_mm=2, border=True)
        n = win._print_render(pr, opts)
        want = (total + 1) // 2
        expect(n == want, f"{want} kâğıt bekleniyordu, {n} basıldı")
        expect(nup.cell_position(1, 2, 3, nup.TBLR) == (1, 0), "sayfa sırası yanlış")
    check("kâğıt başına birden çok sayfa yazdır", _nup_print)

    ok, msg = exporting.tesseract_available()
    langs = exporting.available_languages() if ok else []
    out(f"  · OCR: {'var — ' + ', '.join(langs) if langs else 'yok (' + msg + ')'}")
    out(f"  · Yazı tipi ailesi: {len(fm.families())}")

    if screenshot:
        win.view.fit("width")
        for _ in range(30):
            app.processEvents()
        win.grab().save(screenshot)
        out(f"  · Ekran görüntüsü: {screenshot}")

    out()
    if failures:
        out(f"SONUÇ: {len(failures)} HATA")
        for name, tb in failures:
            out(f"--- {name}\n{tb}")
        _write_log(log_path, lines)
        return 1
    out("SONUÇ: TÜM SINAMALAR BAŞARILI ✔")
    _write_log(log_path, lines)
    return 0


def _write_log(path: str | None, lines: list[str]) -> None:
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    except Exception:
        pass
