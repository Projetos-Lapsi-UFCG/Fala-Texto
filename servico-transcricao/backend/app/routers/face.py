# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Face recognition routes.

POST /autenticacao   — Verify an uploaded image against registered faces.
POST /upload-imagem  — Register a new face image (must contain exactly one face).
"""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from werkzeug.utils import secure_filename

from app.config import IMAGE_FOLDER
from app.dependencies import JWTAuth, limiter
from app.services import face_service

router = APIRouter()


@router.post("/autenticacao")
@limiter.limit("15/minute")
async def autenticacao(
    request: Request,
    file: UploadFile = File(...),
    Authorize: JWTAuth = Depends(),
) -> dict:
    """Verify that the uploaded face image matches a registered identity.

    Args:
        file: Image file containing the face to verify.

    Returns:
        ``{"analise": True}`` if a match is found, ``{"analise": False}``
        otherwise.

    Raises:
        HTTPException: 400 if no file is provided.
    """
    Authorize.jwt_required()
    if not file.filename:
        raise HTTPException(400, "Nenhum arquivo selecionado")

    fn = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    fp = os.path.join(IMAGE_FOLDER, fn)
    with open(fp, "wb") as buf:
        buf.write(await file.read())

    ok = face_service.authenticate_face_multi(fp)
    os.remove(fp)
    return {"analise": ok}


@router.post("/upload-imagem")
@limiter.limit("10/minute")
async def upload_imagem(
    request: Request,
    file: UploadFile = File(...),
    Authorize: JWTAuth = Depends(),
) -> JSONResponse:
    """Register a face image for future authentication.

    The image must contain exactly one detectable face.  Images with zero
    or multiple faces are rejected and deleted.

    Args:
        file: JPEG image file containing a single face.

    Returns:
        200 JSON response on success.

    Raises:
        HTTPException: 400 if no file is provided, the image contains no
            face, or the image contains more than one face.
    """
    Authorize.jwt_required()
    if not file.filename:
        raise HTTPException(400, "Nenhum arquivo enviado")

    fn = f"registered_{uuid.uuid4()}.jpg"
    fp = os.path.join(IMAGE_FOLDER, fn)
    with open(fp, "wb") as buf:
        buf.write(await file.read())

    if face_service.validate_single_face(fp):
        return JSONResponse({"mensagem": "Imagem recebida com sucesso"}, status_code=200)

    os.remove(fp)
    raise HTTPException(400, "Imagem sem face ou com muitos rostos, não foi salva.")
