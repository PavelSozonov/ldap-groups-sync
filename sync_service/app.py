"""FastAPI application."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Response

from .settings import load_config
from .metrics import export_metrics, sync_iterations_total, last_sync_timestamp_seconds
from .logging_conf import configure_logging

config_path = Path("config/config.yaml")
app_config = load_config(config_path)
ready = False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global ready
    configure_logging()

    async def sync_loop() -> None:
        global ready
        ready = True
        while True:
            sync_iterations_total.inc()
            last_sync_timestamp_seconds.set_to_current_time()
            await asyncio.sleep(app_config.sync.get("interval_seconds", 60))

    task = asyncio.create_task(sync_loop())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


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
