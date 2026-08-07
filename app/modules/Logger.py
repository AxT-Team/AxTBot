"""
Logger Module For AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import logging, os, datetime
from pathlib import Path

from app.modules.Config import config_loader

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            level_colors = {
                'DEBUG': Fore.CYAN,
                'INFO': Fore.WHITE,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.RED + Style.BRIGHT,
            }
            level_color = level_colors.get(record.levelname, Fore.WHITE)
            reset = Style.RESET_ALL
            
            time_str = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
            
            time_part = f"{Fore.WHITE}[{reset}{Fore.GREEN}{time_str}{reset}{Fore.WHITE}]{reset}"
            level_part = f"{Fore.WHITE}[{reset}{level_color}{record.levelname}{Fore.WHITE}]{reset}"
            name_part = f"{Fore.WHITE}[{reset}{Fore.LIGHTYELLOW_EX}{record.name}/{record.process}{Fore.WHITE}]{reset}"
            message_part = f"{level_color}{record.getMessage()}{reset}"
            
            return f"{time_part}{name_part}{level_part} {message_part}"
    
    colorama = True
except ImportError:
    colorama = False


class LazyLogger:
    """惰性 logger，在首次真正使用时才初始化"""
    _logger = None
    
    @classmethod
    def _init(cls):
        if cls._logger is not None:
            return
        
        config = config_loader.get_core_config()
        if not os.path.exists(Path(config.log_dir)):
            os.mkdir(config.log_dir)
        if os.path.exists("latest.log"):
            try:
                mtime = os.path.getatime("latest.log")
                timestamp = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d_%H-%M-%S')
                os.replace("latest.log", os.path.join(config.log_dir, f"log_{timestamp}.log"))
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
        
        file_handler = logging.FileHandler("latest.log", encoding="utf-8", mode="w")
        file_handler.setLevel(config.log_level.upper())
        file_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s/%(process)d][%(levelname)s] %(message)s"))
        
        _log.addHandler(console_handler)
        _log.addHandler(file_handler)
        
        # 让 uvicorn 使用相同的 logger
        for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
            uv_logger = logging.getLogger(name)
            uv_logger.handlers = _log.handlers
            uv_logger.setLevel(_log.level)
            uv_logger.propagate = False
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
