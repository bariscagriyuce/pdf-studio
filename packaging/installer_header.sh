#!/usr/bin/env bash
# ============================================================================
#  PDF Studio — kendi kendini açan Linux kurulum dosyası
#  Kullanım:
#     bash PDFStudio-VERSION-x86_64.run              (etkileşimli kurulum)
#     bash PDFStudio-VERSION-x86_64.run --uninstall  (kaldır)
#     bash PDFStudio-VERSION-x86_64.run --help
# ============================================================================
set -euo pipefail

APP_NAME="PDF Studio"
APP_ID="pdf-studio"
BIN_NAME="PDFStudio"
VERSION="__VERSION__"
PAYLOAD_SIZE="__PAYLOAD_SIZE__"

bold=$'\033[1m'; dim=$'\033[2m'; red=$'\033[31m'; grn=$'\033[32m'
ylw=$'\033[33m'; blu=$'\033[34m'; rst=$'\033[0m'

say()  { printf '%s\n' "$*"; }
ok()   { printf '%s✔%s %s\n' "$grn" "$rst" "$*"; }
warn() { printf '%s!%s %s\n' "$ylw" "$rst" "$*"; }
die()  { printf '%s✖%s %s\n' "$red" "$rst" "$*" >&2; exit 1; }

usage() {
    cat <<EOF
${bold}$APP_NAME $VERSION — kurulum${rst}

  bash $(basename "$0")                  Kur (yönetici isen sistem geneline,
                                         değilsen yalnızca kendi kullanıcına)
  bash $(basename "$0") --user           Zorla kullanıcı dizinine kur
  bash $(basename "$0") --system         Zorla sistem geneline kur (root gerekir)
  bash $(basename "$0") --prefix DIZIN   Belirtilen dizine kur
  bash $(basename "$0") --extract DIZIN  Kurmadan yalnızca dosyaları çıkar
  bash $(basename "$0") --uninstall      Kaldır
  bash $(basename "$0") --verify         Kurulumdan sonra kendi kendini sına
  bash $(basename "$0") --help           Bu yardım

Kurulum yerleri:
  Sistem  : /opt/$APP_ID          + /usr/share/applications
  Kullanıcı: ~/.local/opt/$APP_ID + ~/.local/share/applications
EOF
}

# ------------------------------------------------------------------ konumlar
setup_paths() {
    if [ -n "${PREFIX_OVERRIDE:-}" ]; then
        ROOT_DIR="$PREFIX_OVERRIDE"
        DESKTOP_DIR="$HOME/.local/share/applications"
        ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"
        BIN_DIR="$HOME/.local/bin"
        MODE="özel dizin"
    elif [ "$SCOPE" = "system" ]; then
        ROOT_DIR="/opt/$APP_ID"
        DESKTOP_DIR="/usr/share/applications"
        ICON_DIR="/usr/share/icons/hicolor/512x512/apps"
        BIN_DIR="/usr/local/bin"
        MODE="sistem geneli"
    else
        ROOT_DIR="$HOME/.local/opt/$APP_ID"
        DESKTOP_DIR="$HOME/.local/share/applications"
        ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"
        BIN_DIR="$HOME/.local/bin"
        MODE="yalnızca bu kullanıcı"
    fi
}

