"""Şifreleme, izinler ve belge temizliği."""
from __future__ import annotations

import pymupdf

PERMISSIONS = [
    ("print", pymupdf.PDF_PERM_PRINT, "Yazdırma"),
    ("modify", pymupdf.PDF_PERM_MODIFY, "İçeriği değiştirme"),
    ("copy", pymupdf.PDF_PERM_COPY, "Metin/görüntü kopyalama"),
    ("annotate", pymupdf.PDF_PERM_ANNOTATE, "Açıklama ekleme"),
    ("form", pymupdf.PDF_PERM_FORM, "Form doldurma"),
    ("accessibility", pymupdf.PDF_PERM_ACCESSIBILITY, "Erişilebilirlik için çıkarma"),
    ("assemble", pymupdf.PDF_PERM_ASSEMBLE, "Sayfa düzenleme (birleştir/böl)"),
    ("print_hq", pymupdf.PDF_PERM_PRINT_HQ, "Yüksek çözünürlüklü yazdırma"),
]

METHODS = {
    "AES-256 (en güçlü)": pymupdf.PDF_ENCRYPT_AES_256,
    "AES-128": pymupdf.PDF_ENCRYPT_AES_128,
    "RC4-128 (eski)": pymupdf.PDF_ENCRYPT_RC4_128,
    "Şifreleme yok": pymupdf.PDF_ENCRYPT_NONE,
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
    with document.edit("Belgeyi temizle", structural=True) as doc:
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
        total_annots += sum(1 for _ in page.annots())
        total_images += len(page.get_images(full=True))
        total_words += len(page.get_text("words"))
    return {
        "Dosya": document.path or "(kaydedilmedi)",
        "Sayfa sayısı": document.page_count,
        "PDF sürümü": meta.get("format", "?"),
        "Başlık": meta.get("title", ""),
        "Yazar": meta.get("author", ""),
        "Konu": meta.get("subject", ""),
        "Anahtar kelimeler": meta.get("keywords", ""),
        "Üretici": meta.get("producer", ""),
        "Oluşturan": meta.get("creator", ""),
        "Oluşturma": meta.get("creationDate", ""),
        "Değiştirme": meta.get("modDate", ""),
        "Şifreli": "Evet" if document.is_encrypted() else "Hayır",
        "Form içeriyor": "Evet" if doc.is_form_pdf else "Hayır",
        "Açıklama sayısı": total_annots,
        "Görüntü sayısı": total_images,
        "Kelime sayısı": total_words,
        "Yer imi sayısı": len(document.toc()),
    }
