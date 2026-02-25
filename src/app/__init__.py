from fastapi import FastAPI
from contextlib import asynccontextmanager
from pathlib import Path

from src.Utils.Logger import logger, shutdown_logging  # 导入日志模块
from src.Utils.Config import config  # 导入配置模块
from src.Utils.ConfigCli import load_config
from src.Utils.AutoUpdate import check_update
from src.Utils.PluginBase import initialize_plugins, shutdown_plugins
from src.Utils.GetAccessToken import get_access_token

@asynccontextmanager
async def startup_event(app: FastAPI):
    logger.debug("===========框架 startup 事件激活===========")
    logger.info("框架 前置处理 >>> 日志记录已启动")
    logger.info("框架 前置处理 >>> Tortoise ORM数据库已启动")
    await load_config(config_path=Path("config.yaml"))
    logger.debug(f"框架 前置处理 >>> 配置文件：{config}")
    logger.debug("------------------更新检查------------------")
    if config.Advanced.update:
        logger.info("版本检查 >>> 正在检查更新...")
        await check_update()
    else:
        logger.info("版本检查 >>> 检查更新未启用，将跳过检查更新...")
    logger.debug("------------------检查结束------------------")


    logger.debug("----------------加载插件开始----------------")
    await initialize_plugins()
    from src.Utils.PluginBase import COMMAND_REGISTRY
    logger.debug(f"框架 前置处理 >>> 已注册命令: {list(COMMAND_REGISTRY.keys())}")
    logger.debug("----------------加载插件结束----------------")


    logger.debug("----------正在启动AccessToken线程-----------")
    await get_access_token()
    logger.debug("----------AccessToken线程启动完毕-----------")


    logger.debug("===========框架 startup 事件结束===========")
    head = "https://" if config.Network.ssl else "http://"
    logger.info(f"框架已启动，监听地址：{head}{config.Network.host}:{config.Network.port}{config.Network.path}")
    yield

    logger.info("框架 前置处理>>> 正在关闭插件处理器...")
    await shutdown_plugins()
    logger.info("框架 前置处理>>> 正在关闭日志记录器...")
    shutdown_logging()
    logger.info("框架 前置处理>>> 框架已关闭")
def create_app() -> FastAPI:
    app = FastAPI(
        title="AxTBot-Public",
        version="2.1.0",
        docs_url=None,  # 禁用文档
        redoc_url=None,  # 禁用文档
        lifespan=startup_event,
    )
    return app
