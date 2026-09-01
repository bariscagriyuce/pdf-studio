"""Sayfa tuvali: görüntüleme, yakınlaştırma, seçim ve araç etkileşimleri."""
from __future__ import annotations

import pymupdf
from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView

from ..core import textedit as te
from ..core.renderer import PageRenderer
from .tools import LINE_TOOLS, MARKUP_TOOLS, RECT_TOOLS, Tool, ToolSettings

PAGE_GAP = 16.0
MARGIN = 24.0
HANDLE = 7.0

LAYOUT_SINGLE = "tek"
LAYOUT_CONTINUOUS = "sürekli"
LAYOUT_FACING = "çift"
LAYOUT_FACING_COVER = "çift-kapak"


def qcolor(rgb, alpha: float = 1.0) -> QColor:
    c = QColor.fromRgbF(float(rgb[0]), float(rgb[1]), float(rgb[2]))
    c.setAlphaF(alpha)
    return c


class PageItem(QGraphicsItem):
    """Tek bir PDF sayfasını çizen öğe."""

    def __init__(self, view: "PageView", pno: int):
        super().__init__()
        self.view = view
        self.pno = pno
        self._w = 1.0
        self._h = 1.0
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption, True)

    def set_size(self, w: float, h: float) -> None:
        if (w, h) != (self._w, self._h):
            self.prepareGeometryChange()
            self._w, self._h = w, h

    def boundingRect(self) -> QRectF:
        return QRectF(-3, -3, self._w + 6, self._h + 9)

    # ------------------------------------------------------------------ çizim
    def paint(self, painter: QPainter, option, widget=None):
        p = self.view.palette_colors
        rect = QRectF(0, 0, self._w, self._h)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(p["page_shadow"]))
        painter.drawRoundedRect(rect.translated(0, 3), 3, 3)
        painter.setBrush(QColor("#ffffff"))
        painter.drawRect(rect)

        img = self.view.renderer.image(self.pno, self.view.zoom, dpr=self.view.render_dpr)
        painter.drawImage(rect, img)

        painter.setPen(QPen(QColor(p["line"]), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(rect)

        self._paint_overlays(painter)

        if self.view.show_page_labels:
            painter.setPen(QColor(p["dim"]))
            f = QFont()
            f.setPointSizeF(8.5)
            painter.setFont(f)
            painter.drawText(QRectF(0, self._h + 1, self._w, 12), Qt.AlignHCenter,
                             f"{self.pno + 1}")

    def _paint_overlays(self, painter: QPainter):
        v = self.view
        z = v.zoom
        painter.setRenderHint(QPainter.Antialiasing, True)

        # arama sonuçları
        for pno, r in v.search_hits:
            if pno != self.pno:
                continue
            qr = v.pdf_rect_to_item(self.pno, r)
            is_current = v.current_hit is not None and v.search_hits[v.current_hit] == (pno, r)
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 190, 40, 190) if is_current else QColor(90, 160, 255, 110))
            painter.drawRect(qr)

        # metin seçimi
        if v.selection_page == self.pno:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(v.palette_colors["accent"]).lighter(120))
            painter.setOpacity(0.30)
            for quad in v.selection_quads:
                painter.drawRect(v.pdf_rect_to_item(self.pno, quad.rect))
            painter.setOpacity(1.0)

        # metin düzenleme kılavuzları
        if v.tool == Tool.TEXT_EDIT and v.show_text_boxes:
            painter.setPen(QPen(QColor(v.palette_colors["accent"]), 1, Qt.DotLine))
            painter.setBrush(Qt.NoBrush)
            for blk in v.blocks_for(self.pno):
                painter.drawRect(v.pdf_rect_to_item(self.pno, blk.bbox))
        if v.hover_page == self.pno and v.hover_rect is not None:
            painter.setPen(QPen(QColor(v.palette_colors["accent"]), 1.6))
            painter.setBrush(QColor(v.palette_colors["accent"]).lighter(160))
            painter.setOpacity(0.18)
            painter.drawRect(v.hover_rect)
            painter.setOpacity(1.0)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(v.palette_colors["accent"]), 1.6))
            painter.drawRect(v.hover_rect)

        # bekleyen karartmalar
        for pno, r in v.pending_redactions:
            if pno != self.pno:
                continue
            qr = v.pdf_rect_to_item(self.pno, r)
            painter.setPen(QPen(QColor("#e5484d"), 1.5, Qt.DashLine))
            painter.setBrush(QColor(229, 72, 77, 60))
            painter.drawRect(qr)

        # seçili açıklama / görüntü
        if v.selected_object and v.selected_object[0] == self.pno:
            r = v.pdf_rect_to_item(self.pno, v.selected_object[2])
            painter.setPen(QPen(QColor(v.palette_colors["accent"]), 1.5, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(r)
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.setBrush(QColor(v.palette_colors["accent"]))
            for h in v.handle_rects(r):
                painter.drawRect(h)

        # sürüklenen önizleme
        if v.preview_page == self.pno and v.preview is not None:
            kind, data = v.preview
            pen = QPen(qcolor(v.settings.color), max(1.0, v.settings.width * z))
            painter.setPen(pen)
            painter.setBrush(qcolor(v.settings.fill) if v.settings.fill else Qt.NoBrush)
            if kind == "rect":
                painter.drawRect(data)
            elif kind == "ellipse":
                painter.drawEllipse(data)
            elif kind == "line":
                painter.drawLine(data[0], data[1])
            elif kind == "arrow":
                painter.drawLine(data[0], data[1])
                self._arrow_head(painter, data[0], data[1])
            elif kind == "measure":
                painter.setPen(QPen(QColor(v.palette_colors["accent"]), 1.4, Qt.DashLine))
                painter.drawLine(data[0], data[1])
            elif kind == "ink":
                path = QPainterPath()
                for stroke in data:
                    if len(stroke) < 2:
                        continue
                    path.moveTo(stroke[0])
                    for pt in stroke[1:]:
                        path.lineTo(pt)
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(path)
            elif kind == "polygon":
                if len(data) > 1:
                    path = QPainterPath(data[0])
                    for pt in data[1:]:
                        path.lineTo(pt)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPath(path)
            elif kind == "dashed":
                painter.setPen(QPen(QColor(v.palette_colors["accent"]), 1.6, Qt.DashLine))
                painter.setBrush(QColor(79, 140, 255, 40))
                painter.drawRect(data)

    @staticmethod
    def _arrow_head(painter: QPainter, p0: QPointF, p1: QPointF):
        import math
        ang = math.atan2(p1.y() - p0.y(), p1.x() - p0.x())
        size = 11.0
        for delta in (2.6, -2.6):
            painter.drawLine(p1, QPointF(p1.x() + size * math.cos(ang + delta),
                                         p1.y() + size * math.sin(ang + delta)))


class PageView(QGraphicsView):
    """Belgenin tüm sayfalarını gösteren ana tuval."""

    pageChanged = Signal(int)
    zoomChanged = Signal(float)
    statusMessage = Signal(str)
    editTextRequested = Signal(int, object, str, object)   # pno, rect, text, style
    objectSelected = Signal(object)                        # (pno, kind, rect, ref) | None
    rectToolFinished = Signal(object, object)              # Tool, (pno, pymupdf.Rect)
    lineToolFinished = Signal(object, object)              # Tool, (pno, p0, p1)
    pointToolFinished = Signal(object, object)             # Tool, (pno, point)
    inkFinished = Signal(int, object)
    polygonFinished = Signal(int, object)
    selectionChanged = Signal(int, object)                 # pno, quads
    contextRequested = Signal(int, object, object)         # pno, pdf point, global pos

    def __init__(self, document, palette_colors: dict, parent=None):
        super().__init__(parent)
        self.document = document
        self.palette_colors = palette_colors
        self.renderer = PageRenderer(document)
        self.settings = ToolSettings()

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.setBackgroundBrush(QColor(palette_colors["canvas"]))
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        self.items: list[PageItem] = []
        self.zoom = 1.0
        self.fit_mode = "width"
        self.layout_mode = LAYOUT_CONTINUOUS
        self.current_page = 0
        self.show_page_labels = True
        self.show_text_boxes = True
        self.render_dpr = float(self.devicePixelRatioF() or 1.0)

        self.tool = Tool.SELECT
        self._drag_start: QPointF | None = None
        self._drag_page = -1
        self._panning = False
        self._pan_origin = QPointF()
        self._ink_strokes: list[list[QPointF]] = []
        self._polygon_points: list[QPointF] = []
        self._moving_object = False
        self._resize_handle = -1
        self._object_origin = None

        self.preview = None
        self.preview_page = -1
        self.selection_quads: list[pymupdf.Quad] = []
        self.selection_page = -1
        self.search_hits: list[tuple[int, pymupdf.Rect]] = []
        self.current_hit: int | None = None
        self.pending_redactions: list[tuple[int, pymupdf.Rect]] = []
        self.hover_rect: QRectF | None = None
        self.hover_page = -1
        self.selected_object = None  # (pno, kind, pymupdf.Rect, ref)

        self._block_cache: dict[tuple, list] = {}
        self._scroll_timer = QTimer(self)
        self._scroll_timer.setSingleShot(True)
        self._scroll_timer.setInterval(60)
        self._scroll_timer.timeout.connect(self._update_current_page)
        self.verticalScrollBar().valueChanged.connect(lambda _: self._scroll_timer.start())

        document.structureChanged.connect(self.reload)
        document.pagesChanged.connect(self.refresh_pages)

    # -------------------------------------------------------------- yerleşim
    def reload(self) -> None:
        keep = self.current_page
        self._scene.clear()
        self.items = []
        self.renderer.clear()
        self._block_cache.clear()
        self.clear_transient()
        if not self.document.is_open:
            self._scene.setSceneRect(0, 0, 10, 10)
            return
        for pno in range(self.document.page_count):
            item = PageItem(self, pno)
            self._scene.addItem(item)
            self.items.append(item)
        self.relayout()
        self.goto_page(min(keep, self.document.page_count - 1), center=False)

    def refresh_pages(self, pages: list[int]) -> None:
        for pno in pages:
            self.renderer.invalidate_page(pno)
            for key in [k for k in self._block_cache if k[1] == pno]:
                self._block_cache.pop(key, None)
        self.relayout()
        self.viewport().update()

    def clear_transient(self) -> None:
        self.preview = None
        self.preview_page = -1
        self.selection_quads = []
        self.selection_page = -1
        self.hover_rect = None
        self.hover_page = -1
        self.selected_object = None
        self._ink_strokes = []
        self._polygon_points = []

    def _rows(self) -> list[list[int]]:
        n = self.document.page_count
        if self.layout_mode in (LAYOUT_SINGLE, LAYOUT_CONTINUOUS):
            return [[i] for i in range(n)]
        if self.layout_mode == LAYOUT_FACING_COVER:
            rows = [[0]] if n else []
            for i in range(1, n, 2):
                rows.append([i] if i + 1 >= n else [i, i + 1])
            return rows
        rows = []
        for i in range(0, n, 2):
            rows.append([i] if i + 1 >= n else [i, i + 1])
        return rows

    def relayout(self) -> None:
        if not self.document.is_open or not self.items:
            return
        rows = self._rows()
        self._row_of = {}
        for ri, row in enumerate(rows):
            for pno in row:
                self._row_of[pno] = ri
        self._rows_cache = rows

        single = self.layout_mode == LAYOUT_SINGLE
        visible_row = self._row_of.get(self.current_page, 0)

        sizes = {}
        for pno in range(self.document.page_count):
            w, h = self.document.page_size(pno)
            sizes[pno] = (w * self.zoom, h * self.zoom)

        max_row_w = 0.0
        for row in rows:
            rw = sum(sizes[p][0] for p in row) + PAGE_GAP * (len(row) - 1)
            max_row_w = max(max_row_w, rw)
        total_w = max_row_w + MARGIN * 2

        y = MARGIN
        for ri, row in enumerate(rows):
            row_w = sum(sizes[p][0] for p in row) + PAGE_GAP * (len(row) - 1)
            row_h = max(sizes[p][1] for p in row)
            x = (total_w - row_w) / 2
            show = (not single) or ri == visible_row
            for pno in row:
                item = self.items[pno]
                w, h = sizes[pno]
                item.set_size(w, h)
                item.setPos(x, y if show else -100000)
                item.setVisible(show)
                x += w + PAGE_GAP
            if show:
                y += row_h + PAGE_GAP + (14 if self.show_page_labels else 0)
        height = y + MARGIN - PAGE_GAP
        self._scene.setSceneRect(0, 0, total_w, max(height, 10))

    # ------------------------------------------------------------ yakınlaştırma
    def set_zoom(self, value: float, anchor_center: bool = True) -> None:
        value = max(0.08, min(12.0, float(value)))
        if abs(value - self.zoom) < 1e-4:
            return
        vp = self.viewport().rect()
        old_center = self.mapToScene(vp.center())
        ratio = value / self.zoom
        self.zoom = value
        self.fit_mode = "none"
        self.relayout()
        if anchor_center:
            self.centerOn(old_center * ratio)
        self.viewport().update()
        self.zoomChanged.emit(self.zoom)

    def zoom_in(self) -> None:
        self.set_zoom(self.zoom * 1.20)

    def zoom_out(self) -> None:
        self.set_zoom(self.zoom / 1.20)

    def fit(self, mode: str) -> None:
        if not self.document.is_open:
            return
        pno = self.current_page
        w, h = self.document.page_size(pno)
        avail_w = max(80, self.viewport().width() - int(MARGIN * 2) - 18)
        avail_h = max(80, self.viewport().height() - int(MARGIN * 2) - 18)
        cols = 2 if self.layout_mode in (LAYOUT_FACING, LAYOUT_FACING_COVER) else 1
        if cols == 2:
            avail_w = (avail_w - PAGE_GAP) / 2
        if mode == "width":
            z = avail_w / w
        elif mode == "page":
            z = min(avail_w / w, avail_h / h)
        elif mode == "height":
            z = avail_h / h
        else:
            return
        self.zoom = max(0.08, min(12.0, z))
        self.fit_mode = mode
        self.relayout()
        self.goto_page(pno, center=(mode == "page"))
        self.center_horizontally(pno)
        self.viewport().update()
        self.zoomChanged.emit(self.zoom)

    def center_horizontally(self, pno: int) -> None:
        """Farklı genişlikteki sayfalarda görünümü sayfaya ortalar."""
        if not (0 <= pno < len(self.items)):
            return
        item = self.items[pno]
        cx = item.pos().x() + item.boundingRect().width() / 2
        bar = self.horizontalScrollBar()
        bar.setValue(int(cx - self.viewport().width() / 2))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.fit_mode in ("width", "page", "height"):
            QTimer.singleShot(0, lambda: self.fit(self.fit_mode))

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta:
                pos = event.position().toPoint()
                before = self.mapToScene(pos)
                old_zoom = self.zoom
                self.set_zoom(self.zoom * (1.15 if delta > 0 else 1 / 1.15),
                              anchor_center=False)
                ratio = self.zoom / old_zoom
                # imlecin altındaki belge noktası yerinde kalsın
                target = before * ratio
                current = self.mapToScene(pos)
                diff = target - current
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() + int(round(diff.x())))
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() + int(round(diff.y())))
            event.accept()
            return
        super().wheelEvent(event)

    # ------------------------------------------------------------- gezinme
    def goto_page(self, pno: int, center: bool = True) -> None:
        if not self.document.is_open:
            return
        pno = max(0, min(self.document.page_count - 1, pno))
        self.current_page = pno
        if self.layout_mode == LAYOUT_SINGLE:
            self.relayout()
            self.verticalScrollBar().setValue(0)
        else:
            item = self.items[pno]
            if center:
                self.centerOn(item.pos() + QPointF(item.boundingRect().width() / 2,
                                                   item.boundingRect().height() / 2))
            else:
                self.verticalScrollBar().setValue(int(item.pos().y() - MARGIN / 2))
            if self._page_widths_differ():
                self.center_horizontally(pno)
        self.pageChanged.emit(pno)
        self.viewport().update()

    def _page_widths_differ(self) -> bool:
        if not self.document.is_open or self.document.page_count < 2:
            return False
        first = round(self.document.page_size(0)[0], 1)
        for pno in range(1, min(self.document.page_count, 40)):
            if round(self.document.page_size(pno)[0], 1) != first:
                return True
        return False

    def _update_current_page(self) -> None:
        if not self.items or self.layout_mode == LAYOUT_SINGLE:
            return
        top = self.mapToScene(0, int(self.viewport().height() * 0.35)).y()
        best, best_d = self.current_page, None
        for item in self.items:
            if not item.isVisible():
                continue
            d = abs(item.pos().y() - top)
            if best_d is None or d < best_d:
                best, best_d = item.pno, d
        if best != self.current_page:
            self.current_page = best
            self.pageChanged.emit(best)

    def next_page(self):
        self.goto_page(self.current_page + 1, center=False)

    def prev_page(self):
        self.goto_page(self.current_page - 1, center=False)

    def set_layout_mode(self, mode: str) -> None:
        self.layout_mode = mode
        self.relayout()
        self.goto_page(self.current_page, center=False)
        if self.fit_mode in ("width", "page", "height"):
            self.fit(self.fit_mode)

    # --------------------------------------------------------- koordinatlar
    def page_object(self, pno: int) -> pymupdf.Page:
        return self.document.page(pno)

    def item_to_pdf(self, pno: int, pt: QPointF) -> pymupdf.Point:
        p = pymupdf.Point(pt.x() / self.zoom, pt.y() / self.zoom)
        return p * self.page_object(pno).derotation_matrix

    def pdf_to_item(self, pno: int, p) -> QPointF:
        q = pymupdf.Point(p) * self.page_object(pno).rotation_matrix
        return QPointF(q.x * self.zoom, q.y * self.zoom)

    def item_rect_to_pdf(self, pno: int, rect: QRectF) -> pymupdf.Rect:
        a = self.item_to_pdf(pno, rect.topLeft())
        b = self.item_to_pdf(pno, rect.bottomRight())
        r = pymupdf.Rect(min(a.x, b.x), min(a.y, b.y), max(a.x, b.x), max(a.y, b.y))
        return r

    def pdf_rect_to_item(self, pno: int, r) -> QRectF:
        a = self.pdf_to_item(pno, pymupdf.Point(r.x0, r.y0))
        b = self.pdf_to_item(pno, pymupdf.Point(r.x1, r.y1))
        return QRectF(min(a.x(), b.x()), min(a.y(), b.y()),
                      abs(b.x() - a.x()), abs(b.y() - a.y()))

    def page_at(self, scene_pos: QPointF) -> tuple[int, QPointF] | None:
        for item in self.items:
            if not item.isVisible():
                continue
            local = item.mapFromScene(scene_pos)
            if QRectF(0, 0, item.boundingRect().width() - 6,
                      item.boundingRect().height() - 9).contains(local):
                return item.pno, local
        return None

    def nearest_page(self, scene_pos: QPointF) -> tuple[int, QPointF]:
        hit = self.page_at(scene_pos)
        if hit:
            return hit
        item = self.items[self.current_page]
        return item.pno, item.mapFromScene(scene_pos)

    # ------------------------------------------------------------ yardımcılar
    def blocks_for(self, pno: int) -> list:
        key = (self.document.version, pno)
        cached = self._block_cache.get(key)
        if cached is None:
            try:
                cached = te.text_blocks(self.document.page(pno))
            except Exception:
                cached = []
            if len(self._block_cache) > 40:
                self._block_cache.clear()
            self._block_cache[key] = cached
        return cached

    def handle_rects(self, r: QRectF) -> list[QRectF]:
        h = HANDLE
        cx, cy = r.center().x(), r.center().y()
        pts = [(r.left(), r.top()), (cx, r.top()), (r.right(), r.top()),
               (r.right(), cy), (r.right(), r.bottom()), (cx, r.bottom()),
               (r.left(), r.bottom()), (r.left(), cy)]
        return [QRectF(x - h / 2, y - h / 2, h, h) for x, y in pts]

    def set_tool(self, tool: Tool) -> None:
        self.tool = tool
        self.selection_quads = []
        self.selection_page = -1
        self.hover_rect = None
        self._polygon_points = []
        self.selected_object = None
        self.objectSelected.emit(None)
        cursors = {
            Tool.PAN: Qt.OpenHandCursor,
            Tool.SELECT: Qt.ArrowCursor,
            Tool.TEXT_EDIT: Qt.IBeamCursor,
            Tool.INK: Qt.CrossCursor,
            Tool.ERASER: Qt.PointingHandCursor,
        }
        self.viewport().setCursor(cursors.get(tool, Qt.CrossCursor))
        self.viewport().update()

    def set_search_hits(self, hits, current=None) -> None:
        self.search_hits = list(hits)
        self.current_hit = current
        self.viewport().update()

    def goto_hit(self, index: int) -> None:
        if not self.search_hits:
            return
        index %= len(self.search_hits)
        self.current_hit = index
        pno, r = self.search_hits[index]
        self.goto_page(pno, center=False)
        item = self.items[pno]
        qr = self.pdf_rect_to_item(pno, r)
        self.centerOn(item.mapToScene(qr.center()))
        self.viewport().update()

    def clear_pending_redactions(self) -> None:
        self.pending_redactions = []
        self.viewport().update()

    def selected_text(self) -> str:
        if self.selection_page < 0 or not self.selection_quads:
            return ""
        page = self.document.page(self.selection_page)
        parts = []
        for quad in self.selection_quads:
            parts.append(page.get_textbox(quad.rect).strip())
        return " ".join(x for x in parts if x)

    # -------------------------------------------------------------- olaylar
    def mousePressEvent(self, event):
        if not self.document.is_open:
            return super().mousePressEvent(event)
        scene_pos = self.mapToScene(event.position().toPoint())
        hit = self.page_at(scene_pos)

        if event.button() == Qt.MiddleButton or self.tool == Tool.PAN or \
                (event.modifiers() & Qt.ShiftModifier and event.button() == Qt.LeftButton
                 and self.tool == Tool.SELECT):
            self._panning = True
            self._pan_origin = event.position()
            self.viewport().setCursor(Qt.ClosedHandCursor)
            event.accept()
            return

        if event.button() == Qt.RightButton:
            if hit:
                pno, local = hit
                self.contextRequested.emit(pno, self.item_to_pdf(pno, local),
                                           event.globalPosition().toPoint())
            event.accept()
            return

        if event.button() != Qt.LeftButton or not hit:
            return super().mousePressEvent(event)

        pno, local = hit
        self._drag_page = pno
        self._drag_start = local
        self.current_page = pno

        if self.tool == Tool.SELECT:
            self._press_select(pno, local)
        elif self.tool == Tool.TEXT_EDIT:
            self._press_text_edit(pno, local)
        elif self.tool == Tool.INK:
            self._ink_strokes = [[local]]
            self.preview = ("ink", self._ink_strokes)
            self.preview_page = pno
        elif self.tool == Tool.POLYGON:
            if self.preview_page != pno:
                self._polygon_points = []
            self._polygon_points.append(local)
            self.preview = ("polygon", self._polygon_points)
            self.preview_page = pno
        elif self.tool == Tool.NOTE:
            self.pointToolFinished.emit(Tool.NOTE, (pno, self.item_to_pdf(pno, local)))
        elif self.tool == Tool.ERASER:
            self.pointToolFinished.emit(Tool.ERASER, (pno, self.item_to_pdf(pno, local)))
        elif self.tool in MARKUP_TOOLS:
            self.selection_page = pno
            self.selection_quads = []
        self.viewport().update()
        event.accept()

    def _press_select(self, pno: int, local: QPointF):
        # önce seçili nesnenin tutamacına mı basıldı?
        if self.selected_object and self.selected_object[0] == pno:
            r = self.pdf_rect_to_item(pno, self.selected_object[2])
            for i, h in enumerate(self.handle_rects(r)):
                if h.contains(local):
                    self._resize_handle = i
                    self._object_origin = QRectF(r)
                    return
            if r.contains(local):
                self._moving_object = True
                self._object_origin = QRectF(r)
                return
        obj = self._object_at(pno, local)
        self.selected_object = obj
        self._moving_object = obj is not None
        self._resize_handle = -1
        if obj:
            self._object_origin = self.pdf_rect_to_item(pno, obj[2])
        self.objectSelected.emit(obj)
        if obj is None:
            self.selection_page = pno
            self.selection_quads = []

    def _object_at(self, pno: int, local: QPointF):
        pdf_pt = self.item_to_pdf(pno, local)
        from ..core import annots as an
        from ..core import forms as fm
        from ..core import images as im
        page = self.document.page(pno)
        w = fm.field_at(self.document, pno, pdf_pt)
        if w is not None:
            return (pno, "widget", pymupdf.Rect(w.rect), w.xref)
        a = an.annot_at(page, pdf_pt)
        if a is not None:
            return (pno, "annot", pymupdf.Rect(a.rect), a.xref)
        img = im.image_at(self.document, pno, pdf_pt)
        if img is not None:
            return (pno, "image", pymupdf.Rect(img.rect), img.xref)
        return None

    def _press_text_edit(self, pno: int, local: QPointF):
        pdf_pt = self.item_to_pdf(pno, local)
        blk = None
        for b in self.blocks_for(pno):
            if pymupdf.Point(pdf_pt) in b.bbox:
                if blk is None or b.bbox.get_area() < blk.bbox.get_area():
                    blk = b
        if blk is None:
            self.statusMessage.emit("Bu noktada düzenlenebilir metin bulunamadı.")
            return
        self.editTextRequested.emit(pno, blk.bbox, blk.text, blk.style)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.position() - self._pan_origin
            self._pan_origin = event.position()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x()))
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y()))
            event.accept()
            return

        if not self.document.is_open:
            return super().mouseMoveEvent(event)

        scene_pos = self.mapToScene(event.position().toPoint())
        hit = self.page_at(scene_pos)

        if hit and not (event.buttons() & Qt.LeftButton):
            self._hover(hit[0], hit[1])

        if not (event.buttons() & Qt.LeftButton) or self._drag_start is None:
            return super().mouseMoveEvent(event)

        pno = self._drag_page
        item = self.items[pno]
        local = item.mapFromScene(scene_pos)

        if self.tool == Tool.SELECT and self.selected_object:
            self._drag_object(local)
        elif self.tool == Tool.SELECT:
            self._update_text_selection(pno, self._drag_start, local)
        elif self.tool in MARKUP_TOOLS:
            self._update_text_selection(pno, self._drag_start, local)
        elif self.tool == Tool.INK and self._ink_strokes:
            self._ink_strokes[-1].append(local)
            self.preview = ("ink", self._ink_strokes)
            self.preview_page = pno
        elif self.tool in RECT_TOOLS:
            r = QRectF(self._drag_start, local).normalized()
            kind = "ellipse" if self.tool == Tool.ELLIPSE else (
                "rect" if self.tool == Tool.RECT else "dashed")
            self.preview = (kind, r)
            self.preview_page = pno
        elif self.tool in LINE_TOOLS:
            kind = "measure" if self.tool == Tool.MEASURE else (
                "arrow" if self.tool == Tool.ARROW else "line")
            self.preview = (kind, (self._drag_start, local))
            self.preview_page = pno
            if self.tool == Tool.MEASURE:
                p0 = self.item_to_pdf(pno, self._drag_start)
                p1 = self.item_to_pdf(pno, local)
                dist = ((p1.x - p0.x) ** 2 + (p1.y - p0.y) ** 2) ** 0.5
                self.statusMessage.emit(
                    f"Uzunluk: {dist:.1f} pt  •  {dist / 72 * 25.4:.1f} mm  •  {dist / 72:.2f} inç")
        self.viewport().update()
        event.accept()

    def _hover(self, pno: int, local: QPointF):
        old = (self.hover_page, self.hover_rect)
        self.hover_page = pno
        self.hover_rect = None
        if self.tool == Tool.TEXT_EDIT:
            pdf_pt = self.item_to_pdf(pno, local)
            for b in self.blocks_for(pno):
                if pymupdf.Point(pdf_pt) in b.bbox:
                    self.hover_rect = self.pdf_rect_to_item(pno, b.bbox)
                    break
        elif self.tool == Tool.SELECT:
            obj = self._object_at(pno, local)
            if obj:
                self.hover_rect = self.pdf_rect_to_item(pno, obj[2])
        if old != (self.hover_page, self.hover_rect):
            self.viewport().update()

    def _update_text_selection(self, pno: int, a: QPointF, b: QPointF):
        page = self.document.page(pno)
        p0 = self.item_to_pdf(pno, a)
        p1 = self.item_to_pdf(pno, b)
        self.selection_page = pno
        try:
            self.selection_quads = te.selection_quads(page, (p0.x, p0.y), (p1.x, p1.y))
        except Exception:
            self.selection_quads = []

    def _drag_object(self, local: QPointF):
        if not self.selected_object or self._object_origin is None:
            return
        pno, kind, _rect, ref = self.selected_object
        start = self._drag_start
        dx, dy = local.x() - start.x(), local.y() - start.y()
        r = QRectF(self._object_origin)
        if self._resize_handle >= 0:
            h = self._resize_handle
            if h in (0, 6, 7):
                r.setLeft(r.left() + dx)
            if h in (2, 3, 4):
                r.setRight(r.right() + dx)
            if h in (0, 1, 2):
                r.setTop(r.top() + dy)
            if h in (4, 5, 6):
                r.setBottom(r.bottom() + dy)
            r = r.normalized()
            if r.width() < 6 or r.height() < 6:
                return
        elif self._moving_object:
            r.translate(dx, dy)
        else:
            return
        self.selected_object = (pno, kind, self.item_rect_to_pdf(pno, r), ref)
        self.viewport().update()

    def mouseReleaseEvent(self, event):
        if self._panning:
            self._panning = False
            self.viewport().setCursor(
                Qt.OpenHandCursor if self.tool == Tool.PAN else Qt.ArrowCursor)
            event.accept()
            return
        if not self.document.is_open or self._drag_start is None:
            return super().mouseReleaseEvent(event)

        pno = self._drag_page
        item = self.items[pno] if 0 <= pno < len(self.items) else None
        local = item.mapFromScene(self.mapToScene(event.position().toPoint())) if item else None
        start = self._drag_start
        self._drag_start = None

        try:
            if self.tool == Tool.SELECT and self.selected_object and \
                    (self._moving_object or self._resize_handle >= 0):
                if self._object_origin is not None and local is not None and \
                        (abs(local.x() - start.x()) > 1.5 or abs(local.y() - start.y()) > 1.5):
                    self.objectSelected.emit(self.selected_object)
                    self.rectToolFinished.emit(
                        Tool.SELECT, (pno, self.selected_object[2]))
            elif self.tool == Tool.SELECT:
                self.selectionChanged.emit(self.selection_page, self.selection_quads)
            elif self.tool in MARKUP_TOOLS:
                if self.selection_quads:
                    self.selectionChanged.emit(self.selection_page, self.selection_quads)
            elif self.tool == Tool.INK:
                strokes = []
                for stroke in self._ink_strokes:
                    pts = [self.item_to_pdf(pno, p) for p in stroke]
                    strokes.append([(p.x, p.y) for p in pts])
                self._ink_strokes = []
                self.inkFinished.emit(pno, strokes)
            elif self.tool in RECT_TOOLS and local is not None:
                r = QRectF(start, local).normalized()
                if r.width() > 3 and r.height() > 3:
                    self.rectToolFinished.emit(self.tool, (pno, self.item_rect_to_pdf(pno, r)))
            elif self.tool in LINE_TOOLS and local is not None:
                if self.tool != Tool.MEASURE:
                    p0 = self.item_to_pdf(pno, start)
                    p1 = self.item_to_pdf(pno, local)
                    self.lineToolFinished.emit(self.tool,
                                               (pno, (p0.x, p0.y), (p1.x, p1.y)))
        finally:
            self._moving_object = False
            self._resize_handle = -1
            if self.tool != Tool.POLYGON:
                self.preview = None
                self.preview_page = -1
            self.viewport().update()
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if not self.document.is_open:
            return super().mouseDoubleClickEvent(event)
        scene_pos = self.mapToScene(event.position().toPoint())
        hit = self.page_at(scene_pos)
        if not hit:
            return super().mouseDoubleClickEvent(event)
        pno, local = hit
        if self.tool == Tool.POLYGON and self._polygon_points:
            pts = [self.item_to_pdf(pno, p) for p in self._polygon_points]
            self._polygon_points = []
            self.preview = None
            self.preview_page = -1
            self.polygonFinished.emit(pno, [(p.x, p.y) for p in pts])
        elif self.tool in (Tool.SELECT, Tool.TEXT_EDIT):
            self._press_text_edit(pno, local)
        event.accept()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self._polygon_points = []
            self.preview = None
            self.selection_quads = []
            self.selected_object = None
            self.objectSelected.emit(None)
            self.viewport().update()
            return
        if key in (Qt.Key_PageDown, Qt.Key_Space) and self.layout_mode == LAYOUT_SINGLE:
            self.next_page()
            return
        if key == Qt.Key_PageUp and self.layout_mode == LAYOUT_SINGLE:
            self.prev_page()
            return
        if self.selected_object and key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            step = 1.0 if event.modifiers() & Qt.ShiftModifier else 4.0
            dx = -step if key == Qt.Key_Left else (step if key == Qt.Key_Right else 0)
            dy = -step if key == Qt.Key_Up else (step if key == Qt.Key_Down else 0)
            pno, kind, r, ref = self.selected_object
            nr = pymupdf.Rect(r.x0 + dx, r.y0 + dy, r.x1 + dx, r.y1 + dy)
            self.selected_object = (pno, kind, nr, ref)
            self.rectToolFinished.emit(Tool.SELECT, (pno, nr))
            return
        super().keyPressEvent(event)

    def set_palette_colors(self, colors: dict) -> None:
        self.palette_colors = colors
        self.setBackgroundBrush(QColor(colors["canvas"]))
        self.viewport().update()
