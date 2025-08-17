"""Entrypoint for running the service with uvicorn."""

from __future__ import annotations

import uvicorn


def run() -> None:  # pragma: no cover - thin wrapper
    uvicorn.run("sync_service.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
