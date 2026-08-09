"""
Main File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.modules import FrameConfig, config_loader, get_db, logger
from app.router import __all__ as routers
from app.service import certificate_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    config_loader.load("local.env")
    certificate_service.refresh()
    logger.info(f"证书服务 >>> 当前模式: {certificate_service.get_state().mode}")

    if not os.path.exists("data"):
        os.mkdir("data")
        logger.warning("框架 >>> 数据目录不存在，已创建 data 文件夹")

    from app.modules import database
    import time as _time

    logger.info(f"框架 >>> 数据库已初始化: {database.db_url}")

    _db = get_db()
    _now = str(int(_time.time()))
    _existing = _db.get_frame_config_by_key("startup_time")
    if _existing:
        _db.update_frame_config("startup_time", _now, int(_time.time()))
    else:
        _db.add_frame_config(FrameConfig(key="startup_time", value=_now, create_time=_now, update_time=_now))
    logger.debug(f"框架 >>> 启动时间已记录: {_now}")

    try:
        from app.service.qq_service.AccessToken import shutdown_token_service
        from app.service.qq_service.BotInfo import get_qqbot_info

        await get_qqbot_info()
    except Exception as e :
        logger.warning("框架 >>> 无法加载QQ适配器服务，主框架将以终端模式运行")
        logger.warning(f"框架 >>> 详细错误：{e}")
        raise

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
    lifespan=lifespan,
)
app.state.certificate_service = certificate_service

for router in routers:
    app.include_router(router)
    for tag in router.tags:
        logger.debug(f"FastAPI >>> Included router: {str(tag)}")
