import logging
import datetime
import coloredlogs
import colorama
import os
import queue
from .Config import config  # 预留Config配置

# 配置日志目录
os.makedirs(config.log_dir, exist_ok=True)

colorama.init()
logger = logging.getLogger('OneBotWS')
log_level = logging.getLevelName(config.log_level.upper())
logger.setLevel(log_level)

# 文件日志处理器，指定 UTF-8 编码
log_filename = os.path.join(config.log_dir, f'log-{datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log')
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)
file_handler.setLevel(log_level)
logger.addHandler(file_handler)

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
logger.addHandler(console_handler)

# 注册新的日志等级 EVENT
EVENT_LEVEL_NUM = 11
logging.addLevelName(EVENT_LEVEL_NUM, 'EVENT')

def event(self, message, *args, **kwargs):
    if self.isEnabledFor(EVENT_LEVEL_NUM):
        self._log(EVENT_LEVEL_NUM, message, args, **kwargs)

logging.Logger.event = event # type: ignore

# 注册新的日志等级 SUCCESS
SUCCESS_LEVEL_NUM = 21
logging.addLevelName(SUCCESS_LEVEL_NUM, 'SUCCESS')

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)
logging.Logger.success = success # type: ignore

# 自定义颜色
level_styles = {
    'critical': {'color': 'red', 'bold': True},
    'error': {'background': 'red', 'color': 'white'},
    'warning': {'background': 'yellow', 'color': 'white', 'bold': False},
    'notice': {'color': 'magenta'},
    'info': {'color': 'white'},
    'debug': {'color': 'black', 'bright': True},
    'spam': {'color': 'cyan', 'faint': True},
    'success': {'color': 'green', 'bold': True},
    'event': {'background': 'green', 'color': 'white', 'bold': True}
}
field_styles = {
    'asctime': {'color': 'green'},
    'levelname': {'color': 'black', 'bright': True},
    'message': {'color': 'white'}
}

# 安装 coloredlogs
coloredlogs.install(level=config.log_level, logger=logger, fmt='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level_styles=level_styles, field_styles=field_styles)

# 创建日志队列
log_queue = queue.Queue()

# 创建队列日志处理器
class LogQueueHandler(logging.Handler):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def emit(self, record):
        log_entry = self.format(record)
        self.queue.put(log_entry)

# 添加队列处理器
queue_handler = LogQueueHandler(log_queue)
queue_handler.setFormatter(file_formatter)
queue_handler.setLevel(log_level)
logger.addHandler(queue_handler)

# 关闭队列处理器的方法
def close_queue_handler():
    logger.removeHandler(queue_handler)

# 停止日志记录的方法
async def logger_stop():
    file_handler.close()
    close_queue_handler()



# 定义日志过滤器
class CustomLogFilter(logging.Filter):
    def filter(self, record):
        # 排除特定请求的日志
        if '"POST /webhook HTTP/1.1"' or 'Invalid HTTP request received.' in record.getMessage():
            return False
        return True

# 定义一个已有的日志记录器
ulogger = logging.getLogger("OneBotWS")

# 获取 Uvicorn 的日志记录器并绑定到自定义日志记录器
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = ulogger.handlers
uvicorn_logger.propagate = False

uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.handlers = ulogger.handlers
uvicorn_error_logger.propagate = False

uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = ulogger.handlers
uvicorn_access_logger.propagate = False

# 添加过滤器
uvicorn_access_logger.addFilter(CustomLogFilter())