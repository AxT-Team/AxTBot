"""
Module for Plugins Hook/UnHook Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import os, importlib, asyncio, inspect, re, sys
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
from importlib.metadata import entry_points
from pathlib import Path

from app.classes import Message, GroupMessage, PrivateMessage, QQInteraction, SessionManager, PluginMetadata
from app.modules import config, logger, get_db

metadata_registry: Dict[str, PluginMetadata] = {}

class PluginManager:
    def __init__(self, plugin_dir="plugins", load_from_entry_points=True):
        self.plugin_dir = Path(config.plugins_dir)
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
            logger.warning("插件 >>> 插件目录不存在，已生成目录")
        self.load_from_entry_points = load_from_entry_points

    def _check_and_clean_dependencies(self):
        """
        遍历所有已加载插件的元数据，检查依赖是否满足。
        不满足的插件会从 metadata_registry 中移除，并清理其注册的所有处理器。
        """
        from app.modules import logger
        import sys
        
        disabled_plugins = []
        
        # 使用 list() 创建副本，因为我们要在遍历时删除字典项
        for plugin_name, meta in list(metadata_registry.items()):
            missing_deps = []
            
            for dep in meta.dependencies:
                if dep not in metadata_registry:
                    missing_deps.append(dep)
            
            if missing_deps:
                logger.error(
                    f"插件 >>> 插件 '{plugin_name}'({meta.module_name}) 缺少依赖: {', '.join(missing_deps)}，已禁用"
                )
                disabled_plugins.append(plugin_name)
                
                # 1. 从元数据注册表中删除
                del metadata_registry[plugin_name]
                self._remove_handlers_by_module(meta.module_name)  # 需要给 PluginMetadata 增加 module_name 字段
        
        if disabled_plugins:
            logger.warning(f"插件 >>> 已禁用插件: {', '.join(disabled_plugins)}")

    def _remove_handlers_by_module(self, module_full_name: str):
        """
        从所有处理器列表中，移除属于指定模块的所有处理器
        module_full_name: 如 'plugins.weather'
        """
        from app.modules import handlers
        
        # 1. 移除命令处理器
        before_count = len(handlers["command"])
        handlers["command"] = [
            h for h in handlers["command"] 
            if h["func"].__module__ != module_full_name
        ]
        removed = before_count - len(handlers["command"])
        
        # 2. 移除消息关键词处理器
        before_count = len(handlers["message"])
        handlers["message"] = [
            h for h in handlers["message"] 
            if h["func"].__module__ != module_full_name
        ]
        removed += before_count - len(handlers["message"])
        
        # 3. 如果有全局消息钩子（之前我们设计的 on_all_message）
        if "all" in handlers:
            before_count = len(handlers["all"])
            handlers["all"] = [
                h for h in handlers["all"] 
                if h["func"].__module__ != module_full_name
            ]
            removed += before_count - len(handlers["all"])
        
        # 4. 如果有互动事件处理器
        if "interaction" in handlers:
            before_count = len(handlers["interaction"])
            handlers["interaction"] = [
                h for h in handlers["interaction"] 
                if h["func"].__module__ != module_full_name
            ]
            removed += before_count - len(handlers["interaction"])
        
        if removed > 0:
            logger.debug(f"插件 >>> 已移除插件 {module_full_name} 的 {removed} 个处理器")
        return removed

    def _collect_commands_for_module(self, module_name: str) -> List[str]:
        """
        扫描全局命令注册表，找出属于指定模块的所有命令名
        """
        from app.modules import handlers  # 导入你的全局注册表
        
        collected = []
        for h in handlers.get("command", []):
            func = h.get("func")
            if func is None:
                continue
            
            # 通过 __module__ 判断该函数属于哪个插件文件
            if func.__module__ == module_name:
                collected.append(h["name"])
        
        return collected

    def _load_local_packages(self):
        """
        扫描 plugins/ 下的子文件夹，将其作为 Python 包导入
        """
        if str(self.plugin_dir.parent) not in sys.path:
            sys.path.insert(0, str(self.plugin_dir.parent))
        IGNORE_DIRS = {"__pycache__", ".git", ".idea", ".vscode", "tests", "docs", "dist", "build"}
        for item in self.plugin_dir.iterdir():
            if not item.is_dir():
                continue
            if item.name.startswith(".") or item.name in IGNORE_DIRS:
                continue
            init_file = item / "__init__.py" # 检查是否是有效的 Python 包（有 __init__.py）
            if not init_file.exists():
                logger.warning(f"插件 >>> 目录 {item.name} 缺少 __init__.py，跳过")
                continue
            # 构建包名：假设 plugins 的父目录是项目根目录
            # 如果 plugins 在项目根目录下，包名就是 plugins.{folder_name}
            package_name = f"{self.plugin_dir.name}.{item.name}"
            try:
                module = importlib.import_module(package_name)# 动态导入该包（会执行 __init__.py 中的装饰器）
                if hasattr(module, "__meta__") and isinstance(module.__meta__, PluginMetadata): # 提取元数据
                    meta = module.__meta__
                    meta.module_name = package_name  # 记录模块名，用于移除
                    if not meta.commands: # 自动填充命令
                        meta.commands = self._collect_commands_for_module(package_name)
                    metadata_registry[meta.name] = meta
                    logger.info(f"插件 >>> 从本地包加载插件: {meta.name} v{meta.version}")
                else:
                    meta = PluginMetadata( # 没有元数据的包，使用默认值
                        name=item.name,
                        version="0.0.1",
                        description=f"本地插件（未声明元数据）",
                        module_name=package_name
                    )
                    metadata_registry[meta.name] = meta
                    logger.warning(f"插件 >>> 本地包 {item.name} 未定义 __meta__，使用默认值")
            except Exception as e:
                logger.error(f"插件 >>> 加载本地包 {item.name} 失败: {e}")

    def _load_entry_point_plugins(self):
        """
        扫描 'axtbot.plugins' 这个命名空间下的所有入口点
        """
        eps = entry_points(group="axtbot.plugins")  # Python 3.10+ 语法
        for ep in eps:
            try:
                # ep.name 是插件名（如 'weather'）
                # ep.value 是字符串 'axtbot_plugin_weather:__meta__'
                # load() 会导入该包并返回 __meta__ 对象
                meta = ep.load()  
                # 确保它是 PluginMetadata 实例
                if not isinstance(meta, PluginMetadata):
                    logger.warning(f"插件 >>> 入口点 {ep.name} 未返回有效的 PluginMetadata，跳过")
                    continue
                # 存入全局注册表（如果已存在同名插件，覆盖或合并）
                if meta.name in metadata_registry:
                    logger.warning(f"插件 {meta.name} 已存在，将被覆盖")
                metadata_registry[meta.name] = meta
                logger.info(f"插件 >>> 从 PyPI 加载插件: {meta.name} v{meta.version}")
            except Exception as e:
                logger.error(f"加载入口点 {ep.name} 失败: {e}")

    def load_all(self):
        metadata_registry.clear()
        from app.modules import handlers
        self._load_local_packages()
        if self.load_from_entry_points:
            self._load_entry_point_plugins()
        self._check_and_clean_dependencies()
        logger.info(f"插件 >>> 已加载 {len(handlers['command'])} 个命令，{len(handlers['message'])} 个消息处理器")
        logger.info(f"插件 >>> 加载完成，共 {len(metadata_registry)} 个插件")

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
            await asyncio.wait_for(func(event), timeout=60.0)
        else:
            # 同步函数：扔到线程池执行
            await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(_executor, func, event),
                timeout=60.0,
            )
    except asyncio.TimeoutError:
        logger.error(f"处理器 {func.__name__} 执行超时（>60秒），已放弃")
    except Exception as e:
        logger.error(f"处理器 {func.__name__} 执行报错: {e}")
    return None