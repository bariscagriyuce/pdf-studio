"""Sistem yazı tiplerini tarar; PDF'e Unicode (Türkçe dahil) metin gömmeyi sağlar.

PDF'in yerleşik 14 fontu (helv, tiro, cour ...) yalnızca Latin-1 kodlar; bu da
"ığşİĞŞ" gibi karakterleri bozar. Bu modül sistemdeki TTF/OTF dosyalarını
bulup ad tablolarını okuyarak gerçek aile adlarıyla eşler.
"""
from __future__ import annotations

import json
import os
import struct
import sys
from dataclasses import dataclass, asdict

# Türkçe için güvenli, yaygın bulunan aileler (tercih sırasıyla)
PREFERRED_UNICODE = [
    "DejaVu Sans", "Noto Sans", "Liberation Sans", "Arial", "Segoe UI",
    "Ubuntu", "Cantarell", "Helvetica", "FreeSans",
]

# Yerleşik base14 kısayolları (yalnızca Latin-1 metin için)
BASE14 = {
    "Helvetica": "helv", "Helvetica-Bold": "hebo", "Helvetica-Oblique": "heit",
    "Helvetica-BoldOblique": "hebi",
    "Times-Roman": "tiro", "Times-Bold": "tibo", "Times-Italic": "tiit",
    "Times-BoldItalic": "tibi",
    "Courier": "cour", "Courier-Bold": "cobo", "Courier-Oblique": "coit",
    "Courier-BoldOblique": "cobi",
    "Symbol": "symb", "ZapfDingbats": "zadb",
}

_STD_ALIASES = {
    "arial": "Helvetica", "arialmt": "Helvetica", "helvetica": "Helvetica",
    "timesnewroman": "Times-Roman", "timesnewromanpsmt": "Times-Roman", "times": "Times-Roman",
    "couriernew": "Courier", "courier": "Courier", "couriernewpsmt": "Courier",
}


@dataclass
class FontInfo:
    family: str
    style: str
    path: str
    bold: bool = False
    italic: bool = False

    @property
    def key(self) -> tuple:
        return (self.family.lower(), self.bold, self.italic)


# --------------------------------------------------------------- TTF ad tablosu
def _read_name_table(path: str) -> tuple[str, str] | None:
    """(aile, stil) döndürür; okunamazsa None."""
    try:
        with open(path, "rb") as fh:
            data = fh.read(4)
            if data == b"ttcf":
                fh.seek(12)
                off = struct.unpack(">I", fh.read(4))[0]
                fh.seek(off)
                fh.read(4)
            else:
                fh.seek(0)
                fh.read(4)
            num_tables = struct.unpack(">H", fh.read(2))[0]
            fh.read(6)
            base = fh.tell()
            name_off = 0
            for i in range(num_tables):
                fh.seek(base + i * 16)
                rec = fh.read(16)
                if len(rec) < 16:
                    break
                tag, _cs, off, ln = struct.unpack(">4sIII", rec)
                if tag == b"name":
                    name_off = off
                    break
            if not name_off:
                return None
            fh.seek(name_off)
            hdr = fh.read(6)
            if len(hdr) < 6:
                return None
            _fmt, count, str_off = struct.unpack(">HHH", hdr)
            records = fh.read(count * 12)
            best: dict[int, tuple[int, str]] = {}
            for i in range(count):
                r = records[i * 12:(i + 1) * 12]
                if len(r) < 12:
                    break
                plat, enc, lang, nid, ln, off = struct.unpack(">HHHHHH", r)
                if nid not in (1, 2, 16, 17):
                    continue
                fh.seek(name_off + str_off + off)
                raw = fh.read(ln)
                try:
                    if plat == 3:
                        txt = raw.decode("utf-16-be", "ignore")
                    elif plat == 1:
                        txt = raw.decode("mac-roman", "ignore")
                    else:
                        txt = raw.decode("latin-1", "ignore")
                except Exception:
                    continue
                txt = txt.strip("\x00 ").strip()
                if not txt:
                    continue
                score = 3 if (plat == 3 and lang == 0x409) else (2 if plat == 3 else 1)
                if nid not in best or best[nid][0] < score:
                    best[nid] = (score, txt)
            family = (best.get(16) or best.get(1) or (0, ""))[1]
            style = (best.get(17) or best.get(2) or (0, "Regular"))[1]
            return (family, style) if family else None
    except Exception:
        return None


