#!/usr/bin/env bash
# macOS .app paketini imzalar ve sürükle-bırak kurulumlu bir .dmg dosyasına dönüştürür.
#
#   bash packaging/make_macos_dmg.sh "dist/YUCE PDF EDITOR.app" YUCE-PDF-Editor-1.3.0-macOS-arm64.dmg
#
# İmza (ortam değişkenleri):
#   MACOS_SIGN_IDENTITY   "Developer ID Application: …" → hardened runtime ile imzalar.
#                         Verilmezse "ad-hoc" imza (Apple Silicon'da imzasız kod çalışmaz).
#
# Notarization (Apple onayı; yalnızca Developer ID ile). Biri yeterli:
#   MACOS_NOTARY_PROFILE  `xcrun notarytool store-credentials` ile kaydedilmiş profil adı (yerel)
#   MACOS_NOTARY_APPLE_ID + MACOS_NOTARY_PASSWORD + MACOS_NOTARY_TEAM_ID   (CI)
# Notarize edilen .dmg'ye bilet "zımbalanır" (staple); Gatekeeper uyarısı çıkmaz.
set -euo pipefail

APP="${1:?Kullanım: $0 <.app yolu> <çıktı.dmg>}"
OUT="${2:?Kullanım: $0 <.app yolu> <çıktı.dmg>}"
VOLNAME="YUCE PDF EDITOR"
HERE="$(cd "$(dirname "$0")" && pwd)"
ENTITLEMENTS="$HERE/macos-entitlements.plist"

[ -d "$APP" ] || { echo "Bulunamadı: $APP" >&2; exit 1; }

IDENTITY="${MACOS_SIGN_IDENTITY:--}"
# İndirme sırasında eklenen öznitelikler imzayı bozar
xattr -cr "$APP"

if [ "$IDENTITY" = "-" ]; then
    echo "→ İmzalanıyor (ad-hoc)…"
    codesign --force --deep --sign - "$APP"
else
    echo "→ İmzalanıyor: $IDENTITY"
    SIGN=(codesign --force --timestamp --options runtime --sign "$IDENTITY")
    # İçten dışa: önce paketteki tüm Mach-O ikilileri (dylib, .so, framework
    # ikilileri), en son ana çalıştırılabilir ve paketin kendisi. --deep Apple
    # tarafından önerilmiyor ve iç içe framework'lerde imzayı eksik bırakabiliyor.
    count=0
    while IFS= read -r -d '' f; do
        if file -b "$f" | grep -q "Mach-O"; then
            "${SIGN[@]}" "$f" >/dev/null 2>&1 || "${SIGN[@]}" "$f"
            count=$((count + 1))
        fi
    done < <(find "$APP/Contents" -type f ! -path "$APP/Contents/MacOS/*" -print0)
    # Framework paketlerinin kendisi (Versions/A) — ikililer imzalandıktan sonra
    while IFS= read -r -d '' fw; do
        "${SIGN[@]}" "$fw" >/dev/null
    done < <(find "$APP/Contents" -type d -name "*.framework" -print0 | sort -rz)
    echo "  $count ikili imzalandı"
    "${SIGN[@]}" --entitlements "$ENTITLEMENTS" "$APP/Contents/MacOS/"*
    "${SIGN[@]}" --entitlements "$ENTITLEMENTS" "$APP"
fi
codesign --verify --deep --strict "$APP"
echo "  imza doğrulandı ✔"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"

rm -f "$OUT"
echo "→ DMG oluşturuluyor…"
# GitHub'ın macOS makinelerinde hdiutil ara sıra "Resource busy" ile düşüyor;
# birkaç kez yeniden denenir. Hata çıktısı gizlenmez (yalnızca kullanımdan
# kaldırılma uyarısı süzülür).
ok=0
for attempt in 1 2 3 4 5; do
    if hdiutil create -volname "$VOLNAME" -srcfolder "$STAGE" -fs HFS+ \
            -format UDZO -imagekey zlib-level=9 -ov "$OUT" 2>&1 \
            | grep -v "is deprecated" >&2; [ "${PIPESTATUS[0]}" -eq 0 ]; then
        ok=1; break
    fi
    echo "  hdiutil başarısız (deneme $attempt/5), yeniden deneniyor…" >&2
    sleep $((attempt * 5))
done
[ "$ok" = 1 ] || { echo "✖ DMG oluşturulamadı" >&2; exit 1; }
hdiutil verify "$OUT" 2>&1 | grep -v "is deprecated" | tail -1

if [ "$IDENTITY" != "-" ]; then
    codesign --force --timestamp --sign "$IDENTITY" "$OUT"

    NOTARY=()
    if [ -n "${MACOS_NOTARY_PROFILE:-}" ]; then
        NOTARY=(--keychain-profile "$MACOS_NOTARY_PROFILE")
    elif [ -n "${MACOS_NOTARY_APPLE_ID:-}" ] && [ -n "${MACOS_NOTARY_PASSWORD:-}" ]; then
        NOTARY=(--apple-id "$MACOS_NOTARY_APPLE_ID" --password "$MACOS_NOTARY_PASSWORD"
                --team-id "${MACOS_NOTARY_TEAM_ID:?MACOS_NOTARY_TEAM_ID gerekli}")
    fi

    if [ ${#NOTARY[@]} -gt 0 ]; then
        echo "→ Apple'a onaya gönderiliyor (notarization, birkaç dakika sürebilir)…"
        RESULT="$(xcrun notarytool submit "$OUT" "${NOTARY[@]}" --wait --output-format json)"
        echo "$RESULT"
        STATUS="$(printf '%s' "$RESULT" | /usr/bin/python3 -c 'import json,sys; print(json.load(sys.stdin).get("status",""))')"
        if [ "$STATUS" != "Accepted" ]; then
            ID="$(printf '%s' "$RESULT" | /usr/bin/python3 -c 'import json,sys; print(json.load(sys.stdin).get("id",""))')"
            echo "✖ Notarization reddedildi ($STATUS). Ayrıntı:" >&2
            [ -n "$ID" ] && xcrun notarytool log "$ID" "${NOTARY[@]}" >&2 || true
            exit 1
        fi
        xcrun stapler staple "$OUT"
        xcrun stapler validate "$OUT"
        spctl --assess --type open --context context:primary-signature -v "$OUT"
        echo "  Apple onayı alındı ve zımbalandı ✔"
    else
        echo "! Notarization bilgisi yok — DMG imzalı ama Apple onaylı değil."
    fi
fi

echo "✔ $OUT ($(du -h "$OUT" | cut -f1))"
