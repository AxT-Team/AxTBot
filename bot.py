"""
AxTBot launcher

Run with: python bot.py
"""
from __future__ import annotations

import logging
import uvicorn

from app.main import app
from app.modules import config_loader, logger
from app.service import certificate_service


def main() -> None:
    config_loader.load("local.env")
    certificate_service.refresh()

    core_config = config_loader.get_core_config()
    app_logger = logger._logger if getattr(logger, "_logger", None) is not None else None
    if app_logger is None:
        logger.info("Bootstrapping logger")
        app_logger = logger._logger

    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uv_logger = logging.getLogger(name)
        uv_logger.handlers = app_logger.handlers
        uv_logger.setLevel(app_logger.level)
        uv_logger.propagate = False

    uvicorn_kwargs = {
        "host": core_config.host,
        "port": core_config.port,
        "reload": bool(core_config.reload_on_change),
        "log_level": core_config.log_level.lower(),
        "log_config": None,
    }
    uvicorn_kwargs.update(certificate_service.get_uvicorn_kwargs())

    uvicorn.run("app.main:app", **uvicorn_kwargs)


if __name__ == "__main__":
    main()
