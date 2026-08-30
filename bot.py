"""
AxTBot launcher

Run with: python bot.py
"""
from __future__ import annotations
from dotenv import load_dotenv

import os



# 必须在任何 app 导入之前把配置载入 os.environ：
# app.modules 的导入链（PluginManager -> DataBase -> logger）在模块级别就会
# 触发 config_loader.get_core_config()，而 ConfigLoader 单例在首次导入时
# 通过 _auto_init 读取 os.environ。若此时 env 还没载入，就会 RuntimeError。
env_file = os.environ.get("AXTBOT_ENV_FILE", ".env.local")
if os.path.exists(env_file):
    load_dotenv(env_file)

import logging  # noqa: E402
import uvicorn  # noqa: E402

from app.main import app  # noqa: E402
from app.modules import config_loader, logger  # noqa: E402
from app.service import certificate_service  # noqa: E402


def main() -> None:
    # 用同一份 env 文件再显式加载一次，确保 core_config 就绪
    config_loader.load(env_file)
    certificate_service.refresh()

    core_config = config_loader.get_core_config()
    app_logger = getattr(logger, "_logger", None)
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
