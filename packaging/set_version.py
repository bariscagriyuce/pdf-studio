#!/usr/bin/env python3
"""Sürüm numarasını tek komutla her yere işler.

    python packaging/set_version.py 1.2.3

pdfstudio/__init__.py içindeki __version__ değerini günceller ve Windows
sürüm kaynağını (packaging/version_info.txt) yeniden üretir. CI, git etiketinden
gelen sürümü buraya vererek tüm çıktıları tek kaynaktan isimlendirir.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INIT = os.path.join(ROOT, "pdfstudio", "__init__.py")


def main() -> int:
    if len(sys.argv) < 2:
        print("Kullanım: python packaging/set_version.py <sürüm>", file=sys.stderr)
        return 2
    version = sys.argv[1].strip().lstrip("vV")
    if not re.match(r"^\d+(\.\d+)*([-+][0-9A-Za-z.\-]+)?$", version):
        print(f"Geçersiz sürüm biçimi: {version}", file=sys.stderr)
        return 2

    with open(INIT, encoding="utf-8") as fh:
        text = fh.read()
    new, n = re.subn(r'__version__\s*=\s*"[^"]*"', f'__version__ = "{version}"', text)
    if not n:
        print(f"__version__ bulunamadı: {INIT}", file=sys.stderr)
        return 1
    with open(INIT, "w", encoding="utf-8") as fh:
        fh.write(new)
    print(f"✔ {INIT} → {version}")

    subprocess.check_call([sys.executable,
                           os.path.join(HERE, "make_version_info.py"), version])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
