# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller yapılandırması — Linux ve Windows için ortak.

Kullanım:
    pyinstaller --noconfirm --clean packaging/pdfstudio.spec
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(SPEC)), ".."))
WINDOWS = sys.platform.startswith("win")

# PDFSTUDIO_ONEFILE=1 → tek dosyalık taşınabilir çıktı; aksi hâlde klasör dağıtımı
ONEFILE = os.environ.get("PDFSTUDIO_ONEFILE", "") == "1"
APP_NAME = os.environ.get("PDFSTUDIO_NAME", "PDFStudio")

_version_file = os.path.join(ROOT, "packaging", "version_info.txt")
VERSION_FILE = _version_file if (WINDOWS and os.path.exists(_version_file)) else None
ICON_FILE = os.path.join(ROOT, "pdfstudio", "resources",
                         "icon.ico" if WINDOWS else "icon.png")

# Uygulamanın kullanmadığı Qt modülleri — paket boyutunu ciddi biçimde düşürür
EXCLUDES = [
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
    "PySide6.QtQuick", "PySide6.QtQuick3D", "PySide6.QtQuickWidgets", "PySide6.QtQml",
    "PySide6.Qt3DCore", "PySide6.QtCharts", "PySide6.QtDataVisualization",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets", "PySide6.QtSql",
    "PySide6.QtTest", "PySide6.QtBluetooth", "PySide6.QtNfc", "PySide6.QtPositioning",
    "PySide6.QtSerialPort", "PySide6.QtSensors", "PySide6.QtWebSockets",
    "PySide6.QtWebChannel", "PySide6.QtDesigner", "PySide6.QtUiTools", "PySide6.QtHelp",
    "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtSpatialAudio",
    "PySide6.QtTextToSpeech", "PySide6.QtStateMachine", "PySide6.QtRemoteObjects",
    "PySide6.QtScxml", "PySide6.QtHttpServer",
    "matplotlib", "numpy", "PIL", "tkinter", "scipy", "pandas", "pytest",
    "setuptools", "pip", "wheel", "IPython", "notebook", "pydoc_data",
]

# Yalnızca Linux'ta: GTK3 platform teması ~20 MB bağımlılık getiriyor, gerekli değil
DROP_PATTERNS = [
    "platformthemes/libqgtk3", "libgtk-3", "libgdk-3", "libglycin",
    "libgdk_pixbuf", "libx265", "libaom", "libSvtAv1Enc", "libjxl",
    "libKF6BreezeIcons", "libheif", "libde265", "librav1e",
    "imageformats/libqicns", "imageformats/libqtga", "imageformats/libqwbmp",
]


def keep(entry):
    name = entry[0].replace("\\", "/")
    return not any(pat in name for pat in DROP_PATTERNS)


a = Analysis(
    [os.path.join(ROOT, "launcher.py")],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join(ROOT, "pdfstudio", "resources", "icon.png"), "pdfstudio/resources"),
        (os.path.join(ROOT, "pdfstudio", "resources", "icon.ico"), "pdfstudio/resources"),
    ],
    hiddenimports=["pymupdf", "PySide6.QtSvg", "PySide6.QtPrintSupport"],
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False, optimize=2,
)

if not WINDOWS:
    a.binaries = [b for b in a.binaries if keep(b)]
    a.datas = [d for d in a.datas if keep(d)]

pyz = PYZ(a.pure)

if ONEFILE:
    exe = EXE(
        pyz, a.scripts, a.binaries, a.datas, [],
        name=APP_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        icon=ICON_FILE,
        version=VERSION_FILE,
    )
else:
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name=APP_NAME,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=False,
        disable_windowed_traceback=False,
        icon=ICON_FILE,
        version=VERSION_FILE,
    )
    coll = COLLECT(
        exe, a.binaries, a.datas,
        strip=False, upx=False, name=APP_NAME,
    )
