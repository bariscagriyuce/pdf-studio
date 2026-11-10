# Paketleme

Bu klasör, YUCE PDF Düzenleyici'yi kurulabilir dosyalara dönüştüren her şeyi içerir.

| Dosya | Görevi |
|---|---|
| `pdfstudio.spec` | PyInstaller yapılandırması (Linux + Windows + macOS ortak; macOS'ta `.app` paketi de üretir). `PDFSTUDIO_ONEFILE=1` ortam değişkeni tek dosyalık çıktı üretir. |
| `version_info.txt` | Windows `.exe` sürüm bilgisi — **üretilen dosya**, elle düzenlemeyin |
| `make_version_info.py` | `version_info.txt` üreteci |
| `set_version.py` | Sürümü tek komutla her yere işler (`__init__.py` + `version_info.txt`) |
| `make_icons.py` | `icon.png`, çok boyutlu `icon.ico` ve macOS `icon.icns` üreteci |
| `make_macos_dmg.sh` | `.app` paketini imzalar (ad-hoc) ve sürükle-bırak `.dmg` üretir |
| `pdfstudio.iss` | Inno Setup kurulum sihirbazı betiği |
| `LICENSE-notice.txt` | Kurulumda gösterilen lisans metni |
| `installer_header.sh` | Linux `.run` dosyasının kendi kendini açan başlığı |
| `make_linux_installer.sh` | PyInstaller çıktısını tek `.run` dosyasına paketler |
| `arch/PKGBUILD.in` | Arch/CachyOS paket tarifi |
| `arch/build-arch-package.sh` | `.pkg.tar.zst` üretir (makepkg ile) |

## Linux kurulum dosyası üretmek

```bash
python3 -m venv build-venv
build-venv/bin/python -m pip install PySide6-Essentials PyMuPDF pyinstaller
build-venv/bin/python -m PyInstaller --noconfirm --clean packaging/pdfstudio.spec
./dist/PDFStudio/PDFStudio --self-test        # doğrula
bash packaging/make_linux_installer.sh dist/PDFStudio YUCE-PDF-Editor-1.1.0-x86_64.run 1.1.0
```

## Arch / CachyOS paketi üretmek

```bash
bash packaging/arch/build-arch-package.sh dist/PDFStudio 1.1.0
sudo pacman -U pdf-studio-1.1.0-1-x86_64.pkg.tar.zst
```

`PKGBUILD` içinde `options=('!strip')` **şart** — PyInstaller çıktısını
strip etmek çalıştırılabiliri bozar.

> Derlemeyi mümkün olan **en eski** dağıtımda yapın (Ubuntu 22.04 önerilir).
> Üretilen dosya, derlendiği makinenin glibc sürümünden **eski** sistemlerde
> çalışmaz. CI iş akışı bu yüzden `ubuntu-22.04` kullanır.

## macOS kurulum dosyası üretmek

```bash
python3 -m venv build-venv
build-venv/bin/python -m pip install "PySide6-Essentials>=6.8,<6.9" PyMuPDF pyinstaller
build-venv/bin/python build.py
# → dist/YUCE PDF EDITOR.app  +  dist/YUCE-PDF-Editor-<sürüm>-macOS-arm64.dmg
```

Yalnızca Apple Silicon (M1 ve sonrası, `arm64`) için derlenir; Intel Mac'ler desteklenmez.

> **Başka Mac'lere dağıtılacak yapılar için Homebrew Python'u kullanmayın.**
> Homebrew'un Python'u kendi macOS sürümünüz için derlenir; paket yalnızca o
> sürüm ve sonrasında açılır. [python.org](https://www.python.org/downloads/macos/)
> kurulumu ya da `uv python install 3.12` macOS 11+ hedefler. Qt 6.9 ve sonrası
> macOS 13/14+ istediği için PySide6 **6.8 LTS**'e sabitlenir → paket macOS 12+.
> Kontrol: `vtool -show-build "dist/YUCE PDF EDITOR.app/Contents/MacOS/PDFStudio"`.

İmza: Apple geliştirici hesabı olmadan uygulama **ad-hoc** imzalanır (Apple
Silicon'da imzasız kod hiç çalışmaz). Notarize edilmediği için kullanıcı ilk
açılışta *sağ tık → Aç* demelidir. Developer ID sertifikanız varsa:
`MACOS_SIGN_IDENTITY="Developer ID Application: …" bash packaging/make_macos_dmg.sh …`
(ardından `xcrun notarytool submit … --wait` ve `xcrun stapler staple`).

## Windows kurulum dosyası üretmek

Bir Windows makinede (veya GitHub Actions'ta):

```powershell
python -m pip install PySide6-Essentials PyMuPDF pyinstaller
pyinstaller --noconfirm --clean packaging\pdfstudio.spec
dist\PDFStudio\PDFStudio.exe --self-test --log selftest.log

# Kurulum sihirbazı  (Inno Setup 6 gerekir: https://jrsoftware.org/isdl.php)
iscc packaging\pdfstudio.iss

# Taşınabilir tek dosya
$env:PDFSTUDIO_ONEFILE = "1"
pyinstaller --noconfirm --clean --distpath dist-onefile packaging\pdfstudio.spec
```

## Sürüm numarası

Tek kaynak: `pdfstudio/__init__.py` içindeki `__version__`.

```bash
python packaging/set_version.py 1.2.3   # her yere işler
```

CI'da etiketli derlemelerde sürüm git etiketinden okunur (`v1.2.3` → `1.2.3`) ve
aynı betikle uygulanır. Ön sürüm etiketleri (`1.2.3-beta1`) desteklenir; Windows
`VersionInfoVersion` alanı yalnızca sayı kabul ettiği için ayrıca sayısal bir
değer türetilir.

## Otomatik derleme (GitHub Actions)

`.github/workflows/build.yml` üç platformu da (Windows, Linux, macOS arm64) derler, her yapıyı gömülü
sınamadan geçirir ve çıktıları artefakt olarak yükler.

- **Elle çalıştırma:** depo → *Actions* → *Kurulum dosyalarını derle* → *Run workflow*
- **Sürüm yayımlama:** `git tag v1.0.0 && git push --tags` → dosyalar otomatik
  olarak GitHub *Releases* sayfasına, SHA256 toplamlarıyla birlikte yüklenir.

Çıktılar:

| Dosya | Platform |
|---|---|
| `YUCE-PDF-Editor-1.1.0-Setup.exe` | Windows 10/11 — kurulum sihirbazı |
| `YUCE-PDF-Editor-1.1.0-portable.exe` | Windows 10/11 — taşınabilir tek dosya |
| `YUCE-PDF-Editor-1.1.0-x86_64.run` | Linux (glibc 2.35+) |
| `YUCE-PDF-Editor-1.1.0-macOS-arm64.dmg` | macOS 12+ — Apple Silicon |

## Boyut hakkında

Paket ~250 MB açılır, sıkıştırılmış hâli ~73 MB. Dağılım:
Qt 6 (~83 MB) · MuPDF motoru (~53 MB) · ICU yerelleştirme verisi (~32 MB) ·
Python çalışma zamanı (~10 MB). `pdfstudio.spec` içindeki `EXCLUDES` ve
`DROP_PATTERNS` listeleri kullanılmayan Qt modüllerini ve GTK bağımlılıklarını
zaten ayıklıyor (ham çıktı 370 MB → 253 MB).
