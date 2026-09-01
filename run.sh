#!/usr/bin/env bash
# PDF Studio — Linux/macOS başlatıcı.
# İlk çalıştırmada sanal ortamı kurar, sonrakilerde doğrudan açar.
set -e
cd "$(dirname "$0")"

PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || { echo "python3 bulunamadı. Lütfen Python 3.9+ kurun."; exit 1; }

VENV=".venv"
VPY="$VENV/bin/python"

if [ ! -f "$VPY" ]; then
    echo "Sanal ortam oluşturuluyor…"
    "$PY" -m venv --system-site-packages "$VENV"
fi

if ! "$VPY" -c "import PySide6, pymupdf" >/dev/null 2>&1; then
    echo "Bağımlılıklar kuruluyor…"
    "$VPY" -m pip install --upgrade pip
    "$VPY" -m pip install -r requirements.txt
fi

exec "$VPY" -m pdfstudio "$@"
