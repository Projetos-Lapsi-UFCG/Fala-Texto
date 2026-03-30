# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Authentication routes.

GET  /       — Serves the home page (index.html).
POST /login  — Validates credentials and returns a JWT access token.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import JWTAuth, limiter, pwd_context, usuarios
from app.models import LoginModel

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    """Serve the main UI page."""
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/login")
@limiter.limit("15/minute")
def login(
    request: Request,
    data: LoginModel,
    Authorize: JWTAuth = Depends(),
) -> dict:
    """Authenticate a user and return a JWT access token.

    Args:
        data: ``LoginModel`` with ``username`` and ``password``.

    Returns:
        Dict with ``"access_token"`` on success.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    if data.username in usuarios and pwd_context.verify(
        data.password, usuarios[data.username]
    ):
        token = Authorize.create_access_token(subject=data.username)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Usuário ou senha incorretos")
