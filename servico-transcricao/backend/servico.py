# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lapsi/Fala-texto
"""
Entry point for the Fala-Texto transcription service.

Gunicorn/Uvicorn loads this module and looks for the ``app`` object:

    gunicorn -b 0.0.0.0:7050 --workers 1 \\
        --worker-class uvicorn.workers.UvicornWorker servico:app

All application logic lives in the ``app/`` package.  See
``app/__init__.py`` for the ``create_app()`` factory.
"""

from app import create_app

app = create_app()
















