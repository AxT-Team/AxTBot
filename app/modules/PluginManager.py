"""
Module for Plugins Hook/UnHook Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import os, importlib, asyncio, inspect, re
from concurrent.futures import ThreadPoolExecutor

from app.classes import Message
from app.modules import config, logger, get_db

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = config.plugins_dir
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            logger.warning("插件 >>> 插件目录不存在，已生成目录")
    
    def load_all(self):
        from app.modules import handlers
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                module_name = filename[:-3]
                importlib.import_module(f"{self.plugin_dir}.{module_name}")
        logger.info(f"插件 >>> 已加载 {len(handlers['command'])} 个命令，{len(handlers['message'])} 个消息处理器")

# 创建一个全局线程池，用来跑同步插件（防止同步阻塞卡住事件循环）
_executor = ThreadPoolExecutor(max_workers=4)
db = get_db()

async def dispatch(event: dict):
    from app.modules import handlers
    event = Message(**event)
    openid = db.get_frame_config_by_key("bot_union_openid").value
    at = f"<@{openid}>"
    msg = event.content
    if at in msg:
        msg = msg.replace(at, "")
        event.is_you = True
    msg = re.sub(r'^ +', '', msg)
    event.content = msg
    matched_func = None
    if msg.startswith("/"): # 匹配/开头的命令
        cmd = msg[1:].split()[0]
        for h in handlers["command"]:
            if h["name"] == cmd:
                matched_func = h["func"]
                break
    if matched_func is None:
        for h in handlers["message"]: # 匹配关键词
            if h["keyword"] is None or h["keyword"] in msg:
                matched_func = h["func"]
                break
    if matched_func is None:
        logger.debug(f"插件处理器 >>> 未匹配到任何处理器: {msg}")
        return
    
    # 4. 核心执行逻辑（带超时和异常捕获）
    try:
        # 判断插件是同步函数还是异步函数
        if inspect.iscoroutinefunction(matched_func):
            # 异步插件：直接 await，并设置超时
            await asyncio.wait_for(matched_func(event), timeout=10.0)
        else:
            # 同步插件：扔到线程池里执行，防止阻塞主事件循环
            await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(_executor, matched_func, event),
                timeout=30.0
            )
    except asyncio.TimeoutError:
        logger.error(f"插件 {matched_func.__name__} 执行超时（>30秒），已放弃")
    except Exception as e:
        logger.error(f"插件 {matched_func.__name__} 执行报错: {e}")