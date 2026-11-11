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


@dataclass
class NupOptions:
    rows: int = 1
    cols: int = 1
    order: str = LRTB
    gap_mm: float = 0.0       # hücreler arası boşluk
    border: bool = False      # her sayfanın çevresine ince çerçeve
    autorotate: bool = True   # sayfa hücreye yan yatarak daha iyi sığıyorsa döndür

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
            autorotate=bool(self.autorotate),
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict | None) -> "NupOptions":
        d = d or {}
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
                autorotate: bool = True) -> tuple[float, float, float, float, bool]:
    """Sayfayı en-boy oranını koruyarak hücreye ortalar.

    Döner: (x, y, gen, yük, döndür_mü). ``döndür_mü`` doğruysa dönen genişlik ve
    yükseklik, sayfa 90° döndürüldükten sonraki kâğıt üzerindeki ölçülerdir.
    """
    cx, cy, cw, ch = cell
    if page_w <= 0 or page_h <= 0 or cw <= 0 or ch <= 0:
        return cx, cy, 0.0, 0.0, False
    s = min(cw / page_w, ch / page_h)
    rotate = False
    if autorotate:
        s_rot = min(cw / page_h, ch / page_w)
        if s_rot > s * 1.001:
            s, rotate = s_rot, True
    w, h = (page_h * s, page_w * s) if rotate else (page_w * s, page_h * s)
    return cx + (cw - w) / 2, cy + (ch - h) / 2, w, h, rotate


def sheets(pages: list[int], per_sheet: int) -> list[list[int]]:
    """Sayfa listesini kâğıtlara böler."""
    per_sheet = max(1, per_sheet)
    return [pages[i:i + per_sheet] for i in range(0, len(pages), per_sheet)]
