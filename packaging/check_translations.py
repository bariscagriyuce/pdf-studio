#!/usr/bin/env python3
"""Çeviri kataloglarını kaynak koda karşı denetler.

    python packaging/check_translations.py            # denetle (hata varsa çıkış 1)
    python packaging/check_translations.py --missing en > eksik.json

Denetimler:
  * Kodda kullanılan her anahtarın her katalogda çevirisi var mı
  * Çevirideki yer tutucular ({0}, {name}, {0:.0f}) kaynakla aynı mı —
    uyumsuzluk, o mesaj gösterildiğinde uygulamayı çökertir
  * _n() ile kullanılan anahtarların tekil/çoğul biçimleri var mı
  * Katalogda artık kullanılmayan girdiler (uyarı)
"""
from __future__ import annotations

import ast
import json
import os
import string
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PKG = os.path.join(ROOT, "pdfstudio")
LANGS = ["en", "pt_BR"]
MARKERS = {"_", "_n", "N_", "tr"}


def extract() -> dict[str, set[str]]:
    """{anahtar: {kullanılan işlev adları}} ve konumları."""
    keys: dict[str, set[str]] = {}
    where: dict[str, str] = {}
    for dirpath, _dirs, files in os.walk(PKG):
        if os.path.basename(dirpath) == "locales":
            continue
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            tree = ast.parse(open(path, encoding="utf-8").read(), path)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not node.args:
                    continue
                fn = node.func.id if isinstance(node.func, ast.Name) else None
                if fn not in MARKERS:
                    continue
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    keys.setdefault(arg.value, set()).add(fn)
                    where.setdefault(arg.value, f"{os.path.relpath(path, ROOT)}:{node.lineno}")
    extract.where = where
    return keys


def fields(text: str) -> list[str]:
    out = []
    for _lit, field, spec, conv in string.Formatter().parse(text):
        if field is not None:
            out.append(f"{field}!{conv or ''}:{spec or ''}")
    return sorted(out)


def load(code: str) -> dict:
    sys.path.insert(0, ROOT)
    import importlib
    return importlib.import_module(f"pdfstudio.locales.{code}").MESSAGES


def main() -> int:
    keys = extract()
    if "--missing" in sys.argv:
        code = sys.argv[sys.argv.index("--missing") + 1]
        cat = load(code)
        miss = {k: ("PLURAL" if "_n" in keys[k] else "") for k in sorted(keys) if k not in cat}
        print(json.dumps(miss, ensure_ascii=False, indent=1))
        return 0

    errors = 0
    for code in LANGS:
        cat = load(code)
        missing = [k for k in keys if k not in cat]
        stale = [k for k in cat if k not in keys]
        bad = []
        for k, v in cat.items():
            forms = list(v.values()) if isinstance(v, dict) else [v]
            for form in forms:
                try:
                    if fields(form) != fields(k):
                        bad.append((k, form))
                except ValueError as exc:
                    bad.append((k, f"{form}  ({exc})"))
            if k in keys and "_n" in keys[k] and not (isinstance(v, dict) and "one" in v and "other" in v):
                bad.append((k, "_n() anahtarı için {'one':..., 'other':...} gerekli"))
        print(f"[{code}] anahtar: {len(keys)}  çevrili: {len(keys) - len(missing)}  "
              f"eksik: {len(missing)}  yer tutucu hatası: {len(bad)}  kullanılmayan: {len(stale)}")
        for k in missing[:40]:
            print(f"    EKSİK  {extract.where[k]}: {k!r}")
        if len(missing) > 40:
            print(f"    ... ve {len(missing) - 40} tane daha")
        for k, v in bad:
            print(f"    HATA   {k!r} -> {v!r}")
        for k in stale[:10]:
            print(f"    (kullanılmıyor) {k!r}")
        errors += len(missing) + len(bad)
    print("SONUÇ:", "TAMAM" if not errors else f"{errors} sorun")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
