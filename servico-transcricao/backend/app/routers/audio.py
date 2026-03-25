# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Audio transcription route.

POST /transcricao — Preprocesses an uploaded audio file, runs a quality
gate (SNR, pitch, RMS), and returns the Whisper transcription.
"""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi_jwt_auth import AuthJWT
from werkzeug.utils import secure_filename

from app.config import (
    PITCH_THRESHOLD,
    RMS_THRESHOLD,
    SNR_THRESHOLD,
    UPLOAD_FOLDER,
)
from app.dependencies import limiter
from app.services import audio_service

router = APIRouter()


@router.post("/transcricao")
@limiter.limit("15/minute")
async def transcricao(
    request: Request,
    file: UploadFile = File(...),
    Authorize: AuthJWT = Depends(),
) -> dict:
    """Transcribe speech from an uploaded audio file.

    The audio is preprocessed (noise reduction, normalisation) before
    transcription.  A quality gate rejects recordings that are too noisy
    or too quiet (SNR < 12 dB, pitch < 100 Hz, or RMS < 0.012).

    Args:
        file: Uploaded audio file (any format supported by pydub).

    Returns:
        Whisper result dict with at least a ``"text"`` key, or
        ``{"text": "audio ruim"}`` when the quality gate rejects the file.

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

    audio = audio_service.preprocess_audio(fp)
    snr_value = audio_service.calculate_snr_speech(audio)
    rms, pitch, _ = audio_service.analyze_audio(audio)

    if snr_value > SNR_THRESHOLD and pitch > PITCH_THRESHOLD and rms >= RMS_THRESHOLD:
        texto = audio_service.transcricao_pdf(audio)
    else:
        texto = {"text": "audio ruim"}

    os.remove(fp)
    if os.path.exists(audio):
        os.remove(audio)

    return texto
