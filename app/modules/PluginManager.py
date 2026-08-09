"""
Module for Plugins Hook/UnHook Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from __future__ import annotations

import asyncio
import importlib
import inspect
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import entry_points
from pathlib import Path
from typing import Dict, List

from app.classes import (
    GroupMessage,
    Message,
    PluginMetadata,
    PrivateMessage,
    QQInteraction,
    SessionManager,
)
from app.modules import config_loader, get_db, logger

metadata_registry: Dict[str, PluginMetadata] = {}
db = get_db()
_sync_executor: ThreadPoolExecutor | None = None


class PluginManager:
    def __init__(self, load_from_entry_points=True):
        core_config = config_loader.get_core_config()
        self.plugins_dir = Path(core_config.plugins_dir)
        self.disabled_plugins = core_config.disable_plugins
        self.command_timeout = core_config.command_timeout
        self.load_from_entry_points = load_from_entry_points
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            logger.warning("插件 >>> 插件目录不存在，已生成目录")

    def _check_and_clean_dependencies(self):
        disabled_plugins = []
        for plugin_name, meta in list(metadata_registry.items()):
            missing_deps = [dep for dep in meta.dependencies if dep not in metadata_registry]
            if missing_deps:
                logger.error(
                    f"插件 >>> 插件 '{plugin_name}'({meta.module_name}) 缺少依赖: {', '.join(missing_deps)}，已禁用"
                )
                disabled_plugins.append(plugin_name)
                del metadata_registry[plugin_name]
                self._remove_handlers_by_module(meta.module_name)
        if disabled_plugins:
            logger.warning(f"插件 >>> 已禁用插件: {', '.join(disabled_plugins)}")

    def _remove_handlers_by_module(self, module_full_name: str):
        from app.modules import handlers

        removed = 0
        for key in ("command", "message", "all", "interaction"):
            if key not in handlers:
                continue
            before_count = len(handlers[key])
            handlers[key] = [h for h in handlers[key] if h["func"].__module__ != module_full_name]
            removed += before_count - len(handlers[key])

        if removed > 0:
            logger.debug(f"插件 >>> 已移除插件 {module_full_name} 的 {removed} 个处理器")
        return removed

    def _collect_commands_for_module(self, module_name: str) -> List[str]:
        from app.modules import handlers

        collected: List[str] = []
        for h in handlers.get("command", []):
            func = h.get("func")
            if func is not None and func.__module__ == module_name:
                collected.append(h["name"])
        return collected

    def _load_local_packages(self):
        if str(self.plugins_dir.parent) not in sys.path:
            sys.path.insert(0, str(self.plugins_dir.parent))

        ignore_dirs = {"__pycache__", ".git", ".idea", ".vscode", "tests", "docs", "dist", "build"}
        for item in self.plugins_dir.iterdir():
            if not item.is_dir() or item.name.startswith(".") or item.name in ignore_dirs:
                continue

            init_file = item / "__init__.py"
            if not init_file.exists():
                logger.warning(f"插件 >>> 目录 {item.name} 缺少 __init__.py，跳过")
                continue

            package_name = f"{self.plugins_dir.name}.{item.name}"
            try:
                module = importlib.import_module(package_name)
                if hasattr(module, "__meta__") and isinstance(module.__meta__, PluginMetadata):
                    meta = module.__meta__
                    meta.module_name = package_name
                    if not meta.commands:
                        meta.commands = self._collect_commands_for_module(package_name)
                    if meta.name in self.disabled_plugins:
                        logger.info(f"插件 >>> 插件 '{meta.name}' 在禁用列表中，跳过加载")
                        continue
                    metadata_registry[meta.name] = meta
                    logger.info(f"插件 >>> 从本地包加载插件: {meta.name} v{meta.version}")
                else:
                    meta = PluginMetadata(
                        name=item.name,
                        version="0.0.1",
                        description="本地插件（未声明元数据）",
                        module_name=package_name,
                    )
                    if meta.name in self.disabled_plugins:
                        logger.info(f"插件 >>> 插件 '{meta.name}' 在禁用列表中，跳过加载")
                        continue
                    metadata_registry[meta.name] = meta
                    logger.warning(f"插件 >>> 本地包 {item.name} 未定义 __meta__，使用默认值")
            except Exception as e:
                logger.error(f"插件 >>> 加载本地包 {item.name} 失败: {e}")

    def _load_entry_point_plugins(self):
        eps = entry_points(group="axtbot.plugins")
        for ep in eps:
            try:
                meta = ep.load()
                if not isinstance(meta, PluginMetadata):
                    logger.warning(f"插件 >>> 入口点 {ep.name} 未返回有效的 PluginMetadata，跳过")
                    continue
                if meta.name in self.disabled_plugins:
                    logger.info(f"插件 >>> 插件 '{meta.name}' 在禁用列表中，跳过加载")
                    continue
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


async def dispatch(event):
    if isinstance(event, (Message, GroupMessage, PrivateMessage)):
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
        session.resolve(event)
        return

    openid = db.get_frame_config_by_key("bot_union_openid").value
    at = f"<@{openid}>"
    msg = event.content
    if at in msg:
        msg = msg.replace(at, "")
        event.is_you = True
    msg = re.sub(r"^ +", "", msg)
    event.content = msg

    for h in handlers["all"]:
        if isinstance(event, h["event_type"]):
            await _run_handler(h["func"], event)

    if msg.startswith("/"):
        cmd = msg[1:].split()[0]
        for h in handlers["command"]:
            if h["name"] == cmd and isinstance(event, h["event_type"]):
                await _run_handler(h["func"], event)
                return

    for h in handlers["message"]:
        if h["keyword"] in msg and isinstance(event, h["event_type"]):
            await _run_handler(h["func"], event)
            return

    logger.debug(f"插件处理器 >>> 未匹配到任何处理器 {msg}")


async def _dispatch_interaction(event: QQInteraction):
    from app.modules import handlers

    for h in handlers["interaction"]:
        if h["type"] is not None and h["type"] != event.data.type:
            continue
        if isinstance(event, h["event_type"]):
            await _run_handler(h["func"], event)
            break


async def _run_handler(func, event):
    """统一执行器：兼容同步/异步函数，带超时和异常捕获"""
    config = config_loader.get_core_config()
    global _sync_executor

    if _sync_executor is None or _sync_executor._max_workers != config.max_workers:
        if _sync_executor is not None:
            _sync_executor.shutdown(wait=False, cancel_futures=True)
        _sync_executor = ThreadPoolExecutor(max_workers=config.max_workers)

    try:
        if inspect.iscoroutinefunction(func):
            await asyncio.wait_for(func(event), timeout=config.command_timeout)
        else:
            await asyncio.wait_for(
                asyncio.get_running_loop().run_in_executor(_sync_executor, func, event),
                timeout=config.command_timeout,
            )
    except asyncio.TimeoutError:
        logger.error(f"处理器 {func.__name__} 执行超时（{config.command_timeout}秒），已放弃")
    except Exception as e:
        logger.error(f"处理器 {func.__name__} 执行报错: {e}")
        raise