# ------------------------------------------------------------------ kaldırma
do_uninstall() {
    setup_paths
    local found=0
    for d in "/opt/$APP_ID" "$HOME/.local/opt/$APP_ID"; do
        if [ -d "$d" ]; then
            if [ -w "$(dirname "$d")" ] || [ "$(id -u)" = 0 ]; then
                rm -rf "$d" && ok "Silindi: $d" && found=1
            else
                warn "Yetki yok: $d  (sudo ile tekrar deneyin)"
            fi
        fi
    done
    for f in "/usr/share/applications/$APP_ID.desktop" \
             "$HOME/.local/share/applications/$APP_ID.desktop" \
             "/usr/share/icons/hicolor/512x512/apps/$APP_ID.png" \
             "$HOME/.local/share/icons/hicolor/512x512/apps/$APP_ID.png" \
             "/usr/local/bin/$APP_ID" "$HOME/.local/bin/$APP_ID"; do
        [ -e "$f" ] || [ -L "$f" ] || continue
        rm -f "$f" 2>/dev/null && ok "Silindi: $f" && found=1
    done
    command -v update-desktop-database >/dev/null 2>&1 && \
        update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    [ "$found" = 1 ] && say "" && ok "$APP_NAME kaldırıldı." || warn "Kurulu bir sürüm bulunamadı."
    say "${dim}Ayarlarınız ~/.config/PDFStudio ve ~/.cache/pdfstudio içinde durmaya devam eder.${rst}"
    exit 0
}

# ------------------------------------------------------------------ argümanlar
SCOPE=""; PREFIX_OVERRIDE=""; EXTRACT_ONLY=""; VERIFY=0
while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h) usage; exit 0 ;;
        --uninstall) do_uninstall ;;
        --user) SCOPE="user" ;;
        --system) SCOPE="system" ;;
        --prefix) PREFIX_OVERRIDE="${2:?--prefix bir dizin ister}"; shift ;;
        --extract) EXTRACT_ONLY="${2:?--extract bir dizin ister}"; shift ;;
        --verify) VERIFY=1 ;;
        *) die "Bilinmeyen seçenek: $1  (--help deneyin)" ;;
    esac
    shift
done
[ -n "$SCOPE" ] || { [ "$(id -u)" = 0 ] && SCOPE="system" || SCOPE="user"; }

# --------------------------------------------------------------- ön kontroller
say ""
say "${bold}${blu}  $APP_NAME $VERSION${rst}"
say "${dim}  Windows ve Linux için ayrıntılı PDF düzenleyici${rst}"
say ""

[ "$(uname -s)" = "Linux" ] || die "Bu kurulum yalnızca Linux içindir."
case "$(uname -m)" in
    x86_64|amd64) ;;
    *) die "Bu paket x86_64 içindir (bulunan: $(uname -m))." ;;
esac

for tool in tar xz; do
    command -v "$tool" >/dev/null 2>&1 || die "'$tool' komutu gerekli ama bulunamadı."
done

# glibc sürümü (paket manylinux_2_34 ile derlendi)
if command -v ldd >/dev/null 2>&1; then
    glibc="$(ldd --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+$' || true)"
    if [ -n "$glibc" ]; then
        major="${glibc%%.*}"; minor="${glibc##*.}"
        if [ "$major" -lt 2 ] || { [ "$major" -eq 2 ] && [ "$minor" -lt 34 ]; }; then
            warn "glibc $glibc bulundu; bu paket 2.34+ ister. Çalışmayabilir."
        fi
    fi
fi

# --------------------------------------------------------------- yalnızca çıkar
PAYLOAD_LINE=$(awk '/^__PAYLOAD_BELOW__$/ { print NR + 1; exit 0; }' "$0")
extract_to() {
    mkdir -p "$1"
    tail -n +"$PAYLOAD_LINE" "$0" | tar -xJf - -C "$1"
}

if [ -n "$EXTRACT_ONLY" ]; then
    say "Dosyalar çıkarılıyor → $EXTRACT_ONLY"
    extract_to "$EXTRACT_ONLY"
    ok "Bitti. Çalıştırmak için: $EXTRACT_ONLY/$BIN_NAME/$BIN_NAME"
    exit 0
fi

# ------------------------------------------------------------------- kurulum
setup_paths
say "  Kurulum türü : ${bold}$MODE${rst}"
say "  Hedef dizin  : $ROOT_DIR"
say "  Boyut        : ~$PAYLOAD_SIZE"
say ""

if [ "$SCOPE" = "system" ] && [ "$(id -u)" != 0 ]; then
    die "Sistem geneline kurulum için root gerekir:  sudo bash $(basename "$0") --system"
