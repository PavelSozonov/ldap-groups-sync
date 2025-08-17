"""Logging configuration utilities."""

import logging
import os


def configure_logging() -> None:
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    if os.getenv("LOG_FORMAT", "json") == "json":
        fmt = "%(message)s"
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format=fmt)
