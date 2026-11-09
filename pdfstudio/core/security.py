"""Şifreleme, izinler ve belge temizliği."""
from __future__ import annotations

import pymupdf

from ..i18n import N_, _

PERMISSIONS = [
    ("print", pymupdf.PDF_PERM_PRINT, N_("Yazdırma")),
    ("modify", pymupdf.PDF_PERM_MODIFY, N_("İçeriği değiştirme")),
    ("copy", pymupdf.PDF_PERM_COPY, N_("Metin/görüntü kopyalama")),
    ("annotate", pymupdf.PDF_PERM_ANNOTATE, N_("Açıklama ekleme")),
    ("form", pymupdf.PDF_PERM_FORM, N_("Form doldurma")),
    ("accessibility", pymupdf.PDF_PERM_ACCESSIBILITY, N_("Erişilebilirlik için çıkarma")),
    ("assemble", pymupdf.PDF_PERM_ASSEMBLE, N_("Sayfa düzenleme (birleştir/böl)")),
    ("print_hq", pymupdf.PDF_PERM_PRINT_HQ, N_("Yüksek çözünürlüklü yazdırma")),
]

METHODS = {
    N_("AES-256 (en güçlü)"): pymupdf.PDF_ENCRYPT_AES_256,
    N_("AES-128"): pymupdf.PDF_ENCRYPT_AES_128,
    N_("RC4-128 (eski)"): pymupdf.PDF_ENCRYPT_RC4_128,
    N_("Şifreleme yok"): pymupdf.PDF_ENCRYPT_NONE,
}


def permission_flags(selected: set[str]) -> int:
    value = 0
    for key, flag, _label in PERMISSIONS:
        if key in selected:
            value |= flag
    return value


def current_permissions(document) -> set[str]:
    perms = document.permissions
    return {key for key, flag, _l in PERMISSIONS if perms & flag}


def save_encrypted(document, path: str, *, user_pw: str = "", owner_pw: str = "",
                   allowed: set[str] | None = None,
                   method=pymupdf.PDF_ENCRYPT_AES_256) -> str:
    perm = permission_flags(allowed if allowed is not None else {k for k, _f, _l in PERMISSIONS})
    return document.save(
        path, encryption=method, owner_pw=owner_pw or user_pw,
        user_pw=user_pw, permissions=perm, incremental=False,
    )


def save_decrypted(document, path: str) -> str:
    return document.save(path, encryption=pymupdf.PDF_ENCRYPT_NONE, incremental=False)


def sanitize(document, *, remove_metadata: bool = True, remove_js: bool = True,
             remove_attachments: bool = False, remove_links: bool = False) -> None:
    """Gizlilik temizliği: meta veri, JavaScript, ekler ve bağlantılar."""
    with document.edit(_("Belgeyi temizle"), structural=True) as doc:
        if remove_metadata:
            doc.set_metadata({})
            try:
                doc.del_xml_metadata()
            except Exception:
                pass
        if remove_js:
            try:
                for xref in range(1, doc.xref_length()):
                    if doc.xref_get_key(xref, "JS")[0] != "null":
                        doc.xref_set_key(xref, "JS", "null")
                    if doc.xref_get_key(xref, "AA")[0] != "null":
                        doc.xref_set_key(xref, "AA", "null")
                    if doc.xref_get_key(xref, "OpenAction")[0] != "null":
                        doc.xref_set_key(xref, "OpenAction", "null")
            except Exception:
                pass
        if remove_attachments:
            try:
                for name in list(doc.embfile_names()):
                    doc.embfile_del(name)
            except Exception:
                pass
            for pno in range(doc.page_count):
                page = doc[pno]
                for a in list(page.annots(types=[pymupdf.PDF_ANNOT_FILE_ATTACHMENT])):
                    page.delete_annot(a)
        if remove_links:
            for pno in range(doc.page_count):
                page = doc[pno]
                for link in page.get_links():
                    page.delete_link(link)


def document_report(document) -> dict:
    doc = document.doc
    meta = document.metadata()
    total_annots = 0
    total_images = 0
    total_words = 0
    for pno in range(document.page_count):
        page = doc[pno]
        total_annots += sum(1 for _x in page.annots())
        total_images += len(page.get_images(full=True))
        total_words += len(page.get_text("words"))
    return {
        N_("Dosya"): document.path or _("(kaydedilmedi)"),
        N_("Sayfa sayısı"): document.page_count,
        N_("PDF sürümü"): meta.get("format", "?"),
        N_("Başlık"): meta.get("title", ""),
        N_("Yazar"): meta.get("author", ""),
        N_("Konu"): meta.get("subject", ""),
        N_("Anahtar kelimeler"): meta.get("keywords", ""),
        N_("Üretici"): meta.get("producer", ""),
        N_("Oluşturan"): meta.get("creator", ""),
        N_("Oluşturma"): meta.get("creationDate", ""),
        N_("Değiştirme"): meta.get("modDate", ""),
        N_("Şifreli"): _("Evet") if document.is_encrypted() else _("Hayır"),
        N_("Form içeriyor"): _("Evet") if doc.is_form_pdf else _("Hayır"),
        N_("Açıklama sayısı"): total_annots,
        N_("Görüntü sayısı"): total_images,
        N_("Kelime sayısı"): total_words,
        N_("Yer imi sayısı"): len(document.toc()),
    }
