"""Uygulama adı ve kimlikleri — tek kaynak.

Görünen ad seçili arayüz diline göre belirlenir. Teknik kimlikler (çalıştırılabilir adı,
komut, paket adı, ayar klasörleri) bilerek değiştirilmez: değişirlerse önceki
sürümün üzerine güncelleme yerine ikinci bir kopya kurulur ve kullanıcının
ayarları kaybolur.
"""
from __future__ import annotations

APP_NAME_TR = "YUCE PDF Düzenleyici"
APP_NAME_EN = "YUCE PDF EDITOR"
PUBLISHER = "YUCE"

# Dağıtılan dosyaların adı: YUCE-PDF-Editor-1.2.3-Setup.exe vb.
FILE_STEM = "YUCE-PDF-Editor"

# --- değişmeyen teknik kimlikler -------------------------------------------
EXE_NAME = "PDFStudio"          # PDFStudio.exe / PDFStudio
APP_ID = "pdf-studio"           # komut, .desktop, pacman paketi, /opt dizini
SETTINGS_ORG = "PDFStudio"      # QSettings ve önbellek klasörleri

# Güncellemelerin denetlendiği GitHub deposu (Releases)
GITHUB_REPO = "bariscagriyuce/pdf-studio"


def app_name(lang: str | None = None) -> str:
    """Türkçe arayüzde 'YUCE PDF Düzenleyici', diğer dillerde 'YUCE PDF EDITOR'.

    Varsayılan olarak seçili arayüz dilini izler (Görünüm → Dil).
    """
    if lang is None:
        from . import i18n
        lang = i18n.current()
    return APP_NAME_TR if lang.startswith("tr") else APP_NAME_EN
