"""
Module for Plugins Hook/UnHook Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import os, importlib, asyncio, inspect, re
from concurrent.futures import ThreadPoolExecutor

from app.classes import Message, GroupMessage, PrivateMessage, QQInteraction, SessionManager
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

db = get_db()

async def dispatch(event):
    if isinstance(event, Message or GroupMessage or PrivateMessage):
        await _dispatch_message(event)
    elif isinstance(event, QQInteraction):
        await _dispatch_interaction(event)
    else:
        logger.warning(f"未知事件类型: {type(event)}")


async def _dispatch_message(event: GroupMessage | PrivateMessage | Message):
    from app.modules import handlers
    session_id = f"{event.author.member_openid}_{event.group_id if hasattr(event, 'group_id') else 'private'}"
    session = SessionManager.get(session_id)
    if session and not session.future.done():
        # 将该消息交给 Session 处理，不再走正常匹配流程
        session.resolve(event)
        return
    openid = db.get_frame_config_by_key("bot_union_openid").value
    at = f"<@{openid}>"
    msg = event.content
    if at in msg:
        msg = msg.replace(at, "")
        event.is_you = True
    msg = re.sub(r'^ +', '', msg)
    event.content = msg
    matched_func = None
    for h in handlers["all"]:     # 全局消息匹配
        if isinstance(event, h["event_type"]):
            await _run_handler(h["func"], event)
    if msg.startswith("/"):
        cmd = msg[1:].split()[0]
        for h in handlers["command"]: # 命令匹配
            if h["name"] == cmd and isinstance(event, h["event_type"]):
                await _run_handler(h["func"], event)
                return
    if matched_func is None:
        for h in handlers["message"]: # 关键词匹配
            if h["keyword"] in msg and isinstance(event, h["event_type"]):
                await _run_handler(h["func"], event)
                return
    if matched_func is None:
        logger.debug(f"插件处理器 >>> 未匹配到任何处理器: {msg}")
        return

async def _dispatch_interaction(event: QQInteraction):
    from app.modules import handlers
    for h in handlers["interaction"]:
        # 1. 匹配互动数据类型（注意：现在是整数比较）
        if h["type"] is not None and h["type"] != event.data.type:
            continue
        # 2. 匹配事件类型注解（isinstance）
        if isinstance(event, h["event_type"]):
            await _run_handler(h["func"], event)
            break  # 命中一个就停止


_executor = ThreadPoolExecutor(max_workers=4)
async def _run_handler(func, event):
    """统一执行器：兼容同步/异步函数，带超时和异常捕获"""
    try:
        if inspect.iscoroutinefunction(func):
            # 异步函数：直接 await
            await asyncio.wait_for(func(event), timeout=10.0)
        else:
            # 同步函数：扔到线程池执行
            await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(_executor, func, event),
                timeout=30.0
            )
    except asyncio.TimeoutError:
        logger.error(f"处理器 {func.__name__} 执行超时（>30秒），已放弃")
    except Exception as e:
        logger.error(f"处理器 {func.__name__} 执行报错: {e}")
    return None