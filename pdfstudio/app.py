"""Uygulama başlangıcı."""
from __future__ import annotations

import os
import sys

from PySide6.QtCore import QEvent, QLocale, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication

from . import i18n
from .i18n import _
from .ui import icons


def app_icon() -> QIcon:
    here = os.path.dirname(os.path.abspath(__file__))
    png = os.path.join(here, "resources", "icon.png")
    if os.path.exists(png):
        return QIcon(QPixmap(png))
    ic = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        ic.addPixmap(icons.pixmap("reader", size, "#4f8cff", width=1.4, dpr=1.0))
    return ic


class Application(QApplication):
    """macOS'ta Finder'dan "Birlikte Aç" / çift tıklama / Dock'a sürükleme,
    dosyayı komut satırıyla değil QFileOpenEvent ile iletir. Pencere henüz
    hazır değilse yol saklanır ve pencere açılınca yüklenir."""

    def __init__(self, argv):
        super().__init__(argv)
        self.window = None
        self.pending_files: list[str] = []

    def event(self, ev):
        if ev.type() == QEvent.FileOpen:
            path = ev.file()
            if path and path.lower().endswith(".pdf"):
                if self.window is not None:
                    self.window.open_path(path)
                else:
                    self.pending_files.append(path)
            return True
        return super().event(ev)


def usage() -> str:
    from .branding import APP_NAME_EN, APP_NAME_TR
    return _("""{tr} ({en}) — ayrıntılı PDF düzenleyici

Kullanım:
  PDFStudio [dosya.pdf]      Belgeyi açar (dosya verilmezse boş başlar)
  PDFStudio --self-test      Kurulumu doğrular ve çıkar (CI / kurulum sonrası)
      [--log YOL]            Sınama çıktısını dosyaya da yazar
      [--screenshot YOL]     Ekran görüntüsü kaydeder
  PDFStudio --version        Sürümü yazar
  PDFStudio --help           Bu yardımı gösterir

Dil, uygulamada Görünüm → Dil menüsünden ya da PDFSTUDIO_LANG ortam
değişkeniyle (tr, en, pt_BR) seçilir.
""").format(tr=APP_NAME_TR, en=APP_NAME_EN)


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv)

    # Dil, arayüz modülleri içe aktarılmadan ÖNCE kurulmalı: bazı değerler
    # (ör. pencere başlığındaki uygulama adı) içe aktarma anında hesaplanır.
    i18n.init()

    if "--help" in argv or "-h" in argv:
        print(usage())
        return 0
    if "--version" in argv:
        from . import __version__
        from .branding import app_name
        print(f"{app_name()} {__version__}")
        return 0
    if "--self-test" in argv:
        from .selftest import run

        def opt(flag):
            if flag in argv:
                i = argv.index(flag)
                if i + 1 < len(argv):
                    return argv[i + 1]
            return None

        return run(opt("--screenshot"), opt("--log"))

    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    from .branding import APP_ID, EXE_NAME, SETTINGS_ORG
    from .ui.mainwindow import APP_NAME, MainWindow

    app = Application(argv)
    # Sayı/tarih biçimi arayüz diliyle tutarlı olsun (2.00 / 2,00)
    QLocale.setDefault(QLocale(i18n.current()))
    # Qt'nin kendi pencereleri (Evet/Hayır, dosya/renk seçici, baskı önizleme)
    app._translators = i18n.install_qt_translators(app)
    # Teknik ad sabit kalır: X11'de WM_CLASS olur ve .desktop dosyasındaki
    # StartupWMClass ile eşleşmesi gerekir (görev çubuğu ikonu/gruplama).
    app.setApplicationName(EXE_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName(SETTINGS_ORG)
    # Wayland'de pencereyi .desktop girdisine (ad + ikon) bağlar
    app.setDesktopFileName(APP_ID)
    app.setWindowIcon(app_icon())

    # Yazı tipi taraması ilk açılışta uzun sürebilir; arka planda hazırlanır.
    win = MainWindow()
    win.show()
    app.window = win
    if app.pending_files:
        # Finder'dan gelen dosya, komut satırındaki dosyanın önüne geçer
        sys.argv = [sys.argv[0], app.pending_files[-1]]

    from .core.fonts import FontManager
    FontManager.instance()

    # Yeni sürüm denetimi: açılışı yavaşlatmasın diye biraz sonra, arka planda
    QTimer.singleShot(5000, win.updater.check_on_startup)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
