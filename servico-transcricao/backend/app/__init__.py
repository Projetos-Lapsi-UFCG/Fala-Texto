# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Application factory for the Fala-Texto transcription service.

Call :func:`create_app` to obtain a fully configured :class:`~fastapi.FastAPI`
instance.  The entry point ``servico.py`` does exactly that and exposes the
result as ``app`` so Gunicorn/Uvicorn can find it.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_jwt_auth.exceptions import AuthJWTException
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import IMAGE_FOLDER, ORIGINS, UPLOAD_FOLDER
from app.dependencies import limiter
from app.exceptions import authjwt_exception_handler, rate_limit_handler
from app.routers import auth, audio, face, pdf


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application.

    * Mounts ``static/`` for favicon and other static assets.
    * Registers CORS, rate-limiting, and JWT middleware.
    * Attaches exception handlers for rate-limit and JWT errors.
    * Includes all domain routers (auth, audio, face, pdf).
    * Ensures upload and image storage directories exist.

    Returns:
        A ready-to-serve :class:`~fastapi.FastAPI` instance.
    """
    app = FastAPI(
        title="API FastAPI: PDF, Áudio e Face",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)
    app.add_exception_handler(AuthJWTException, authjwt_exception_handler)

    app.include_router(auth.router)
    app.include_router(audio.router)
    app.include_router(face.router)
    app.include_router(pdf.router)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(IMAGE_FOLDER, exist_ok=True)

    return app
