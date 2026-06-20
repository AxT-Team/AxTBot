"""
Logger Module For AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import logging, os, datetime

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

def get_logger():
    if not os.path.exists("logs"):
        os.mkdir("logs")
    if os.path.exists("latest.log"):
        try:
            mtime = os.path.getatime("latest.log")
            timestamp = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d_%H-%M-%S')
            os.replace("latest.log", os.path.join("logs", f"log_{timestamp}.log"))
        except Exception as e:
            print(f"Error replacing log file: {e}")
    
    logger = logging.getLogger("Main")
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    if colorama:
        console_handler.setFormatter(ColoredFormatter())
    else:
        console_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s/%(process)d][%(levelname)s] %(message)s"))
    
    file_handler = logging.FileHandler("latest.log", encoding="utf-8", mode="w")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter("[%(asctime)s][%(name)s/%(process)d][%(levelname)s] %(message)s"))
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = get_logger()

# 让 uvicorn 使用相同的 logger（就这几行）
for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
    uv_logger = logging.getLogger(name)
    uv_logger.handlers = logger.handlers
    uv_logger.setLevel(logger.level)
    uv_logger.propagate = False
    logging.getLogger("uvicorn.error").name = "Uvicorn"
    logging.getLogger("uvicorn.access").disabled = True