"""Arayüz çevirisi.

Kaynak dil Türkçedir: koddaki Türkçe metinler aynı zamanda çeviri
anahtarıdır (gettext yaklaşımı). Diğer diller ``pdfstudio/locales/<kod>.py``
içindeki ``MESSAGES`` sözlüğünden gelir. Bir anahtarın çevirisi yoksa Türkçe
metin gösterilir; böylece eksik bir çeviri arayüzü bozmaz, yalnızca o satır
Türkçe kalır (``packaging/check_translations.py`` bunları yakalar).

Kullanım:
    from ..i18n import _, _n
    _("Kaydet")
    _("Sayfa {n} / {total}").format(n=3, total=10)
    _n("{n} sonuç bulundu", count).format(n=count)

Dil, uygulama açılırken bir kez seçilir; değiştirmek yeniden başlatma gerektirir.
"""
from __future__ import annotations

import os

#: Desteklenen diller — adlar kendi dillerinde yazılır (kullanıcı tanısın diye)
LANGUAGES: dict[str, str] = {
    "tr": "Türkçe",
    "en": "English",
    "pt_BR": "Português (Brasil)",
}
SOURCE_LANGUAGE = "tr"
SYSTEM = "system"

_current = SOURCE_LANGUAGE
_catalog: dict = {}


def _load_catalog(code: str) -> dict:
    # Statik içe aktarma: PyInstaller katalogları kendiliğinden paketlesin
    if code == "en":
        from .locales import en as mod
    elif code == "pt_BR":
        from .locales import pt_BR as mod
    else:
        return {}
    return dict(mod.MESSAGES)


def system_language() -> str:
    """Sistem dilini desteklenen bir koda eşler (tr / pt_BR / en)."""
    name = ""
    try:
        from PySide6.QtCore import QLocale
        name = QLocale.system().name()          # "tr_TR", "pt_BR", "en_US"
    except Exception:
        import locale
        name = locale.getlocale()[0] or os.environ.get("LANG", "")
    name = (name or "").replace("-", "_")
    if name.lower().startswith("tr"):
        return "tr"
    if name.lower().startswith("pt"):
        return "pt_BR"
    return "en"


def resolve(preference: str | None) -> str:
    """'system' veya geçersiz değerleri gerçek bir dil koduna çevirir."""
    if preference in LANGUAGES:
        return preference  # type: ignore[return-value]
    return system_language()


def _settings():
    from PySide6.QtCore import QSettings
    return QSettings("PDFStudio", "PDFStudio")


def saved_preference() -> str:
    """Kullanıcının seçimi: 'system', 'tr', 'en' veya 'pt_BR'.

    PDFSTUDIO_LANG ortam değişkeni kayıtlı seçimi geçersiz kılar (sınama için).
    """
    forced = os.environ.get("PDFSTUDIO_LANG", "").strip()
    if forced:
        for code in LANGUAGES:
            if forced.lower().replace("-", "_") in (code.lower(), code.lower()[:2]):
                return code
        return SYSTEM
    try:
        value = _settings().value("language", SYSTEM)
    except Exception:
        value = SYSTEM
    return value if (value in LANGUAGES or value == SYSTEM) else SYSTEM


def save_preference(preference: str) -> None:
    _settings().setValue("language", preference)


def set_language(code: str) -> str:
    global _current, _catalog
    code = resolve(code)
    _current = code
    _catalog = _load_catalog(code)
    return code


def init() -> str:
    """Kayıtlı tercihe göre dili kurar; seçilen kodu döndürür."""
    return set_language(saved_preference())


def current() -> str:
    return _current


def _(text: str) -> str:
    if _current == SOURCE_LANGUAGE or not text:
        return text
    value = _catalog.get(text)
    if isinstance(value, dict):
        value = value.get("other")
    return value or text


def N_(text: str) -> str:
    """Çeviri için *işaretler* ama çevirmez. İçe aktarma anında değerlendirilen
    yerlerde (modül sabitleri, varsayılan argümanlar) kullanılır; metin
    gösterilirken ayrıca _() ile çevrilir."""
    return text


def _n(text: str, n: int) -> str:
    """Sayıya göre tekil/çoğul seçen çeviri. Katalog değeri
    {"one": "...", "other": "..."} olabilir. Türkçede isim çoğul eki
    sayıdan sonra kullanılmadığı için kaynak metin tek biçimlidir."""
    if _current == SOURCE_LANGUAGE:
        return text
    value = _catalog.get(text)
    if isinstance(value, dict):
        # pt_BR'de 0 ve 1 tekil; İngilizcede yalnızca 1
        singular = n in (0, 1) if _current == "pt_BR" else n == 1
        return value.get("one" if singular else "other") or value.get("other") or text
    return value or text


def translate_to(code: str, text: str) -> str:
    """Metni etkin dilden bağımsız olarak verilen dile çevirir."""
    code = resolve(code)
    if code == SOURCE_LANGUAGE:
        return text
    value = _load_catalog(code).get(text)
    if isinstance(value, dict):
        value = value.get("other")
    return value or text


def install_qt_translators(app) -> list:
    """Qt'nin kendi pencereleri (Evet/Hayır, dosya seçici, renk seçici,
    baskı önizleme) için çevirileri yükler. Döndürülen nesneler canlı
    tutulmalıdır."""
    from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
    loaded = []
    code = _current
    paths = [QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath),
             "/usr/share/qt6/translations"]
    for base in ("qtbase", "qt"):
        tr = QTranslator(app)
        for p in paths:
            if p and tr.load(QLocale(code), base, "_", p):
                app.installTranslator(tr)
                loaded.append(tr)
                break
    if loaded:
        fb = _mnemonic_fallback(app, list(loaded))
        app.installTranslator(fb)
        loaded.append(fb)
    return loaded


def _mnemonic_fallback(app, bases: list):
    """Qt'nin yeni sürümleri bazı metinlere kısayol işareti ekledi
    ("Pages per sheet:" → "Pages &per sheet:"), ama Qt'nin kendi çeviri
    dosyalarında bu metinler eski hâlleriyle duruyor; eşleşmedikleri için
    yazdırma penceresinde İngilizce kalıyorlar. Bu çevirmen, karşılığı
    bulunamayan metni '&' olmadan bir daha arar."""
    from PySide6.QtCore import QTranslator

    class MnemonicFallback(QTranslator):
        def translate(self, context, source, disambiguation=None, n=-1):
            if not source or "&" not in source:
                return None
            for t in bases:
                if t.translate(context, source, disambiguation, n):
                    return None          # zaten çevriliyor, karışma
            plain = source.replace("&&", "\0").replace("&", "").replace("\0", "&&")
            for t in bases:
                text = t.translate(context, plain, disambiguation, n)
                if text:
                    return text if "&" in text else "&" + text
            return None

        def isEmpty(self):
            return False

    return MnemonicFallback(app)
