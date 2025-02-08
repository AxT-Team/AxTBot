import asyncio
from fastapi import FastAPI, Request, Depends
import os
import uvicorn
import threading
from Core.Auth import validate_callback, generate_signature, start_token_refresh
from Core.Event import handle_event
from Core.Logger import logger  # 导入日志对象
import logging

app = FastAPI()

# 从 QQ 机器人控制台获取的 Bot Secret
BOT_SECRET = "1VzTxRvPtOtOtOtOuQwSyU0W3a7eBiFn"

# 从 QQ 机器人控制台获取的 App ID 和 Client Secret
APP_ID = "102076583"

@app.post("/webhook")
async def callback(request: Request, body: dict = Depends(validate_callback)):
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
        elif op == 12:
            logger.debug("Callback mode response")
            pass  # 回调模式回包
        elif op == 0:
            asyncio.create_task(handle_event(event_type, event_data))
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        return {"status": "error"}

def run_uvicorn():
    """启动 FastAPI 应用的函数"""
    logger.info("正在启动 FastAPI 应用...")
    # 配置 uvicorn 使用自定义日志
    logging.getLogger("uvicorn").handlers = logger.handlers
    logging.getLogger("uvicorn.error").handlers = logger.handlers
    logging.getLogger("uvicorn.access").handlers = logger.handlers
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8443,
        ssl_certfile="data/cert.pem",
        ssl_keyfile="data/key.pem",
        log_config=None,  # 禁用 uvicorn 默认日志配置
        log_level="error"  # 设置日志级别
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