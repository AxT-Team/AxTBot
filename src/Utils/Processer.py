from typing import Union

from src.Utils.EventClass import MessageEventPayload, GroupEvent
from src.Utils.PluginBase import get_command_handler, get_group_add_handler, get_interaction_handler, get_friend_add_handler
from src.Utils.Logger import logger
from src.Utils.EventSenderApp import MessageStore

async def handle_event(payload: Union[MessageEventPayload, GroupEvent]):
    """处理消息事件"""
    # 获取命令处理器（使用全局状态）
    if payload.t in ["MESSAGE_CREATE","AT_MESSAGE_CREATE","DIRECT_MESSAGE_CREATE","C2C_MESSAGE_CREATE","GROUP_AT_MESSAGE_CREATE"]:
        logger.debug(f"插件管理器 >>> 处理消息: {payload.content}")
        await MessageStore.save_from_event(payload)
        # 解析命令
        parts = payload.content.strip().split(maxsplit=1)
        if not parts:
            return "错误: 空消息"
        command = parts[0].lower()
        # 获取命令处理器
        handler = await get_command_handler(command, type(payload))
        if not handler:
            return f"未知命令: {command}"
        try:
            await handler(payload)
            return
        except Exception as e:
            error_msg = f"执行命令 {command} 出错: {str(e)}"
            logger.error(f"插件管理器 >>> {error_msg}")
            raise # 受不了了，直接抛出异常方便debug。。。
    else:
        logger.debug(f"插件管理器 >>> 处理事件: {payload.event_type}")
        if payload.t == "GROUP_ADD_ROBOT":
            handler = await get_group_add_handler()
            if handler is None:
                logger.warning(f"插件管理器 >>> 未找到 GROUP_ADD_ROBOT 的处理器")
                return
            try:
                await handler(payload)
                return
            except Exception as e:
                error_msg = f"处理事件 {payload.event_type} 出错: {str(e)}"
                logger.error(f"插件管理器 >>> {error_msg}")
                raise
        elif payload.t == "GROUP_DEL_ROBOT":
            # 目前不处理退群事件
            return
        elif payload.t == "FRIEND_ADD":
            handler = await get_friend_add_handler()
            if handler is None:
                logger.warning(f"插件管理器 >>> 未找到 FRIEND_ADD 的处理器")
                return
            try:
                await handler(payload)
            except Exception as e:
                error_msg = f"处理事件 {payload.event_type} 出错: {str(e)}"
                logger.error(f"插件管理器 >>> {error_msg}")
                raise
        elif payload.t == "INTERACTION_CREATE":
            handler = await get_interaction_handler()
            if handler is None:
                logger.warning(f"插件管理器 >>> 未找到 INTERACTION_CREATE 的处理器")
                return
            try:
                await handler(payload)
            except Exception as e:
                error_msg = f"处理事件 {payload.event_type} 出错: {str(e)}"
                logger.error(f"插件管理器 >>> {error_msg}")
                raise
        else:
            pass