# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
PDF processing service.

Wraps PyMuPDF (fitz) operations for form field listing, form filling,
and page-to-image extraction.  All functions are stateless and operate
purely on file paths.
"""

import logging
from typing import Any, Dict, Optional

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def listar_campos_pdf(pdf_path: str) -> Dict[str, Optional[str]]:
    """Return all form-field names and types found in *pdf_path*.

    Keys are formatted as ``"field_name|field_type_int"`` and values are
    ``None`` (placeholders for later population).

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        Dict mapping ``"name|type"`` keys to ``None``, or a dict with an
        ``"error"`` key if the file cannot be processed.
    """
    try:
        doc = fitz.open(pdf_path)
        campos: Dict[str, Optional[str]] = {}
        for i in range(doc.page_count):
            for w in doc.load_page(i).widgets() or []:
                key = f"{w.field_name}|{w.field_type}"
                campos[key] = None
        doc.close()
        return campos
    except Exception as e:
        return {"error": str(e)}


def preencher_campos_pdf(
    pdf_path: str,
    output_path: str,
    data: Dict[str, Any],
) -> Any:
    """Fill form fields in *pdf_path* with *data* and save to *output_path*.

    Fields named ``"parte 1"``, ``"parte 2"``, or ``"parte 3"`` receive
    text inserted at their widget coordinates (the widget is then deleted).
    All other fields use the standard ``widget.field_value`` assignment.

    Args:
        pdf_path: Path to the source PDF with fillable form fields.
        output_path: Destination path for the filled PDF.
        data: Dict of ``{field_name: value}`` to apply.

    Returns:
        *output_path* on success, or a dict with an ``"error"`` key on
        failure.
    """
    try:
        doc = fitz.open(pdf_path)
        for i in range(doc.page_count):
            page = doc.load_page(i)
            for w in doc.load_page(i).widgets() or []:
                if w.field_name in data:
                    if w.field_name in ("parte 1", "parte 2", "parte 3"):
                        r = w.rect
                        padding = 1
                        box = fitz.Rect(
                            r.x0 + padding,
                            r.y0 + padding,
                            r.x1 - padding,
                            r.y1 - padding,
                        )
                        try:
                            page.insert_text(
                                (box.x0, box.y0 + 12),
                                data[w.field_name],
                                fontname="helv",
                                fontsize=12,
                                color=(0, 0, 0),
                            )
                        except Exception as e:
                            logger.warning("insert_text falhou: %s", e)
                        page.delete_widget(w)
                    else:
                        w.field_value = data[w.field_name]
                        w.update()
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        return output_path
    except Exception as e:
        return {"error": str(e)}


def extract_pdf_image(pdf_path: str, image_path: str) -> None:
    """Render the first page of *pdf_path* as a PNG and save to *image_path*.

    Args:
        pdf_path: Path to the source PDF.
        image_path: Destination path for the output PNG image.
    """
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap()
    pix.save(image_path)
