"""
Entry File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
import asyncio, threading

from app.modules import on_message, on_command, on_interaction, on_all_message

try:
    from app.service.qq_service.AccessToken import get_access_token
    def run_async_in_thread():
        asyncio.run(get_access_token())

    thread1 = threading.Thread(target=run_async_in_thread, name="AccessTokenThread", daemon=True)
    thread1.start()
except Exception as e:
    from app.modules import logger
    logger.warning("框架 >>> 未加载QQ服务框架，主框架将以终端模式运行")


try:
    from app.modules import PM
    pm = PM()
    pm.load_all()
except Exception as e:
    from app.modules import logger
    logger.error(f"插件 >>> 插件处理器加载失败，错误如下：{e}")
    raise e