"""CLI entry points for the application."""

import os

import uvicorn


def run_dev() -> None:
    """Run the app in development mode with auto-reload."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


def run_prod() -> None:
    """Run the app in production mode with workers matching CPU count."""
    workers = os.cpu_count() or 1
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=workers,
        log_level="info",
    )
