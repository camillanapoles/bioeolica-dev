"""
Celery application configuration.
"""
from __future__ import annotations

import os
from celery import Celery

# Broker and backend URLs must be set via environment variables.
broker_url = os.getenv("CELERY_BROKER_URL")
if not broker_url:
    raise RuntimeError("CELERY_BROKER_URL environment variable must be set")
result_backend = os.getenv("CELERY_RESULT_BACKEND")
if not result_backend:
    raise RuntimeError("CELERY_RESULT_BACKEND environment variable must be set")

celery_app = Celery(
    "virtuallab",
    broker=broker_url,
    backend=result_backend,
    include=[
        "platforms.virtual_lab_platform.backend.src.workflow.tasks",
    ]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
