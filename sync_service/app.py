"""FastAPI application."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
import logging
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Response

from .settings import load_config
from .metrics import export_metrics, last_sync_timestamp_seconds, sync_iterations_total
from .logging_conf import configure_logging
from .services.engine_manager import EngineManager

config_path = Path("config/config.yaml")
app_config = load_config(config_path)
ready = False


engine_manager = EngineManager(app_config)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global ready
    configure_logging()

    # Build and start all engines
    engine_manager.build_engines()
    await engine_manager.start()
    ready = True

    try:
        yield
    finally:
        await engine_manager.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    return {"ready": str(ready).lower()}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(export_metrics(), media_type="text/plain; version=0.0.4")


@app.get("/version")
async def version() -> dict[str, str]:
    return {"version": "0.1.0"}


@app.get("/engines/status")
async def engines_status() -> dict[str, str]:
    """Get status of all sync engines."""
    return engine_manager.get_engine_status()
