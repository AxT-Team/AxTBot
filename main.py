import asyncio
from fastapi import FastAPI, Request, Depends, BackgroundTasks
import os
import uvicorn
import threading
from Core.Auth import validate_callback, generate_signature, start_token_refresh
from Core.Event import handle_event
from Core.Logger import logger, log_level, file_formatter, console_handler, file_handler  # 导入日志对象和相关配置
import logging


# 从 QQ 机器人控制台获取的 Bot Secret
BOT_SECRET = "您的BOTSecret"

# 从 QQ 机器人控制台获取的 App ID 和 Client Secret
APP_ID = "您的APPID"


# 定义日志过滤器
class CustomLogFilter(logging.Filter):
    def filter(self, record):
        # 排除特定请求的日志
        if '"POST /webhook HTTP/1.1"' in record.getMessage():
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

app = FastAPI()

@app.post("/webhook")
async def callback(request: Request, background_tasks: BackgroundTasks, body: dict = Depends(validate_callback)):
    try:
        data = await request.json()
        op = data.get("op")
        event_type = data.get("t")
        event_data = data.get("d")

        if op == 13:  # 回调地址验证
            plain_token = event_data.get("plain_token")
            event_ts = event_data.get("event_ts")
            signature = generate_signature(BOT_SECRET, plain_token, event_ts)
            logger.debug("Callback address validation successful")
            return {"plain_token": plain_token, "signature": signature}
        elif op == 0:
            background_tasks.add_task(handle_event, event_type, event_data)
            event_id = data.get("id")
            return {"op_code": 12, "d": {"event_id": event_id, "status": 0, "message": "success"}}
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        return {"status": "error"}


def run_uvicorn():
    """启动 FastAPI 应用的函数"""
    logger.info("正在启动 FastAPI 应用...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443,
        ssl_certfile="data/cert.pem",
        ssl_keyfile="data/key.pem",
        log_config=None,  # 禁用 Uvicorn 默认日志配置
        log_level=log_level,  # 设置 Uvicorn 的日志级别
    )


if __name__ == "__main__":
    try:
        # 启动令牌刷新线程
        logger.info("正在启动令牌刷新线程...")
        token_refresh_thread = threading.Thread(target=start_token_refresh, args=(APP_ID, BOT_SECRET), daemon=True)
        token_refresh_thread.start()

        # 启动 FastAPI 应用
        run_uvicorn()
    except KeyboardInterrupt:
        logger.info("Ctrl + C 被按下，正在关机...")
        os._exit(0)
    except Exception as e:
        logger.error(f"未知错误: {e}")
        os._exit(1)