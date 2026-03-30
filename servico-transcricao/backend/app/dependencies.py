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

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import JWT_ACCESS_TOKEN_EXPIRES, JWT_SECRET_KEY

_bearer = HTTPBearer(auto_error=False)


class JWTAuth:
    """Minimal JWT helper that mimics the fastapi-jwt-auth interface."""

    def __init__(
        self,
        credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
    ) -> None:
        self._credentials = credentials

    def jwt_required(self) -> None:
        if not self._credentials:
            raise HTTPException(status_code=401, detail="Token de autorização ausente")
        try:
            jwt.decode(
                self._credentials.credentials,
                JWT_SECRET_KEY,
                algorithms=["HS256"],
            )
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
        return jwt.encode(
            {"sub": subject, "exp": expire},
            JWT_SECRET_KEY,
            algorithm="HS256",
        )

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
