# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Application configuration.

All tuneable values live here. Hardcoded defaults preserve the original
behaviour; override them via environment variables in production.
"""

import os
import secrets

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

ORIGINS: list[str] = [
    os.getenv("CORS_ORIGIN", "https://processarcadastro.cyberedu.com.br"),
]

# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
JWT_ACCESS_TOKEN_EXPIRES: int = int(
    os.getenv("JWT_ACCESS_TOKEN_EXPIRES", str(6 * 60 * 60))  # 6 hours
)


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
