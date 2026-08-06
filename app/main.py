"""
Main File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.router import __all__ as routers
from app.modules import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists("data"):
        os.mkdir("data")
        logger.warning("框架 >>> 数据目录不存在，已创建 data 文件夹")
    else:
        pass
    from app.modules import database, get_db, FrameConfig
    import time as _time
    logger.info(f"框架 >>> 数据库已初始化: {database.db_url}")

    # 记录框架启动时间
    _db = get_db()
    _now = str(int(_time.time()))
    _existing = _db.get_frame_config_by_key("startup_time")
    if _existing:
        _db.update_frame_config("startup_time", _now, int(_time.time()))
    else:
        _db.add_frame_config(FrameConfig(key="startup_time", value=_now, create_time=_now, update_time=_now))
    logger.info(f"框架 >>> 启动时间已记录: {_now}")

    try:
        from app.service.qq_service.AccessToken import shutdown_token_service
        from app.service.qq_service.BotInfo import get_qqbot_info
        await get_qqbot_info()
    except Exception as e :
        logger.warning("框架 >>> 无法加载QQ适配器服务，主框架将以终端模式运行")
        logger.warning(f"框架 >>> 详细错误：{e}")
        raise e

    yield

    logger.info("框架 >>> 正在关闭数据库连接...")
    # 释放数据库连接池
    database.engine.dispose()
    logger.info("框架 >>> 正在结束后台服务...")
    shutdown_token_service()


app = FastAPI(
    title="AxTBot API",
    description="AxTBot Service for OpenAPI",
    version="2.1.1",
    lifespan=lifespan
)

for i in routers:
    app.include_router(i)
    for tag in i.tags:
        logger.debug(f"FastAPI >>> Included router: {str(tag)}")