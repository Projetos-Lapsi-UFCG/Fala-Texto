# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Application configuration.

All tuneable values live here. Hardcoded defaults preserve the original
behaviour; override them via environment variables in production.
"""

import os
import secrets

from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

ORIGINS: list[str] = [
    os.getenv("CORS_ORIGIN", "https://processarcadastro.cyberedu.com.br"),
]

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

class JWTSettings(BaseModel):
    """JWT configuration consumed by fastapi-jwt-auth."""

    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
    authjwt_access_token_expires: int = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES", str(6 * 60 * 60))  # 6 hours
    )


@AuthJWT.load_config
def get_jwt_settings() -> JWTSettings:
    return JWTSettings()


# ---------------------------------------------------------------------------
# Storage folders
# ---------------------------------------------------------------------------

UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
IMAGE_FOLDER: str = os.getenv("IMAGE_FOLDER", "imagens")

# ---------------------------------------------------------------------------
# Whisper model
# ---------------------------------------------------------------------------

WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "turbo")

# ---------------------------------------------------------------------------
# Audio quality thresholds (used in /transcricao quality gate)
# ---------------------------------------------------------------------------

SNR_THRESHOLD: float = 12.0
PITCH_THRESHOLD: float = 100.0
RMS_THRESHOLD: float = 0.012
