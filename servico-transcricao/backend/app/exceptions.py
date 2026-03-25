# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Application-level exception handlers.

These are registered on the FastAPI app instance inside ``create_app()``.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from slowapi.errors import RateLimitExceeded


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return 429 when a client exceeds its rate limit."""
    return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)


def authjwt_exception_handler(request: Request, exc: AuthJWTException) -> JSONResponse:
    """Return the appropriate status code for JWT authentication errors."""
    return JSONResponse({"detail": exc.message}, status_code=exc.status_code)
