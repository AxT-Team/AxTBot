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
from app.service.AccessToken import shutdown_token_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists("data"):
        os.mkdir("data")
        logger.warning("框架 >>> 数据目录不存在，已创建 data 文件夹")
    else:
        pass
    from app.modules.DataBase import get_db
    db_instance = get_db()
    logger.info(f"框架 >>> 数据库已初始化: {db_instance.db_url}")

    yield

    logger.info("框架 >>> 正在关闭数据库连接...")
    # 释放数据库连接池
    db_instance.engine.dispose()
    logger.info("框架 >>> 正在结束后台服务...")
    shutdown_token_service()


app = FastAPI(
    title="AxTBot API",
    description="AxTBot Webhook Service for OpenAPI",
    version="2.1.1",
    lifespan=lifespan
)

for i in routers:
    app.include_router(i)
    logger.debug(f"Included router: {i}")