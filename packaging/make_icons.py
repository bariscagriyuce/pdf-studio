#!/usr/bin/env python3
"""Uygulama ikonlarını üretir: icon.png (512) ve çok boyutlu icon.ico.

Windows kabuğu ve Inno Setup, ikonun birden çok boyut içermesini bekler;
tek boyutlu bir ICO küçük yerlerde bulanık görünür. ImageMagick'in ICO
desteği her sistemde bulunmadığı için ICO kabı burada elle yazılır.

    python packaging/make_icons.py
"""
from __future__ import annotations

import os
import struct

from PySide6.QtCore import QBuffer, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QImage, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QApplication

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_DIR = os.path.join(ROOT, "pdfstudio", "resources")

# BMP olarak yazılacak boyutlar (küçük ikonlar için en uyumlu biçim)
BMP_SIZES = [16, 24, 32, 48, 64]
# PNG olarak yazılacak boyutlar (Vista+ standardı, dosyayı küçük tutar)
PNG_SIZES = [128, 256]


def draw(size: int) -> QPixmap:
    """Belge + kalem simgesini verilen boyutta çizer."""
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)

    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor("#3f7bf0"))
    grad.setColorAt(1, QColor("#2a4fd0"))
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(grad))
    p.drawRoundedRect(QRectF(size * 0.04, size * 0.04, size * 0.92, size * 0.92),
                      size * 0.18, size * 0.18)

    p.setBrush(QColor("#ffffff"))
    p.drawRoundedRect(QRectF(size * 0.26, size * 0.20, size * 0.48, size * 0.60),
                      size * 0.05, size * 0.05)

    # Küçük boyutlarda satır çizgileri lekeye dönüşüyor; sadeleştir
    lines = 4 if size >= 48 else (3 if size >= 32 else 0)
    p.setBrush(QColor("#c9d6f5"))
    for i in range(lines):
        step = 0.10 if lines == 4 else 0.13
        p.drawRoundedRect(
            QRectF(size * 0.33, size * (0.30 + i * step), size * 0.34, size * 0.045),
            size * 0.02, size * 0.02)

    p.setBrush(QColor("#f5a524"))
    p.save()
    p.translate(size * 0.66, size * 0.70)
    p.rotate(-45)
    p.drawRoundedRect(QRectF(0, 0, size * 0.10, size * 0.34), size * 0.03, size * 0.03)
    p.setBrush(QColor("#2b3040"))
    p.drawRect(QRectF(0, size * 0.34, size * 0.10, size * 0.05))
    p.restore()
    p.end()
    return px


def png_bytes(px: QPixmap) -> bytes:
    buf = QBuffer()
    buf.open(QBuffer.WriteOnly)
    px.toImage().save(buf, "PNG")
    return bytes(buf.data())


def bmp_bytes(px: QPixmap) -> bytes:
    """32bpp BGRA DIB + AND maskesi (ICO içi klasik biçim)."""
    img = px.toImage().convertToFormat(QImage.Format_ARGB32)
    w, h = img.width(), img.height()

    header = struct.pack(
        "<IiiHHIIiiII",
        40,        # biSize
        w,         # biWidth
        h * 2,     # biHeight — XOR + AND maskesi birlikte
        1,         # biPlanes
        32,        # biBitCount
        0,         # biCompression = BI_RGB
        0, 0, 0, 0, 0,
    )

    # XOR verisi: alttan üste, BGRA
    rows = []
    for y in range(h - 1, -1, -1):
        row = bytearray()
        for x in range(w):
            c = img.pixelColor(x, y)
            row += bytes((c.blue(), c.green(), c.red(), c.alpha()))
        rows.append(bytes(row))
    xor_data = b"".join(rows)

    # AND maskesi: 1bpp, satırlar 4 bayta hizalı, tamamı 0 (alfa kanalı kullanılıyor)
    mask_row = ((w + 31) // 32) * 4
    and_data = b"\x00" * (mask_row * h)

    return header + xor_data + and_data


def build_ico(path: str) -> None:
    entries: list[tuple[int, bytes, bool]] = []
    for size in sorted(set(BMP_SIZES)):
        entries.append((size, bmp_bytes(draw(size)), False))
    for size in sorted(set(PNG_SIZES)):
        entries.append((size, png_bytes(draw(size)), True))

    count = len(entries)
    offset = 6 + count * 16
    directory = b""
    payload = b""
    for size, data, _is_png in entries:
        directory += struct.pack(
            "<BBBBHHII",
            0 if size >= 256 else size,   # genişlik (256 → 0)
            0 if size >= 256 else size,   # yükseklik
            0,                            # renk sayısı
            0,                            # ayrılmış
            1,                            # düzlem
            32,                           # bit derinliği
            len(data),
            offset,
        )
        payload += data
        offset += len(data)

    with open(path, "wb") as fh:
        fh.write(struct.pack("<HHH", 0, 1, count) + directory + payload)


def main() -> int:
    QApplication.instance() or QApplication([])  # QPixmap için gerekli
    os.makedirs(OUT_DIR, exist_ok=True)

    png_path = os.path.join(OUT_DIR, "icon.png")
    draw(512).save(png_path)
    print(f"OK: {png_path}")

    ico_path = os.path.join(OUT_DIR, "icon.ico")
    build_ico(ico_path)
    print(f"OK: {ico_path} ({os.path.getsize(ico_path) / 1024:.0f} KB, "
          f"{len(BMP_SIZES) + len(PNG_SIZES)} sizes)")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    raise SystemExit(main())
