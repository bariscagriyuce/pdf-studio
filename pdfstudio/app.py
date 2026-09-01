"""Uygulama başlangıcı."""
from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication

from .ui import icons
from .ui.mainwindow import APP_NAME, MainWindow


def app_icon() -> QIcon:
    here = os.path.dirname(os.path.abspath(__file__))
    png = os.path.join(here, "resources", "icon.png")
    if os.path.exists(png):
        return QIcon(QPixmap(png))
    ic = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        ic.addPixmap(icons.pixmap("reader", size, "#4f8cff", width=1.4, dpr=1.0))
    return ic


USAGE = """PDF Studio — ayrıntılı PDF düzenleyici

Kullanım:
  PDFStudio [dosya.pdf]      Belgeyi açar (dosya verilmezse boş başlar)
  PDFStudio --self-test      Kurulumu doğrular ve çıkar (CI / kurulum sonrası)
      [--log YOL]            Sınama çıktısını dosyaya da yazar
      [--screenshot YOL]     Ekran görüntüsü kaydeder
  PDFStudio --version        Sürümü yazar
  PDFStudio --help           Bu yardımı gösterir
"""


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv)

    if "--help" in argv or "-h" in argv:
        print(USAGE)
        return 0
    if "--version" in argv:
        from . import __version__
        print(f"PDF Studio {__version__}")
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

    app = QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName("PDFStudio")
    app.setWindowIcon(app_icon())

    # Yazı tipi taraması ilk açılışta uzun sürebilir; arka planda hazırlanır.
    win = MainWindow()
    win.show()

    from .core.fonts import FontManager
    FontManager.instance()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
