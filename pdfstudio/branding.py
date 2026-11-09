"""Uygulama adı ve kimlikleri — tek kaynak.

Görünen ad sistem diline göre seçilir. Teknik kimlikler (çalıştırılabilir adı,
komut, paket adı, ayar klasörleri) bilerek değiştirilmez: değişirlerse önceki
sürümün üzerine güncelleme yerine ikinci bir kopya kurulur ve kullanıcının
ayarları kaybolur.
"""
from __future__ import annotations

import os

APP_NAME_TR = "YUCE PDF Düzenleyici"
APP_NAME_EN = "YUCE PDF EDITOR"
PUBLISHER = "YUCE"

# Dağıtılan dosyaların adı: YUCE-PDF-Editor-1.2.3-Setup.exe vb.
FILE_STEM = "YUCE-PDF-Editor"

# --- değişmeyen teknik kimlikler -------------------------------------------
EXE_NAME = "PDFStudio"          # PDFStudio.exe / PDFStudio
APP_ID = "pdf-studio"           # komut, .desktop, pacman paketi, /opt dizini
SETTINGS_ORG = "PDFStudio"      # QSettings ve önbellek klasörleri


def system_language() -> str:
    """'tr', 'en' gibi iki harfli dil kodu. PDFSTUDIO_LANG ile zorlanabilir."""
    forced = os.environ.get("PDFSTUDIO_LANG", "").strip().lower()
    if forced:
        return forced[:2]
    try:
        from PySide6.QtCore import QLocale
        return QLocale.system().name()[:2].lower()
    except Exception:
        import locale
        name = (locale.getlocale()[0] or os.environ.get("LANG", "")).lower()
        return name[:2]


def app_name(lang: str | None = None) -> str:
    """Türkçe sistemde 'YUCE PDF Düzenleyici', diğerlerinde 'YUCE PDF EDITOR'."""
    return APP_NAME_TR if (lang or system_language()).startswith("tr") else APP_NAME_EN
