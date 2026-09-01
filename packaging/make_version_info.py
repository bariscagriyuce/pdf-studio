#!/usr/bin/env python3
"""Windows .exe sürüm kaynağını (VERSIONINFO) verilen sürüm numarasından üretir.

    python packaging/make_version_info.py 1.2.3
    python packaging/make_version_info.py          # pdfstudio.__version__ kullanır
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "version_info.txt")

TEMPLATE = """# packaging/make_version_info.py tarafindan uretildi - elle duzenlemeyin.
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={tup},
    prodvers={tup},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '041F04B0',
        [StringStruct('CompanyName', 'PDF Studio'),
         StringStruct('FileDescription', 'PDF Studio - PDF Duzenleyici'),
         StringStruct('FileVersion', '{display}'),
         StringStruct('InternalName', 'PDFStudio'),
         StringStruct('LegalCopyright', 'PyMuPDF (AGPL-3.0) ve PySide6 (LGPL-3.0) kullanir'),
         StringStruct('OriginalFilename', 'PDFStudio.exe'),
         StringStruct('ProductName', 'PDF Studio'),
         StringStruct('ProductVersion', '{display}')])
    ]),
    VarFileInfo([VarStruct('Translation', [0x041F, 1200])])
  ]
)
"""


def numeric_tuple(version: str) -> tuple[int, int, int, int]:
    """'1.2.3-beta1' -> (1, 2, 3, 0). VERSIONINFO yalnızca sayı kabul eder."""
    parts = re.split(r"[^0-9]+", version.strip().lstrip("vV"))
    nums = [int(p) for p in parts if p != ""][:4]
    while len(nums) < 4:
        nums.append(0)
    return tuple(nums)  # type: ignore[return-value]


def package_version() -> str:
    init = os.path.join(ROOT, "pdfstudio", "__init__.py")
    with open(init, encoding="utf-8") as fh:
        m = re.search(r'__version__\s*=\s*"([^"]+)"', fh.read())
    return m.group(1) if m else "1.0.0"


def main() -> int:
    version = sys.argv[1] if len(sys.argv) > 1 else package_version()
    version = version.strip().lstrip("vV")
    tup = numeric_tuple(version)
    with open(OUT, "w", encoding="ascii") as fh:
        fh.write(TEMPLATE.format(tup=str(tup), display=version))
    print(f"OK: {OUT} (version {version} -> {tup})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