fi

if [ -t 0 ]; then
    printf "  Devam edilsin mi? [E/h] "
    read -r answer </dev/tty || answer="e"
    case "${answer:-e}" in
        [hHnN]*) say "Vazgeçildi."; exit 0 ;;
    esac
    say ""
fi

if [ -d "$ROOT_DIR" ]; then
    say "  Önceki sürüm kaldırılıyor…"
    rm -rf "$ROOT_DIR"
fi

say "  Dosyalar açılıyor (bu birkaç saniye sürebilir)…"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT
extract_to "$TMP_DIR"

mkdir -p "$(dirname "$ROOT_DIR")"
mv "$TMP_DIR/$BIN_NAME" "$ROOT_DIR"
chmod -R a+rX "$ROOT_DIR"
chmod +x "$ROOT_DIR/$BIN_NAME"
ok "Uygulama kuruldu: $ROOT_DIR"

# ---- ikon
mkdir -p "$ICON_DIR"
if [ -f "$ROOT_DIR/_internal/pdfstudio/resources/icon.png" ]; then
    cp "$ROOT_DIR/_internal/pdfstudio/resources/icon.png" "$ICON_DIR/$APP_ID.png"
    ok "İkon kuruldu"
fi

# ---- masaüstü kısayolu
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/$APP_ID.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Version=1.0
Name=PDF Studio
GenericName=PDF Düzenleyici
GenericName[en]=PDF Editor
Comment=PDF dosyalarını görüntüleyin ve ayrıntılı olarak düzenleyin
Comment[en]=View and edit PDF documents
Exec=$ROOT_DIR/$BIN_NAME %f
Icon=$APP_ID
Terminal=false
Categories=Office;Viewer;Publishing;
MimeType=application/pdf;
Keywords=pdf;editor;düzenle;belge;annotate;
StartupNotify=true
StartupWMClass=PDFStudio
DESKTOP
chmod 644 "$DESKTOP_DIR/$APP_ID.desktop"
ok "Menü kısayolu oluşturuldu"

# ---- komut satırı bağlantısı
mkdir -p "$BIN_DIR"
ln -sf "$ROOT_DIR/$BIN_NAME" "$BIN_DIR/$APP_ID"
ok "Komut oluşturuldu: $BIN_DIR/$APP_ID"

# ---- masaüstü veritabanlarını tazele
command -v update-desktop-database >/dev/null 2>&1 && \
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && \
    gtk-update-icon-cache -f -t "$(dirname "$(dirname "$(dirname "$ICON_DIR")")")" 2>/dev/null || true

# ---- doğrulama
if [ "$VERIFY" = 1 ]; then
    say ""
    say "  Kendi kendini sınama çalıştırılıyor…"
    if "$ROOT_DIR/$BIN_NAME" --self-test >/dev/null 2>&1; then
        ok "Sınama başarılı"
    else
        warn "Sınama başarısız — ayrıntı için: $ROOT_DIR/$BIN_NAME --self-test"
    fi
fi

say ""
ok "${bold}Kurulum tamamlandı.${rst}"
say ""
say "  Başlatmak için:"
say "    • Uygulama menüsünde ${bold}PDF Studio${rst} arayın"
say "    • veya terminalde: ${bold}$APP_ID${rst}"
say "    • veya bir PDF'e sağ tıklayıp ${bold}Birlikte aç → PDF Studio${rst}"
if ! printf '%s' ":$PATH:" | grep -q ":$BIN_DIR:"; then
    say ""
    warn "$BIN_DIR PATH içinde değil. Şunu ~/.bashrc veya ~/.config/fish/config.fish"
    warn "dosyanıza ekleyebilirsiniz:  export PATH=\"\$PATH:$BIN_DIR\""
fi
say ""
say "  Kaldırmak için: ${dim}bash $(basename "$0") --uninstall${rst}"
say ""
exit 0

__PAYLOAD_BELOW__
