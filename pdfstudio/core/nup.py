"""Bir kâğıda birden çok sayfa yerleştirme (N-up) hesapları.

Sistem yazdırma iletişim kutusu yalnızca sabit seçenekler (1, 2, 4, 6, 9, 16)
sunar; burada satır × sütun serbestçe seçilir ve yerleşimi uygulama kendisi
çizer. Tüm ölçüler aynı birimdedir (çağıran ne verirse o: nokta ya da piksel).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

# Sayfaların hücrelere diziliş sırası
LRTB = "lrtb"   # soldan sağa, sonra aşağı
RLTB = "rltb"   # sağdan sola, sonra aşağı
TBLR = "tblr"   # yukarıdan aşağı, sonra sağa
TBRL = "tbrl"   # yukarıdan aşağı, sonra sola
ORDERS = (LRTB, RLTB, TBLR, TBRL)

MAX_CELLS = 20   # satır ya da sütun için üst sınır

# Sayfanın hücre içindeki yönü
ROT_AUTO = "auto"            # hangisi daha büyük sığıyorsa (0° ya da 90°)
ROTATIONS = (ROT_AUTO, "0", "90", "270", "180")

# Kâğıt yönü
PAPER_PRINTER = "printer"    # yazıcı ayarında ne seçiliyse
PAPER_PORTRAIT = "portrait"
PAPER_LANDSCAPE = "landscape"
PAPERS = (PAPER_PRINTER, PAPER_PORTRAIT, PAPER_LANDSCAPE)


@dataclass
class NupOptions:
    rows: int = 1
    cols: int = 1
    order: str = LRTB
    gap_mm: float = 0.0       # hücreler arası boşluk
    border: bool = False      # her sayfanın çevresine ince çerçeve
    rotation: str = ROT_AUTO  # sayfa yönü: auto / 0 / 90 / 180 / 270 (saat yönünde)
    paper: str = PAPER_PRINTER  # kâğıt yönü

    @property
    def per_sheet(self) -> int:
        return self.rows * self.cols

    @property
    def is_single(self) -> bool:
        return self.per_sheet == 1

    def normalized(self) -> "NupOptions":
        return NupOptions(
            rows=min(MAX_CELLS, max(1, int(self.rows))),
            cols=min(MAX_CELLS, max(1, int(self.cols))),
            order=self.order if self.order in ORDERS else LRTB,
            gap_mm=max(0.0, float(self.gap_mm)),
            border=bool(self.border),
            rotation=str(self.rotation) if str(self.rotation) in ROTATIONS else ROT_AUTO,
            paper=self.paper if self.paper in PAPERS else PAPER_PRINTER,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict | None) -> "NupOptions":
        d = dict(d or {})
        if "rotation" not in d and "autorotate" in d:      # 1.4.x ayarları
            d["rotation"] = ROT_AUTO if d["autorotate"] else "0"
        known = {k: d[k] for k in cls.__dataclass_fields__ if k in d}
        try:
            return cls(**known).normalized()
        except (TypeError, ValueError):
            return cls()


def cell_position(index: int, rows: int, cols: int, order: str = LRTB) -> tuple[int, int]:
    """Kâğıttaki ``index``. sayfanın (satır, sütun) konumu."""
    if order in (TBLR, TBRL):
        r, c = index % rows, index // rows
        if order == TBRL:
            c = cols - 1 - c
    else:
        r, c = index // cols, index % cols
        if order == RLTB:
            c = cols - 1 - c
    return r, c


def cell_rects(width: float, height: float, rows: int, cols: int,
               gap: float = 0.0) -> list[list[tuple[float, float, float, float]]]:
    """Alanı eşit hücrelere böler → rects[satır][sütun] = (x, y, gen, yük)."""
    gap_x = gap if cols > 1 else 0.0
    gap_y = gap if rows > 1 else 0.0
    cw = max(0.0, (width - gap_x * (cols - 1)) / cols)
    ch = max(0.0, (height - gap_y * (rows - 1)) / rows)
    return [[(c * (cw + gap_x), r * (ch + gap_y), cw, ch) for c in range(cols)]
            for r in range(rows)]


def fit_in_cell(page_w: float, page_h: float, cell: tuple[float, float, float, float],
                rotation: str | int = ROT_AUTO) -> tuple[float, float, float, float, int]:
    """Sayfayı en-boy oranını koruyarak hücreye ortalar.

    Döner: (x, y, gen, yük, açı). ``açı`` saat yönünde 0/90/180/270'tir;
    genişlik ve yükseklik, sayfa döndürüldükten sonra kâğıt üzerindeki
    ölçülerdir.
    """
    cx, cy, cw, ch = cell
    if page_w <= 0 or page_h <= 0 or cw <= 0 or ch <= 0:
        return cx, cy, 0.0, 0.0, 0
    if str(rotation) == ROT_AUTO:
        s0 = min(cw / page_w, ch / page_h)
        s90 = min(cw / page_h, ch / page_w)
        angle = 90 if s90 > s0 * 1.001 else 0
    else:
        try:
            angle = int(rotation) % 360
        except (TypeError, ValueError):
            angle = 0
        if angle not in (0, 90, 180, 270):
            angle = 0
    sideways = angle in (90, 270)
    pw, ph = (page_h, page_w) if sideways else (page_w, page_h)
    s = min(cw / pw, ch / ph)
    w, h = pw * s, ph * s
    return cx + (cw - w) / 2, cy + (ch - h) / 2, w, h, angle


def sheets(pages: list[int], per_sheet: int) -> list[list[int]]:
    """Sayfa listesini kâğıtlara böler."""
    per_sheet = max(1, per_sheet)
    return [pages[i:i + per_sheet] for i in range(0, len(pages), per_sheet)]
