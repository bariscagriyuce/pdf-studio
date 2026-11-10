# YUCE PDF EDITOR

[Türkçe](README.md) · **English** · [Português (Brasil)](README.pt-BR.md)

*YUCE PDF Düzenleyici*

An **Adobe Acrobat Pro–style** desktop PDF editor for Windows, macOS and Linux. It edits
the real text in the page content, adds annotations, manages pages, fills forms,
applies true redaction and encrypts documents.

| | |
|---|---|
| **Engine** | PyMuPDF (MuPDF) — fast, local, no network connection needed |
| **Interface** | PySide6 (Qt 6) — dark/light theme; Turkish, English, Brazilian Portuguese |
| **Platforms** | Windows, macOS, Linux |

---

## Installation

### Ready-made installers

The current files are on the **[Releases → latest release](https://github.com/bariscagriyuce/pdf-studio/releases/latest)**
page. Below, replace `<version>` with the version you downloaded (e.g. `1.2.0`).

| Platform | File | How to install |
|---|---|---|
| **Windows** 10/11 | `YUCE-PDF-Editor-<version>-Setup.exe` | Double-click and follow the wizard |
| **Windows** (no install) | `YUCE-PDF-Editor-<version>-portable.exe` | Double-click; runs directly |
| **Linux** (glibc 2.35+) | `YUCE-PDF-Editor-<version>-x86_64.run` | `bash YUCE-PDF-Editor-<version>-x86_64.run` |
| **macOS** 12+ (Apple Silicon: M1–M4) | `YUCE-PDF-Editor-<version>-macOS-arm64.dmg` | Open it, drag the app to *Applications* |
| **macOS** 12+ (Intel) | `YUCE-PDF-Editor-<version>-macOS-x86_64.dmg` | Open it, drag the app to *Applications* |

Python does not need to be installed; everything is bundled. Every file passes
the built-in self-test before it is published, and you can verify its integrity
with `SHA256SUMS.txt` on the release page.

> **Name change (1.1.0):** The application was previously called *PDF Studio*.
> Technical identifiers were deliberately kept — the command is still
> `pdf-studio`, the package name `pdf-studio`, the executable `PDFStudio.exe`.
> This way new versions update older installs in place and your settings are kept.

#### Windows

`Setup.exe` opens an installation wizard in Turkish, English or Brazilian
Portuguese and can install for you only (no administrator rights needed) or for
all users. It adds a Start menu shortcut, an optional desktop shortcut and an
"Open with" entry for PDF files, and uninstalls cleanly from the Control Panel.

#### macOS — `.dmg`

Download the file that matches your Mac's processor ( → *About This Mac*:
"Apple M…" means `arm64`, "Intel" means `x86_64`). Open the `.dmg` and drag
**YUCE PDF EDITOR** into *Applications*. The app appears in Finder's *Open With*
list, and you can also drop PDFs onto its Dock icon.

> **"Cannot be verified" warning on first launch:** The app is not signed with an
> Apple developer certificate (not notarized), so macOS warns the first time.
> Open it once like this: in *Applications*, **right-click the icon → Open → Open**.
> On macOS 15 and later: try to open it, then click **"Open Anyway"** under
> *System Settings → Privacy & Security*. From Terminal:
>
> ```bash
> xattr -dr com.apple.quarantine "/Applications/YUCE PDF EDITOR.app"
> ```

To uninstall, move the app to the Trash (settings:
`~/Library/Preferences/com.pdfstudio.PDFStudio.plist`, cache:
`~/Library/Caches/PDFStudio`).

#### Linux — `.run` installer

```bash
bash YUCE-PDF-Editor-<version>-x86_64.run
```

Without root it installs under `~/.local/opt/pdf-studio`; with `sudo`, under
`/opt/pdf-studio`. It adds an application-menu entry and the `pdf-studio`
command. Options:

```bash
bash YUCE-PDF-Editor-<version>-x86_64.run --help       # all options
bash YUCE-PDF-Editor-<version>-x86_64.run --verify     # install, then run the self-test
bash YUCE-PDF-Editor-<version>-x86_64.run --system     # system-wide, with sudo
bash YUCE-PDF-Editor-<version>-x86_64.run --extract .  # extract only, do not install
bash YUCE-PDF-Editor-<version>-x86_64.run --uninstall  # uninstall
```

