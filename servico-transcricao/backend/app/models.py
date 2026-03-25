# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Pydantic request / response models.
"""

from pydantic import BaseModel


class LoginModel(BaseModel):
    """Credentials for the ``POST /login`` endpoint."""

    username: str
    password: str
