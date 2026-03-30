# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Application-level exception handlers.

These are registered on the FastAPI app instance inside ``create_app()``.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded


def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Return 429 when a client exceeds its rate limit."""
    return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
