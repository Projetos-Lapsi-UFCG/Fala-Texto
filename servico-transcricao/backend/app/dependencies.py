# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Shared FastAPI dependencies and application-wide singletons.

The `limiter` and `pwd_context` objects are created once at import time and
reused by all routers that need them.

NOTE: `usuarios` is a hardcoded in-memory stub.  It is not a real database.
Replace with a proper user store before any production rollout that requires
more than the current two fixed accounts.
"""

from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------

limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# In-memory user store (stub — not a real database)
# ---------------------------------------------------------------------------

usuarios: dict[str, str] = {
    "Fala-texto": pwd_context.hash("Transcrição_de_fala_em_texto_api"),
    "whisperadm": pwd_context.hash("Transcrição_de_fala_api"),
}
