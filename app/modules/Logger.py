"""
Logger Module For AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from __future__ import annotations

import datetime
import logging
from pathlib import Path

from app.modules.Config import config_loader

try:
    from colorama import Fore, Style, init

    init(autoreset=True)

    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            level_colors = {
                "DEBUG": Fore.CYAN,
                "INFO": Fore.WHITE,
                "WARNING": Fore.YELLOW,
                "ERROR": Fore.RED,
                "CRITICAL": Fore.RED + Style.BRIGHT,
            }
            level_color = level_colors.get(record.levelname, Fore.WHITE)
            reset = Style.RESET_ALL
            time_str = self.formatTime(record, "%Y-%m-%d %H:%M:%S")

            time_part = f"{Fore.WHITE}[{reset}{Fore.GREEN}{time_str}{reset}{Fore.WHITE}]{reset}"
            level_part = f"{Fore.WHITE}[{reset}{level_color}{record.levelname}{Fore.WHITE}]{reset}"
            name_part = f"{Fore.WHITE}[{reset}{Fore.LIGHTYELLOW_EX}{record.name}/{record.process}{Fore.WHITE}]{reset}"
            message_part = f"{level_color}{record.getMessage()}{reset}"
            return f"{time_part}{name_part}{level_part} {message_part}"

    colorama = True
except ImportError:
    colorama = False


class LazyLogger:
    """懒加载 logger，在首次真正使用时才初始化。"""

    _logger = None

    @classmethod
    def _init(cls):
        if cls._logger is not None:
            return

        config = config_loader.get_core_config()
        log_dir = Path(config.log_dir or "logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        latest_log = Path("latest.log")
        if latest_log.exists():
            try:
                timestamp = datetime.datetime.fromtimestamp(latest_log.stat().st_mtime).strftime("%Y-%m-%d_%H-%M-%S")
                latest_log.replace(log_dir / f"log_{timestamp}.log")
            except Exception as e:
                print(f"日志处理器 >>> Error replacing log file: {e}")

        _log = logging.getLogger("Main")
        _log.setLevel(config.log_level.upper())

        console_handler = logging.StreamHandler()
        console_handler.setLevel(config.log_level.upper())
        if colorama:
            console_handler.setFormatter(ColoredFormatter())
        else:
            console_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s/%(process)d][%(levelname)s] %(message)s"))

        file_handler = logging.FileHandler(latest_log, encoding="utf-8", mode="w")
        file_handler.setLevel(config.log_level.upper())
        file_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s/%(process)d][%(levelname)s] %(message)s"))

        _log.addHandler(console_handler)
        _log.addHandler(file_handler)

        for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
            uv_logger = logging.getLogger(name)
            uv_logger.setLevel(_log.level)
            uv_logger.propagate = True

        logging.getLogger("uvicorn.error").name = "Uvicorn"
        logging.getLogger("uvicorn.access").disabled = True

        cls._logger = _log

    def __getattr__(self, name):
        self._init()
        return getattr(self._logger, name)

    def __repr__(self):
        self._init()
        return repr(self._logger)


logger = LazyLogger()
