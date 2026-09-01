#!/usr/bin/env python3
"""Kurulum dosyası üretir (çalıştığınız platform için).

    python build.py              # klasör dağıtımı + Linux'ta .run kurulumu
    python build.py --onefile    # taşınabilir tek dosya
    python build.py --no-installer

Windows kurulum sihirbazı için ayrıca Inno Setup 6 gerekir:
    iscc packaging\\pdfstudio.iss
Ayrıntı: packaging/README.md
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(ROOT, "packaging", "pdfstudio.spec")


def _version() -> str:
    """Sürüm tek yerde tanımlı: pdfstudio/__init__.py"""
    import re
    with open(os.path.join(ROOT, "pdfstudio", "__init__.py"), encoding="utf-8") as fh:
        m = re.search(r'__version__\s*=\s*"([^"]+)"', fh.read())
    return m.group(1) if m else "1.0.0"


VERSION = _version()
WINDOWS = sys.platform.startswith("win")


def ensure(module: str, package: str | None = None) -> None:
    try:
        __import__(module)
    except ImportError:
        print(f"{package or module} kuruluyor…")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package or module])


def main() -> int:
    onefile = "--onefile" in sys.argv
    make_installer = "--no-installer" not in sys.argv and not onefile

    ensure("PyInstaller", "pyinstaller")
    ensure("PySide6", "PySide6-Essentials")
    ensure("pymupdf", "PyMuPDF")

    env = dict(os.environ)
    dist = os.path.join(ROOT, "dist-onefile" if onefile else "dist")
    if onefile:
        env["PDFSTUDIO_ONEFILE"] = "1"

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
           "--distpath", dist, SPEC]
    print(" ".join(cmd))
    rc = subprocess.call(cmd, cwd=ROOT, env=env)
    if rc != 0:
        return rc

    exe = os.path.join(dist, "PDFStudio" + (".exe" if WINDOWS else ""))
    if not onefile:
        exe = os.path.join(dist, "PDFStudio", "PDFStudio" + (".exe" if WINDOWS else ""))
    if not WINDOWS and os.path.exists(exe):
        os.chmod(exe, 0o755)

    print("\n→ Kendi kendini sınama çalıştırılıyor…")
    log = os.path.join(ROOT, "selftest.log")
    rc = subprocess.call([exe, "--self-test", "--log", log])
    if rc != 0:
        print("✖ Sınama BAŞARISIZ — ayrıntı:", log)
        return rc
    print("✔ Sınama başarılı")

    if make_installer and not WINDOWS:
        out = os.path.join(ROOT, f"PDFStudio-{VERSION}-x86_64.run")
        rc = subprocess.call(
            ["bash", os.path.join(ROOT, "packaging", "make_linux_installer.sh"),
             os.path.join(dist, "PDFStudio"), out, VERSION], cwd=ROOT)
        if rc == 0:
            print(f"\n✔ Kurulum dosyası hazır: {out}")
            print(f"  Kurmak için:  bash {os.path.basename(out)}")
        return rc

    if make_installer and WINDOWS:
        iscc = shutil.which("iscc") or \
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
        if os.path.exists(iscc):
            rc = subprocess.call([iscc, f"/DAppVersion={VERSION}",
                                  os.path.join(ROOT, "packaging", "pdfstudio.iss")])
            if rc == 0:
                print(f"\n✔ Kurulum sihirbazı: dist\\installer\\PDFStudio-{VERSION}-Setup.exe")
            return rc
        print("\n! Inno Setup bulunamadı — kurulum sihirbazı atlandı.")
        print("  https://jrsoftware.org/isdl.php adresinden kurup tekrar deneyin.")

    print(f"\n✔ Çıktı: {exe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