def _font_dirs() -> list[str]:
    dirs: list[str] = []
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        dirs += [
            os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
        ]
    elif sys.platform == "darwin":
        dirs += ["/System/Library/Fonts", "/Library/Fonts", os.path.join(home, "Library/Fonts")]
    else:
        dirs += [
            "/usr/share/fonts", "/usr/local/share/fonts",
            os.path.join(home, ".fonts"),
            os.path.join(home, ".local/share/fonts"),
        ]
    return [d for d in dirs if d and os.path.isdir(d)]


def cache_path() -> str:
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        d = os.path.join(base, "PDFStudio")
    else:
        base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
        d = os.path.join(base, "pdfstudio")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "fonts.json")


class FontManager:
    _instance: "FontManager | None" = None

    def __init__(self):
        self.fonts: list[FontInfo] = []
        self._by_key: dict[tuple, FontInfo] = {}
        self._families: list[str] = []
        self._loaded = False

    @classmethod
    def instance(cls) -> "FontManager":
        if cls._instance is None:
            cls._instance = FontManager()
            cls._instance.load()
        return cls._instance

    # ------------------------------------------------------------- yükleme
    def load(self, force: bool = False) -> None:
        if self._loaded and not force:
            return
        if not force and self._load_cache():
            self._loaded = True
            return
        self.scan()
        self._loaded = True

    def _load_cache(self) -> bool:
        try:
            with open(cache_path(), "r", encoding="utf-8") as fh:
                blob = json.load(fh)
            if blob.get("v") != 2:
                return False
            fonts = [FontInfo(**d) for d in blob["fonts"]]
            fonts = [f for f in fonts if os.path.exists(f.path)]
            if len(fonts) < 3:
                return False
            self._install(fonts)
            return True
        except Exception:
            return False

    def _save_cache(self) -> None:
        try:
            with open(cache_path(), "w", encoding="utf-8") as fh:
                json.dump({"v": 2, "fonts": [asdict(f) for f in self.fonts]}, fh)
        except Exception:
            pass

    def scan(self) -> None:
        found: list[FontInfo] = []
        seen: set[str] = set()
        for root in _font_dirs():
            for dirpath, _dirs, files in os.walk(root):
                for name in files:
                    ext = os.path.splitext(name)[1].lower()
                    if ext not in (".ttf", ".otf", ".ttc"):
                        continue
                    path = os.path.join(dirpath, name)
                    real = os.path.realpath(path)
                    if real in seen:
                        continue
                    seen.add(real)
                    info = _read_name_table(path)
                    if not info:
                        continue
                    family, style = info
                    low = style.lower()
                    found.append(FontInfo(
                        family=family, style=style, path=path,
                        bold="bold" in low or "black" in low or "heavy" in low,
                        italic="italic" in low or "oblique" in low,
                    ))
        self._install(found)
        self._save_cache()

    @staticmethod
    def _style_rank(f: "FontInfo") -> int:
        """Aynı (aile, kalın, italik) anahtarı için en "normal" kesimi öne alır."""
        low = f.style.lower().replace(" ", "")
        for i, token in enumerate(("regular", "book", "roman", "normal", "bold", "italic",
                                   "boldialic", "bolditalic", "oblique")):
            if low == token:
                return i
        penalty = 20
        for bad in ("light", "thin", "extra", "ultra", "semi", "medium", "condensed",
                    "narrow", "black", "heavy", "display", "caption", "mono"):
            if bad in low:
                penalty += 5
        return penalty + len(low)

    def _install(self, fonts: list[FontInfo]) -> None:
        self.fonts = sorted(fonts, key=lambda f: (f.family.lower(), self._style_rank(f)))
        self._by_key = {}
        for f in self.fonts:
            self._by_key.setdefault(f.key, f)
        self._families = sorted({f.family for f in self.fonts}, key=str.lower)

    # -------------------------------------------------------------- sorgular
    def families(self) -> list[str]:
        return self._families

    @staticmethod
    def _squash(name: str) -> str:
        return "".join(ch for ch in (name or "").lower() if ch.isalnum())

    def find(self, family: str, bold: bool = False, italic: bool = False) -> FontInfo | None:
        fam = (family or "").lower()
        for key in ((fam, bold, italic), (fam, bold, False), (fam, False, italic),
                    (fam, False, False)):
            f = self._by_key.get(key)
            if f:
                return f
        # boşluk/tire farklarını yok sayarak tam eşleşme ("DejaVuSans" ↔ "DejaVu Sans")
        squashed = self._squash(family)
        if squashed:
            for want_b, want_i in ((bold, italic), (bold, False), (False, italic),
                                   (False, False)):
                for f in self.fonts:
                    if (self._squash(f.family) == squashed and f.bold == want_b
                            and f.italic == want_i):
                        return f
        # kısmi eşleşme
        for f in self.fonts:
            if fam and fam in f.family.lower() and f.bold == bold and f.italic == italic:
                return f
        for f in self.fonts:
            if squashed and squashed in self._squash(f.family):
                return f
        return None

    def default_unicode(self, bold: bool = False, italic: bool = False) -> FontInfo | None:
        for fam in PREFERRED_UNICODE:
            f = self.find(fam, bold, italic)
            if f:
                return f
        return self.fonts[0] if self.fonts else None

    def path_for(self, family: str, bold: bool = False, italic: bool = False) -> str | None:
        f = self.find(family, bold, italic) or self.default_unicode(bold, italic)
        return f.path if f else None


