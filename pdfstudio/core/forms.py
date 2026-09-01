"""PDF form alanları: listeleme, doldurma, ekleme, dışa/içe aktarma."""
from __future__ import annotations

import json
from dataclasses import dataclass

import pymupdf

FIELD_TYPE_NAMES = {
    pymupdf.PDF_WIDGET_TYPE_BUTTON: "Düğme",
    pymupdf.PDF_WIDGET_TYPE_CHECKBOX: "Onay kutusu",
    pymupdf.PDF_WIDGET_TYPE_COMBOBOX: "Açılır liste",
    pymupdf.PDF_WIDGET_TYPE_LISTBOX: "Liste",
    pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON: "Seçenek düğmesi",
    pymupdf.PDF_WIDGET_TYPE_SIGNATURE: "İmza",
    pymupdf.PDF_WIDGET_TYPE_TEXT: "Metin kutusu",
}


@dataclass
class FieldInfo:
    pno: int
    xref: int
    name: str
    label: str
    type_id: int
    type_name: str
    value: str
    options: list
    rect: pymupdf.Rect
    readonly: bool
    required: bool


def has_form(document) -> bool:
    try:
        return bool(document.doc.is_form_pdf)
    except Exception:
        return False


def list_fields(document, pno: int | None = None) -> list[FieldInfo]:
    out: list[FieldInfo] = []
    rng = [pno] if pno is not None else range(document.page_count)
    for i in rng:
        try:
            page = document.page(i)
        except Exception:
            continue
        for w in page.widgets():
            flags = w.field_flags or 0
            out.append(FieldInfo(
                pno=i, xref=w.xref, name=w.field_name or "",
                label=w.field_label or w.field_name or "",
                type_id=w.field_type, type_name=FIELD_TYPE_NAMES.get(w.field_type, "Alan"),
                value="" if w.field_value is None else str(w.field_value),
                options=list(w.choice_values or []),
                rect=pymupdf.Rect(w.rect),
                readonly=bool(flags & 1), required=bool(flags & 2),
            ))
    return out


def field_at(document, pno: int, point):
    p = pymupdf.Point(point)
    for w in document.page(pno).widgets():
        if p in pymupdf.Rect(w.rect):
            return w
    return None


def set_value(document, pno: int, xref: int, value) -> bool:
    ok = False
    with document.edit("Form alanını doldur", pages=[pno]) as doc:
        for w in doc[pno].widgets():
            if w.xref != xref:
                continue
            if w.field_type == pymupdf.PDF_WIDGET_TYPE_CHECKBOX:
                w.field_value = bool(value)
            else:
                w.field_value = value
            w.update()
            ok = True
            break
    return ok


def set_values(document, values: dict[str, object]) -> int:
    """{alan_adı: değer} sözlüğüne göre toplu doldurma."""
    n = 0
    with document.edit("Formu doldur", structural=True) as doc:
        for pno in range(doc.page_count):
            for w in doc[pno].widgets():
                if w.field_name in values:
                    v = values[w.field_name]
                    if w.field_type == pymupdf.PDF_WIDGET_TYPE_CHECKBOX:
                        w.field_value = bool(v)
                    else:
                        w.field_value = v
                    w.update()
                    n += 1
    return n


def export_values(document) -> dict:
    return {f.name: f.value for f in list_fields(document) if f.name}


def export_json(document, path: str) -> str:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(export_values(document), fh, ensure_ascii=False, indent=2)
    return path


def import_json(document, path: str) -> int:
    with open(path, "r", encoding="utf-8") as fh:
        return set_values(document, json.load(fh))


def add_field(document, pno: int, rect, *, kind: str = "text", name: str = "alan",
              value: str = "", options: list | None = None, fontsize: float = 11,
              border_color=(0.4, 0.4, 0.4), fill_color=(0.96, 0.96, 1.0),
              text_color=(0, 0, 0), max_len: int = 0, multiline: bool = False) -> None:
    kinds = {
        "text": pymupdf.PDF_WIDGET_TYPE_TEXT,
        "checkbox": pymupdf.PDF_WIDGET_TYPE_CHECKBOX,
        "combobox": pymupdf.PDF_WIDGET_TYPE_COMBOBOX,
        "listbox": pymupdf.PDF_WIDGET_TYPE_LISTBOX,
        "radio": pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON,
        "signature": pymupdf.PDF_WIDGET_TYPE_SIGNATURE,
    }
    with document.edit("Form alanı ekle", pages=[pno]) as doc:
        w = pymupdf.Widget()
        w.rect = pymupdf.Rect(rect)
        w.field_type = kinds.get(kind, pymupdf.PDF_WIDGET_TYPE_TEXT)
        w.field_name = name
        w.field_value = value
        w.text_fontsize = fontsize
        w.text_color = text_color
        w.fill_color = fill_color
        w.border_color = border_color
        if options:
            w.choice_values = list(options)
        if max_len:
            w.text_maxlen = max_len
        if multiline:
            w.field_flags = (w.field_flags or 0) | 4096
        doc[pno].add_widget(w)


def delete_field(document, pno: int, xref: int) -> None:
    with document.edit("Form alanını sil", pages=[pno]) as doc:
        page = doc[pno]
        for a in list(page.annots(types=[pymupdf.PDF_ANNOT_WIDGET])):
            if a.xref == xref:
                page.delete_annot(a)
                break


def flatten_forms(document) -> None:
    with document.edit("Formu düzleştir", structural=True) as doc:
        doc.bake(annots=False, widgets=True)
