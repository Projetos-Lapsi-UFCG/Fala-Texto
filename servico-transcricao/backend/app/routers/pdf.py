# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
PDF processing routes.

POST /listar-campos    — List all form fields in an uploaded PDF.
POST /preencher-campos — Fill form fields supplied as multipart form data.
POST /imagem           — Render the first page of a PDF as a PNG image.
POST /preencher-pdf    — Fill a PDF using key/value pairs from an uploaded CSV.
"""

import os
import uuid
from typing import Any, Dict, List

import pandas as pd
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from werkzeug.utils import secure_filename

from app.config import IMAGE_FOLDER, UPLOAD_FOLDER
from app.dependencies import JWTAuth, limiter
from app.services import pdf_service
from app.services.field_mapping import coerce_field_types, map_csv_to_pdf_fields

router = APIRouter()


@router.post("/listar-campos")
@limiter.limit("15/minute")
async def listar_campos(
    request: Request,
    file: UploadFile = File(...),
    Authorize: JWTAuth = Depends(),
) -> dict:
    """Return all form-field names and types found in the uploaded PDF.

    Args:
        file: PDF file with fillable form fields.

    Returns:
        Dict of ``{"field_name|field_type": None}`` entries.

    Raises:
        HTTPException: 400 if no file is provided.
    """
    Authorize.jwt_required()
    if not file.filename:
        raise HTTPException(400, "Nenhum arquivo selecionado")

    fn = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    fp = os.path.join(UPLOAD_FOLDER, fn)
    with open(fp, "wb") as buf:
        buf.write(await file.read())

    campos = pdf_service.listar_campos_pdf(fp)
    os.remove(fp)
    return campos


@router.post("/preencher-campos")
@limiter.limit("15/minute")
async def preencher_campos(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    Authorize: JWTAuth = Depends(),
) -> FileResponse:
    """Fill PDF form fields with values from the multipart form body.

    Each non-file form field must be keyed as ``"field_name|field_type_int"``
    (the same format returned by ``/listar-campos``).

    Args:
        file: Source PDF file.

    Returns:
        The filled PDF as a file download.

    Raises:
        HTTPException: 400 if no file is provided.
    """
    Authorize.jwt_required()
    if not file.filename:
        raise HTTPException(400, "Nenhum arquivo selecionado")

    in_fn = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    in_fp = os.path.join(UPLOAD_FOLDER, in_fn)
    with open(in_fp, "wb") as buf:
        buf.write(await file.read())

    out_fn = f"{uuid.uuid4()}_preenchido.pdf"
    out_fp = os.path.join(UPLOAD_FOLDER, out_fn)

    form = await request.form()
    data: Dict[str, Any] = {}
    for key, val in form.items():
        if key != "file":
            name, t = key.split("|")
            t = int(t)
            if t == 7:
                data[name] = val
            elif t == 5:
                data[name] = int(val)
            elif t == 2:
                data[name] = bool(val)

    pdf_service.preencher_campos_pdf(in_fp, out_fp, data)
    os.remove(in_fp)
    background_tasks.add_task(os.remove, out_fp)
    return FileResponse(
        path=out_fp,
        filename=os.path.basename(out_fp),
        media_type="application/pdf",
        background=background_tasks,
    )


@router.post("/imagem")
@limiter.limit("15/minute")
async def imagem(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    Authorize: JWTAuth = Depends(),
) -> FileResponse:
    """Render the first page of an uploaded PDF as a PNG image.

    Args:
        file: Source PDF file.

    Returns:
        The rendered page as a PNG file download.

    Raises:
        HTTPException: 400 if no file is provided.
    """
    Authorize.jwt_required()
    if not file.filename:
        raise HTTPException(400, "Nenhum arquivo selecionado")

    in_fn = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    in_fp = os.path.join(UPLOAD_FOLDER, in_fn)
    with open(in_fp, "wb") as buf:
        buf.write(await file.read())

    out_fn = f"{uuid.uuid4()}_pagina.png"
    out_fp = os.path.join(IMAGE_FOLDER, out_fn)

    pdf_service.extract_pdf_image(in_fp, out_fp)
    os.remove(in_fp)
    background_tasks.add_task(os.remove, out_fp)
    return FileResponse(
        path=out_fp,
        filename=out_fn,
        media_type="image/png",
        background=background_tasks,
    )


@router.post("/preencher-pdf")
@limiter.limit("15/minute")
async def preencher_pdf(
    request: Request,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    Authorize: JWTAuth = Depends(),
) -> FileResponse:
    """Fill a PDF form using key/value pairs from an uploaded CSV file.

    Accepts exactly two files: one ``.csv`` (with ``chave``/``valor``
    columns) and one ``.pdf``.  The CSV keys are mapped to PDF form fields
    by :func:`~app.services.field_mapping.map_csv_to_pdf_fields`.

    Args:
        files: List containing exactly a CSV and a PDF file (any order).

    Returns:
        The filled PDF as a file download.

    Raises:
        HTTPException: 400 if no file is selected, an unsupported file type
            is uploaded, or the PDF contains no form fields.
    """
    Authorize.jwt_required()

    caminho_csv: str = ""
    in_fp: str = ""

    for file in files:
        if not file.filename:
            raise HTTPException(400, "Nenhum arquivo selecionado")
        nome = file.filename.lower()
        if nome.endswith(".csv"):
            caminho_csv = os.path.join(
                UPLOAD_FOLDER, f"{uuid.uuid4()}_{secure_filename(nome)}"
            )
            with open(caminho_csv, "wb") as buf:
                buf.write(await file.read())
        elif nome.endswith(".pdf"):
            in_fn = f"{uuid.uuid4()}_{secure_filename(nome)}"
            in_fp = os.path.join(UPLOAD_FOLDER, in_fn)
            with open(in_fp, "wb") as buf:
                buf.write(await file.read())
        else:
            raise HTTPException(400, f"Tipo de arquivo não suportado: {nome}")

    out_fn = f"{uuid.uuid4()}_preenchido.pdf"
    out_fp = os.path.join(UPLOAD_FOLDER, out_fn)

    campos = pdf_service.listar_campos_pdf(in_fp)
    if len(campos) <= 1:
        raise HTTPException(400, "Erro !!!")

    df = pd.read_csv(caminho_csv, header=0, names=["chave", "valor"])
    df.fillna("", inplace=True)
    dicionario = dict(zip(df["chave"], df["valor"]))
    os.remove(caminho_csv)

    form = map_csv_to_pdf_fields(dicionario, campos)
    data = coerce_field_types(form)

    pdf_service.preencher_campos_pdf(in_fp, out_fp, data)
    os.remove(in_fp)
    background_tasks.add_task(os.remove, out_fp)
    return FileResponse(
        path=out_fp,
        filename=os.path.basename(out_fp),
        media_type="application/pdf",
        background=background_tasks,
    )
