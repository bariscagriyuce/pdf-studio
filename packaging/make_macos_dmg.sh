#!/usr/bin/env bash
# macOS .app paketini sürükle-bırak kurulumlu bir .dmg dosyasına dönüştürür.
#
#   bash packaging/make_macos_dmg.sh "dist/YUCE PDF EDITOR.app" YUCE-PDF-Editor-1.2.0-macOS-arm64.dmg
#
# Uygulama, Apple geliştirici sertifikası olmadan "ad-hoc" imzalanır. Apple
# Silicon'da imzasız kod hiç çalışmaz; ad-hoc imza bunu çözer. Notarize
# edilmediği için ilk açılışta Gatekeeper uyarısı çıkar (bkz. README).
#
# MACOS_SIGN_IDENTITY ortam değişkeni verilirse (ör. "Developer ID Application: …")
# ad-hoc yerine o kimlikle, hardened runtime açık olarak imzalanır.
set -euo pipefail

APP="${1:?Kullanım: $0 <.app yolu> <çıktı.dmg>}"
OUT="${2:?Kullanım: $0 <.app yolu> <çıktı.dmg>}"
VOLNAME="YUCE PDF EDITOR"

[ -d "$APP" ] || { echo "Bulunamadı: $APP" >&2; exit 1; }

IDENTITY="${MACOS_SIGN_IDENTITY:--}"
echo "→ İmzalanıyor (${IDENTITY/#-/ad-hoc})…"
# İndirme sırasında eklenen öznitelikler imzayı bozar
xattr -cr "$APP"
if [ "$IDENTITY" = "-" ]; then
    codesign --force --deep --sign - "$APP"
else
    codesign --force --deep --options runtime --timestamp --sign "$IDENTITY" "$APP"
fi
codesign --verify --deep --strict "$APP"
echo "  imza doğrulandı ✔"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"

rm -f "$OUT"
echo "→ DMG oluşturuluyor…"
hdiutil create -volname "$VOLNAME" -srcfolder "$STAGE" -fs HFS+ \
    -format UDZO -imagekey zlib-level=9 -ov "$OUT" >/dev/null
hdiutil verify "$OUT" >/dev/null
echo "✔ $OUT ($(du -h "$OUT" | cut -f1))"
