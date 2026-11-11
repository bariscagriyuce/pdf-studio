"""Güncelleme denetimi — Qt'ye bağlı olmayan kısım.

Yeni sürümler GitHub Releases'ten gelir: CI, ``v1.2.3`` etiketi gönderildiğinde
kurulum dosyalarını derleyip oraya yükler. Uygulama en son sürümü sorar,
kendi sürümüyle karşılaştırır ve çalıştığı kurulum türüne uygun dosyayı seçer.
Ağ ve arayüz işleri ``ui/updater.py`` içindedir.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

from ..branding import APP_ID, GITHUB_REPO

LATEST_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE = f"https://github.com/{GITHUB_REPO}/releases/latest"
CHECKSUMS_NAME = "SHA256SUMS.txt"
CHECK_INTERVAL_S = 24 * 3600     # otomatik denetim en çok günde bir

# Kurulum türleri
SOURCE = "source"                # kaynak koddan çalışıyor (geliştirme)
WIN_SETUP = "win-setup"          # Windows kurulum sihirbazıyla kurulmuş
WIN_PORTABLE = "win-portable"    # Windows taşınabilir exe
MAC_APP = "mac-app"              # macOS .app paketi
LINUX_PACMAN = "linux-pacman"    # Arch paketi (pacman)
LINUX_RUN_USER = "linux-run-user"      # .run → ~/.local/opt
LINUX_RUN_SYSTEM = "linux-run-system"  # .run → /opt (root)
OTHER = "other"                  # tanınmayan yer: yalnızca sayfayı aç

#: Kendiliğinden kurulabilen türler (diğerlerinde indirme sayfası açılır)
AUTO_INSTALL = {WIN_SETUP, MAC_APP, LINUX_PACMAN, LINUX_RUN_USER, LINUX_RUN_SYSTEM}


def parse_version(text: str) -> tuple[int, ...]:
    """'v1.4.0' → (1, 4, 0). Sayı olmayan ekler (-beta vb.) yok sayılır."""
    m = re.match(r"\s*[vV]?(\d+(?:\.\d+)*)", text or "")
    if not m:
        return ()
    parts = [int(p) for p in m.group(1).split(".")]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    a, b = parse_version(latest), parse_version(current)
    return bool(a) and a > b


@dataclass
class Asset:
    name: str
    url: str
    size: int = 0


@dataclass
class Release:
    version: str
    tag: str
    notes: str
    page_url: str
    assets: list[Asset] = field(default_factory=list)

    def asset(self, name: str) -> Asset | None:
        return next((a for a in self.assets if a.name == name), None)


def parse_release(data: dict) -> Release | None:
    """GitHub API yanıtını (releases/latest) okur. Taslak ya da ön sürüm yok sayılır."""
    if not isinstance(data, dict) or data.get("draft") or data.get("prerelease"):
        return None
    tag = str(data.get("tag_name") or "")
    if not parse_version(tag):
        return None
    assets = [Asset(str(a.get("name", "")), str(a.get("browser_download_url", "")),
                    int(a.get("size") or 0))
              for a in data.get("assets") or [] if a.get("browser_download_url")]
    return Release(version=tag.lstrip("vV"), tag=tag, notes=str(data.get("body") or ""),
                   page_url=str(data.get("html_url") or RELEASES_PAGE), assets=assets)


# ------------------------------------------------------------ kurulum türü
def _pacman_owns(path: str) -> bool:
    if not shutil.which("pacman"):
        return False
    try:
        r = subprocess.run(["pacman", "-Qqo", path], capture_output=True, text=True,
                           timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and r.stdout.strip() == APP_ID


def mac_bundle_path(executable: str) -> str | None:
    """…/YUCE PDF EDITOR.app/Contents/MacOS/PDFStudio → …/YUCE PDF EDITOR.app"""
    p = os.path.abspath(executable)
    marker = ".app" + os.sep + "Contents" + os.sep + "MacOS"
    i = p.find(marker)
    return p[:i + 4] if i >= 0 else None


def install_kind(executable: str | None = None, frozen: bool | None = None,
                 platform: str | None = None) -> str:
    """Uygulamanın nasıl kurulduğunu bulur."""
    frozen = getattr(sys, "frozen", False) if frozen is None else frozen
    platform = platform or sys.platform
    executable = executable or sys.executable
    if not frozen:
        return SOURCE
    exe_dir = os.path.dirname(os.path.abspath(executable))
    if platform.startswith("win"):
        try:
            names = os.listdir(exe_dir)
        except OSError:
            names = []
        if any(re.match(r"unins\d+\.exe$", n, re.I) for n in names):
            return WIN_SETUP
        return WIN_PORTABLE
    if platform == "darwin":
        return MAC_APP if mac_bundle_path(executable) else OTHER
    if platform.startswith("linux"):
        if exe_dir == f"/opt/{APP_ID}":
            return LINUX_PACMAN if _pacman_owns(executable) else LINUX_RUN_SYSTEM
        if exe_dir == os.path.expanduser(f"~/.local/opt/{APP_ID}"):
            return LINUX_RUN_USER
    return OTHER


def pick_asset(release: Release, kind: str, machine: str | None = None) -> Asset | None:
    """Bu kurulum türü için indirilecek dosya (yoksa None → sayfayı aç)."""
    import platform as _pf
    machine = (machine or _pf.machine() or "").lower()
    v = release.version

    def ends(suffix: str) -> Asset | None:
        return next((a for a in release.assets if a.name.endswith(suffix)), None)

    if kind == WIN_SETUP:
        return ends(f"{v}-Setup.exe")
    if kind == MAC_APP:
        arch = "arm64" if machine in ("arm64", "aarch64") else "x86_64"
        return ends(f"{v}-macOS-{arch}.dmg")
    if kind == LINUX_PACMAN:
        return next((a for a in release.assets
                     if a.name.startswith(f"{APP_ID}-{v}-") and a.name.endswith(".pkg.tar.zst")),
                    None)
    if kind in (LINUX_RUN_USER, LINUX_RUN_SYSTEM):
        return ends(f"{v}-x86_64.run")
    return None


# ----------------------------------------------------------------- doğrulama
def parse_checksums(text: str) -> dict[str, str]:
    """sha256sum çıktısı → {dosya_adı: özet}"""
    out = {}
    for line in (text or "").splitlines():
        parts = line.strip().split()
        if len(parts) >= 2 and re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]):
            out[parts[-1].lstrip("*")] = parts[0].lower()
    return out


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------- macOS değiştirici
MAC_REPLACE_SCRIPT = r"""#!/bin/bash
# Uygulama kapanınca .app paketini .dmg içindekiyle değiştirir ve yeniden açar.
pid="$1"; dmg="$2"; app="$3"
for _ in $(seq 1 600); do kill -0 "$pid" 2>/dev/null || break; sleep 0.2; done
mnt="$(mktemp -d /tmp/pdfstudio-update.XXXXXX)"
if hdiutil attach -nobrowse -readonly -quiet -mountpoint "$mnt" "$dmg"; then
    src="$(find "$mnt" -maxdepth 1 -name '*.app' -type d | head -1)"
    if [ -n "$src" ]; then
        rm -rf "$app.new"
        if ditto "$src" "$app.new"; then
            rm -rf "$app.old"
            mv "$app" "$app.old" && mv "$app.new" "$app" && rm -rf "$app.old"
            [ -d "$app" ] || mv "$app.old" "$app"
        fi
    fi
    hdiutil detach -quiet "$mnt" || hdiutil detach -force -quiet "$mnt"
fi
rmdir "$mnt" 2>/dev/null
open "$app"
"""