> The installer's own terminal messages are in Turkish; the application itself
> follows the language you choose.

> **Why doesn't double-clicking work?** Two common reasons:
>
> 1. **The file is on an NTFS/FAT drive.** These file systems cannot store the
>    executable permission; `chmod +x` silently has no effect. Copy the file to
>    your home folder: `cp YUCE-PDF-Editor-*.run ~/ && chmod +x ~/YUCE-PDF-Editor-*.run`
> 2. **Your desktop does not run shell scripts.** KDE/Dolphin and GNOME/Nautilus
>    open files like `.run` in a text editor by default. On KDE: *Dolphin →
>    Settings → Configure Dolphin → General → Confirmations → "When opening an
>    executable file"* → **"Run script"**.
>
> Running `bash YUCE-PDF-Editor-*.run` from a terminal always works — `.run`
> installers (NVIDIA driver, Anaconda, etc.) are traditionally used this way.

#### Arch / CachyOS / Manjaro — local package

There is **no** prebuilt Arch package on the release page; the `.run` installer
also works on Arch-based distributions. If you prefer an install managed by
pacman, you can build the package from source (see
[Building your own installer](#building-your-own-installer) below):

```bash
bash packaging/arch/build-arch-package.sh dist/PDFStudio <version>
sudo pacman -U pdf-studio-<version>-1-x86_64.pkg.tar.zst
```

It installs under `/opt/pdf-studio`; uninstall with `sudo pacman -R pdf-studio`.

#### Verifying the installation

```bash
pdf-studio --self-test
```

The application creates a real document, runs every path — text editing,
annotations, redaction, forms, encryption and export — and reports the result.

### Running from source

For development or to try your own changes:

```bash
bash run.sh
```

`bash run.sh` also works on macOS (requires Python 3.9+: `brew install python@3.12`).
On Windows, `run.bat`. The first run creates a virtual environment and
downloads the dependencies; later starts are instant.

### Building your own installer

See [`packaging/README.md`](packaging/README.md) (in Turkish) for details. In short:

```bash
python3 -m PyInstaller --noconfirm --clean packaging/pdfstudio.spec

# Universal .run installer
bash packaging/make_linux_installer.sh dist/PDFStudio YUCE-PDF-Editor-<version>-x86_64.run <version>

# Arch/CachyOS package (requires makepkg)
bash packaging/arch/build-arch-package.sh dist/PDFStudio <version>
```

On macOS a single command produces the `.app` and the `.dmg`:

```bash
python3 build.py     # → dist/YUCE PDF EDITOR.app and dist/YUCE-PDF-Editor-<version>-macOS-<arch>.dmg
```

Each platform's files can only be built on that platform.
Windows files cannot be built on Linux. The `.github/workflows/build.yml`
workflow builds all three platforms (Windows, Linux, macOS) on GitHub's machines:

- **Manual build:** repository → *Actions* → *Kurulum dosyalarını derle* → *Run workflow*.
  The outputs are kept as artifacts for 90 days.
- **Publishing a release:** `git tag v1.2.3 && git push --tags`. The files are
  uploaded to the *Releases* page with SHA256 checksums and **stay there
  permanently** (unlike artifacts, they do not expire).

Every build passes the built-in self-test and the translation check before it is uploaded.

#### How the version number is set

There is a single source: `__version__` in `pdfstudio/__init__.py`. In a tagged
build the version is **read from the tag** and applied everywhere by
`packaging/set_version.py`: file names, Windows executable properties, the
installer wizard and the application's About window. So the `v1.2.3` tag
produces `YUCE-PDF-Editor-1.2.3-Setup.exe`; no manual version bump is needed.

To change the version locally:

```bash
python packaging/set_version.py 1.2.3
```

### Linux desktop shortcut (when running from source)

```bash
sudo cp -r . /opt/pdf-studio && sudo cp pdf-studio.desktop /usr/share/applications/ && sudo cp pdfstudio/resources/icon.png /usr/share/icons/hicolor/512x512/apps/pdf-studio.png
```

---

## Features

### Text editing (the main difference)
- **Edit text tool (E)** — click a text block on the page and edit its content,
  font, size, color, alignment and line spacing in a window with a live preview.
  The old text is really removed (redaction) and the new text is written into
  the page content.
- **Full Unicode support** — PDF's 14 built-in fonts cannot encode characters
  such as Turkish `ığşİĞŞ`. The application scans the system's TTF/OTF files,
  maps them to their real family names and embeds the font when needed.
- **Add text (T)** — draw a box on the page and type new text; it is added as
  real page content, not as an annotation.
- **Find and replace** — across the whole document, keeping the original font and color.
- **Erase area** — permanently removes text, graphics and images in the selected region.

### Annotations
Highlight, underline, strikeout, squiggly, sticky note, free text box, freehand
drawing (pen), rectangle, ellipse, line, arrow, polygon, stamp, link, file
attachment. Each annotation has color, fill, width, opacity and author
settings; select to move, resize with handles, nudge with the arrow keys.

### Page management
Insert blank pages, delete, duplicate, rotate, reorder by dragging thumbnails,
crop, change page size, merge PDFs, split (every N pages or by ranges), extract
pages, insert images as pages, reverse the page order.

### Forms
List and fill form fields, add text boxes / check boxes, export and import
values as JSON, flatten the form.

### Images
Insert images on a page, list embedded images, move/resize, replace, delete,
export one by one or all at once.

### Signature
Draw it with the mouse, type it (in any font) or import a transparent PNG;
place it by drawing a box on the page.

### Security and privacy
AES-256 / AES-128 / RC4 encryption, user and owner passwords, detailed
permission control (printing, copying, editing, form filling…), password
removal, **true redaction** (the content is permanently removed, not just
painted over), metadata and JavaScript cleanup.

### Printing a selected area
With the **Print area** tool (`Ctrl+Shift+P`, the toolbar or the right-click
menu), draw a box on the page; only that region is printed. Options: fit to
paper, actual size or a custom scale; centering; crop marks; printing the same
area on several pages (for labels, receipts, form sections). A print preview
opens before printing. **Save as PDF** instead exports the area at actual size
in vector quality to a separate PDF — text stays selectable and annotations are
included.

### Export
PNG/JPG/WEBP images (36–1200 DPI, grayscale, transparent background), plain
text, HTML, XHTML, XML, JSON, selected pages as a separate PDF, embedded images,
file-size reduction (image resampling + font subsetting).

### OCR
If Tesseract is installed, adds a searchable text layer to scanned pages.

- Linux: `sudo pacman -S tesseract tesseract-data-eng`
  (Debian/Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-eng`)
- Windows: install [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki).

### Viewing
Continuous / single page / two pages / two pages (cover) layouts, 8%–1200% zoom,
fit width and fit page, thumbnail panel, bookmarks (add, rename, delete),
annotation list, search results panel, dark and light themes, print preview and
printing, drag and drop of PDFs.

---

## Languages

The interface supports **Turkish**, **English** and **Brazilian Portuguese**.
Choose it under *View → Language*; the change takes effect after a restart
(the application offers to restart itself with the open document). The default
is **System language**: a Turkish system opens in Turkish, a Portuguese system
in Portuguese, all others in English. Qt's own windows (Yes/No buttons, file
and color pickers, print preview) and number formatting follow the chosen
language too.

The application is called *YUCE PDF Düzenleyici* in the Turkish interface and
*YUCE PDF EDITOR* in the other languages. To force a language from the command
line:

```bash
PDFSTUDIO_LANG=en pdf-studio
```

### Adding or fixing a translation

The source language is Turkish: the `_("…")` strings in the code are also the
translation keys. Translations live in the `MESSAGES` dictionary in
`pdfstudio/locales/<language>.py`. After a change, run:

```bash
python packaging/check_translations.py
```

It reports missing translations and placeholder mismatches (`{0}`, `{name}`,
`{0:.0f}`) — a mismatched placeholder crashes the application when that message
is shown. CI runs this check on every build. To add a new language, add it to
the `LANGUAGES` dictionary in `pdfstudio/i18n.py` and create a catalog file with
the same structure.

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` / `Ctrl+S` / `Ctrl+Shift+S` | Open / Save / Save as |
| `Ctrl+Z` / `Ctrl+Y` | Undo / Redo |
| `Ctrl+F` / `F3` / `Shift+F3` | Find / next / previous result |
| `Ctrl+P` | Print |
| `Ctrl+Shift+P` | Print selected area |
| `Ctrl+=` / `Ctrl+-` / `Ctrl+0` | Zoom in / zoom out / 100% |
| `Ctrl+1` / `Ctrl+2` | Fit width / fit page |
| `Ctrl` + mouse wheel | Smooth zoom |
| `V` `H` `E` `T` | Select · Hand · Edit text · Add text |
| `D` `R` `L` `A` | Draw · Rectangle · Line · Arrow |
| `N` `S` `I` `K` `C` `M` | Note · Signature · Image · Link · Crop · Measure |
| `Ctrl+Shift+R` | Apply redactions |
| `Ctrl+Shift+←/→` | Rotate page |
| `F9` / `F10` / `F11` | Sidebar / properties / full screen |
| `Shift`+drag | Pan the page |
| Arrow keys | Move the selected object (`Shift` for fine steps) |
| `Esc` | Cancel selection / drawing |

---

## Project structure

```
pdfstudio/
├── app.py                 Application startup
├── i18n.py                Translation layer (_ / _n / N_, language choice, Qt translations)
├── locales/               Translation catalogs (en.py, pt_BR.py)
├── selftest.py            Built-in self-test (--self-test)
├── branding.py            Application name and technical identifiers
├── core/                  PDF engine (independent of the UI)
│   ├── document.py        Document model, snapshot-based undo/redo
│   ├── textedit.py        Text-block detection, in-place replacement, find/replace
│   ├── fonts.py           System font scanner (TTF name-table reader)
│   ├── annots.py          Annotations
│   ├── pageops.py         Page operations, watermark, page numbers
│   ├── images.py          Embedded images
│   ├── forms.py           Form fields
│   ├── security.py        Encryption, permissions, sanitizing
│   ├── exporting.py       Export, compression, OCR
│   └── renderer.py        Page rendering cache
└── ui/                    Qt interface
    ├── mainwindow.py      Menus, toolbars, all commands
    ├── pageview.py        Page canvas, tool interactions, coordinate transforms
    ├── inspector.py       Right panel (tool settings / object properties)
    ├── panels.py          Thumbnails, bookmarks, annotations, search, forms, images
    ├── dialogs.py         All dialogs
    ├── tools.py           Tool definitions
    ├── widgets.py         Shared widgets
    ├── icons.py           Vector icon set
    └── theme.py           Dark/light palette and stylesheet

packaging/                 Installer builds
├── pdfstudio.spec         PyInstaller configuration (Linux + Windows)
├── pdfstudio.iss          Inno Setup installer wizard
├── installer_header.sh    Start script of the Linux .run file
├── make_linux_installer.sh
├── arch/                  Arch/CachyOS package (PKGBUILD + build script)
├── check_translations.py  Translation checker (runs in CI)
├── set_version.py         Applies the version number everywhere
└── version_info.txt       Windows executable version info (generated)

.github/workflows/build.yml  Automated builds (Windows + Linux)
```

---

## Good to know

- **Text editing is limited by the nature of PDF.** PDF is a page-description
  format; there is no paragraph reflow as in a word processor. If you make a
  block longer, the text wraps inside its box and the font size shrinks if
  needed, but the blocks below do not move down on their own. Acrobat works
  under the same constraint.
- **Undo is snapshot-based** (30 steps by default). Memory use can grow with
  very large documents; adjust it with `limit` in `pdfstudio/core/history.py`.
- **Redaction is a one-way operation**: once applied and the document is saved,
  the content is really gone.
- The application is completely offline; no data is ever sent anywhere.

## License

The code is free to use. The licenses of the dependencies apply:
PyMuPDF **AGPL-3.0** (commercial use requires a commercial license from Artifex),
PySide6 **LGPL-3.0**.
