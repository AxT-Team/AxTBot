import asyncio
from fastapi import FastAPI, Request, Depends, BackgroundTasks
import os
import uvicorn
import threading
from Core.Auth import auth
from Core.Event import handle_event
from Core.Logger import logger, log_level, logger_stop  # 导入日志对象和相关配置
from Core.Config import config

app = FastAPI()

@app.post(config.path)
async def callback(request: Request, background_tasks: BackgroundTasks, body: dict = Depends(auth.validate_callback)):
    try:
        data = await request.json()
        logger.debug(data)
        op = data.get("op")
        event_type = data.get("t")
        event_data = data.get("d")

        if op == 13:  # 回调地址验证
            plain_token = event_data.get("plain_token")
            event_ts = event_data.get("event_ts")
            signature = auth.generate_signature(plain_token, event_ts)
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
        host=config.ip,
        port=config.port,
        ssl_certfile=config.ssl_cert,
        ssl_keyfile=config.ssl_key,
        log_config=None,  # 禁用 Uvicorn 默认日志配置
        log_level=log_level,  # 设置 Uvicorn 的日志级别
    )


if __name__ == "__main__":
    try:
        # 启动令牌刷新线程
        logger.info("正在启动令牌刷新线程...")
        token_refresh_thread = threading.Thread(target=auth.start_token_refresh, daemon=True)
        token_refresh_thread.start()
        logger.debug(f'框架 >>> 加载配置项：{config}')
        # 启动 FastAPI 应用
        run_uvicorn()
    except KeyboardInterrupt:
        logger.info("Ctrl + C 被按下，正在关机...")
        logger.info('框架 >>> 正在关闭日志记录器...')
        asyncio.run(logger_stop())
        os._exit(0)
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise e