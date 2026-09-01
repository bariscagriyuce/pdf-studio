#!/usr/bin/env bash
# PyInstaller çıktısından tek dosyalık .run kurulum dosyası üretir.
#   bash packaging/make_linux_installer.sh <dist/PDFStudio dizini> <çıktı.run> [sürüm]
set -euo pipefail

DIST_DIR="${1:?PyInstaller çıktı dizini gerekli (ör. dist/PDFStudio)}"
OUT="${2:?çıktı dosyası gerekli (ör. PDFStudio-1.0-x86_64.run)}"
VERSION="${3:-1.0}"
HERE="$(cd "$(dirname "$0")" && pwd)"

[ -d "$DIST_DIR" ] || { echo "Dizin yok: $DIST_DIR" >&2; exit 1; }
[ -x "$DIST_DIR/PDFStudio" ] || chmod +x "$DIST_DIR/PDFStudio" 2>/dev/null || true

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "→ Arşiv oluşturuluyor (xz -9, biraz sürer)…"
tar -C "$(dirname "$DIST_DIR")" -cf - "$(basename "$DIST_DIR")" \
    | XZ_OPT="-9 -T0" xz -c > "$TMP/payload.tar.xz"

SIZE="$(du -h "$TMP/payload.tar.xz" | cut -f1)"
echo "→ Sıkıştırılmış boyut: $SIZE"

sed -e "s/__VERSION__/$VERSION/g" -e "s/__PAYLOAD_SIZE__/$SIZE/g" \
    "$HERE/installer_header.sh" > "$TMP/header.sh"

cat "$TMP/header.sh" "$TMP/payload.tar.xz" > "$OUT"
chmod +x "$OUT" 2>/dev/null || true

echo "✔ Hazır: $OUT  ($(du -h "$OUT" | cut -f1))"