# ------------------------------------------------------------------ yardımcılar
def is_latin1(text: str) -> bool:
    try:
        text.encode("latin-1")
        return True
    except UnicodeEncodeError:
        return False


def normalize_pdf_fontname(name: str) -> tuple[str, bool, bool]:
    """'ABCDEF+Arial-BoldMT' -> ('Arial', True, False)"""
    n = name or ""
    if "+" in n[:8]:
        n = n.split("+", 1)[1]
    bold = any(t in n.lower() for t in ("bold", "black", "heavy", "semibold"))
    italic = any(t in n.lower() for t in ("italic", "oblique"))
    for sep in ("-", ","):
        if sep in n:
            n = n.split(sep)[0]
    for suffix in ("MT", "PS", "PSMT", "Std", "Pro"):
        if n.endswith(suffix) and len(n) > len(suffix) + 2:
            n = n[: -len(suffix)]
    return n.strip() or "Helvetica", bold, italic


def resolve_insert_font(family: str, bold: bool, italic: bool, text: str) -> tuple[str, str | None]:
    """(fontname, fontfile) ikilisi döndürür.

    Metin Latin-1 ile ifade edilebiliyorsa ve aile standart bir base14 ise
    gömme yapılmaz (dosya küçük kalır); aksi halde bir TTF gömülür.
    """
    fm = FontManager.instance()
    canon = _STD_ALIASES.get(family.replace(" ", "").lower())
    if canon and is_latin1(text):
        name = canon
        if canon == "Helvetica":
            name = ("Helvetica-BoldOblique" if bold and italic else
                    "Helvetica-Bold" if bold else "Helvetica-Oblique" if italic else "Helvetica")
        elif canon == "Times-Roman":
            name = ("Times-BoldItalic" if bold and italic else "Times-Bold" if bold else
                    "Times-Italic" if italic else "Times-Roman")
        elif canon == "Courier":
            name = ("Courier-BoldOblique" if bold and italic else "Courier-Bold" if bold else
                    "Courier-Oblique" if italic else "Courier")
        return BASE14[name], None

    path = fm.path_for(family, bold, italic)
    if path:
        alias = "F" + str(abs(hash((path, bold, italic))) % 10**8)
        return alias, path
    return BASE14["Helvetica"], None


def text_width(text: str, fontsize: float, family: str, bold: bool = False,
               italic: bool = False) -> float:
    import pymupdf
    name, fontfile = resolve_insert_font(family, bold, italic, text)
    try:
        font = pymupdf.Font(fontfile=fontfile) if fontfile else pymupdf.Font(name)
        return font.text_length(text, fontsize)
    except Exception:
        return len(text) * fontsize * 0.5
