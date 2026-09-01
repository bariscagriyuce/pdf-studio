#!/usr/bin/env bash
# PyInstaller çıktısından Arch Linux paketi (.pkg.tar.zst) üretir.
#   bash packaging/arch/build-arch-package.sh <dist/PDFStudio> [sürüm]
set -euo pipefail

DIST_DIR="${1:?PyInstaller çıktı dizini gerekli (ör. dist/PDFStudio)}"
VERSION="${2:-1.0.0}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
OUT_DIR="${OUT_DIR:-$ROOT}"

command -v makepkg >/dev/null || { echo "makepkg gerekli (Arch/CachyOS)"; exit 1; }
[ -d "$DIST_DIR" ] || { echo "Dizin yok: $DIST_DIR"; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "→ Kaynaklar hazırlanıyor…"
tar -C "$(dirname "$DIST_DIR")" -cf - "$(basename "$DIST_DIR")" \
    | zstd -19 -T0 -q -o "$WORK/PDFStudio-dist.tar.zst"

cp "$ROOT/pdfstudio/resources/icon.png" "$WORK/pdf-studio.png"
cp "$ROOT/packaging/LICENSE-notice.txt" "$WORK/LICENSE-notice.txt"

cat > "$WORK/pdf-studio.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Version=1.0
Name=PDF Studio
GenericName=PDF Düzenleyici
GenericName[en]=PDF Editor
Comment=PDF dosyalarını görüntüleyin ve ayrıntılı olarak düzenleyin
Comment[en]=View and edit PDF documents
Exec=/opt/pdf-studio/PDFStudio %f
Icon=pdf-studio
Terminal=false
Categories=Office;Viewer;Publishing;
MimeType=application/pdf;
Keywords=pdf;editor;düzenle;belge;annotate;
StartupNotify=true
StartupWMClass=PDFStudio
DESKTOP

sed "s/__VERSION__/$VERSION/" "$HERE/PKGBUILD.in" > "$WORK/PKGBUILD"

echo "→ Paket derleniyor (makepkg)…"
( cd "$WORK" && makepkg --noconfirm --nodeps --skipinteg --clean )

PKG="$(find "$WORK" -maxdepth 1 -name '*.pkg.tar.zst' | head -1)"
[ -n "$PKG" ] || { echo "Paket üretilemedi"; exit 1; }
mv "$PKG" "$OUT_DIR/"
FINAL="$OUT_DIR/$(basename "$PKG")"
echo
echo "✔ Hazır: $FINAL  ($(du -h "$FINAL" | cut -f1))"
echo "  Kurmak için : sudo pacman -U \"$FINAL\""
echo "  Kaldırmak   : sudo pacman -R pdf-studio"
