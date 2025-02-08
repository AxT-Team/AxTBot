import importlib
import os
from Core.Auth import get_current_access_token
from typing import Callable, Dict, List
from functools import wraps
import aiohttp
import re
from Core.Logger import logger

# 用于存储插件的字典
plugin_registry: Dict[str, List[Callable]] = {}


def group_handle_event(*commands):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(event):
            await func(event)

        # 注册命令
        for command in commands:
            if command not in plugin_registry:
                plugin_registry[command] = []
            plugin_registry[command].append(wrapper)
            logger.debug(f"框架 >>> 注册事件处理器：{command}")
        return wrapper
    return decorator

async def load_plugins():
    plugin_dir = "plugins"
    for filename in os.listdir(plugin_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            importlib.import_module(f"{plugin_dir}.{module_name}")
            logger.debug(f"框架 >>> 加载插件 {module_name}")

class Event:
    """
    封装事件类，用于消息信息传递

    Attributes:
        msg_id (str): 事件回传message_id，用于区分不同消息
        content (str): 用户消息
        timestamp (str): 事件时间戳
        author (dict): 发送者信息
        attachments (list): 富媒体文件附件
        group_openid (str): 群聊的 openid（如果适用）
        channel_id (str): 频道 ID（如果适用）
        guild_id (str): 频道 ID（如果适用）
        user_id (int): 用户ID（如果适用）
        seq (int): 消息序列号（如果适用）
        event_type (str): 事件类型
    """

    def __init__(self, msg_id: str, content: str, timestamp: str, author: dict, attachments: list = None, group_openid: str = None, channel_id: str = None, guild_id: str = None, user_id: str = None, seq: int = None, event_type: str = None):
        """
        初始化事件类

        Args:
            msg_id (str): 事件回传message_id，用于区分不同消息
            content (str): 用户消息
            timestamp (str): 事件时间戳
            author (dict): 发送者信息
            attachments (list): 富媒体文件附件
            group_openid (str): 群聊的 openid（如果适用）
            channel_id (str): 频道 ID（如果适用）
            guild_id (str): 频道 ID（如果适用）
            user_id (int): 用户ID（如果适用）
            seq (int): 消息序列号（如果适用）
            event_type (str): 事件类型
        """
        self.msg_id = msg_id
        self.content = re.sub(r'^\s+', '', content)
        self.timestamp = timestamp
        self.author = author
        self.attachments = attachments if attachments else []
        self.group_openid = group_openid
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.user_id = user_id
        self.seq = seq
        self.event_type = event_type

    def __str__(self):
        """
        返回事件的字符串表示

        Returns:
            str: 格式化的字符串，包含事件详情
        """
        return (f"Event(msg_id={self.msg_id}, content='{self.content}', timestamp={self.timestamp}, "
                f"author={self.author}, attachments={self.attachments}, group_openid={self.group_openid}, "
                f"channel_id={self.channel_id}, guild_id={self.guild_id}, user_id={self.user_id}, seq={self.seq}, event_type={self.event_type})")

async def handle_event(event_type: str, event_data: dict) -> None:
    """
    处理事件

    Args:
        event_type (str): 事件类型
        event_data (dict): 事件数据的字典
    """
    event = Event(
        msg_id=event_data.get('id'),
        content=event_data.get('content'),
        timestamp=event_data.get('timestamp'),
        author=event_data.get('author'),
        attachments=event_data.get('attachments', []),
        group_openid=event_data.get('group_openid'),
        channel_id=event_data.get('channel_id'),
        guild_id=event_data.get('guild_id'),
        user_id=event_data.get('author').get('member_openid', ""),
        seq=event_data.get('seq'),
        event_type=event_type
    )
    await load_plugins()
    if event_type == "C2C_MESSAGE_CREATE":
        # 私聊消息
        user_id = event.author.get('user_openid')
        logger.info(f'框架 >>> [私聊消息][用户:{user_id}][MsgID:{event.msg_id}] >>> {event.content}')
    elif event_type == "GROUP_AT_MESSAGE_CREATE":
        # 群聊 @ 机器人消息
        user_id = event.author.get('member_openid')
        group_id = event.group_openid
        logger.info(f'框架 >>> [群聊消息][群组:{group_id}][用户:{user_id}][MsgID:{event.msg_id}] >>> {event.content}')
        cleaned_content = re.sub(r'\s+$', '', event.content)
        split_content = re.split(r'\s', cleaned_content, maxsplit=1)
        key = split_content[0] if split_content else cleaned_content
        if key in list(plugin_registry.keys()):
            for handler in plugin_registry[key]:
                await handler(event)
        else:
            logger.info(f"无事件处理器，当前处理器：" + str(list(plugin_registry.keys())))
    elif event_type == "DIRECT_MESSAGE_CREATE":
        # 频道私信消息
        user_id = event.author.get('id')
        logger.info(f'框架 >>> [频道私信][用户:{user_id}][MsgID:{event.msg_id}] >>> {event.content}')
    elif event_type == "AT_MESSAGE_CREATE":
        # 文字子频道 @ 机器人消息
        user_id = event.author.get('id')
        channel_id = event.channel_id
        logger.info(f'框架 >>> [频道消息][频道:{channel_id}][用户:{user_id}][MsgID:{event.msg_id}] >>> {event.content}')
    else:
        # 未知消息
        logger.info(f'框架 >>> [未知消息][用户未知][MsgID:{event.msg_id}] >>> {event.content}')









async def send_group_message(group_openid: str, msg_type: int, content: str, msg_id: str, msg_seq=None, event_id=None, markdown=None, ark=None, embed=None, media=None):
    """
    发送群聊消息，支持多种消息类型

    :param group_openid: 群聊的 openid

    :param msg_type: 消息类型

        - 0: 文本消息
        - 2: Markdown 消息
        - 3: Ark 消息
        - 4: Embed 消息
        - 7: 富媒体消息

    :param content: 文本内容（仅在 msg_type=0 时使用）

    :param markdown: Markdown 对象（仅在 msg_type=2 时使用）

    :param ark: Ark 对象（仅在 msg_type=3 时使用）

    :param embed: Embed 对象（仅在 msg_type=4 时使用）

    :param media: 富媒体对象（仅在 msg_type=7 时使用）

    :param msg_id: 前置收到的用户发送过来的消息 ID，用于发送被动消息（回复）

    :param msg_seq: 回复消息的序号，与 msg_id 联合使用
    
    :param event_id: 前置收到的事件 ID，用于发送被动消息
    """

    logger.event(f"框架 >>> [SEND MESSAGE] 发送消息到群组: {group_openid}, 消息类型: {msg_type}, 消息内容: {content}")
    url = f"https://api.sgroup.qq.com/v2/groups/{group_openid}/messages"
    access_token = get_current_access_token()
    headers = {
        "Authorization": f"QQBot {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "msg_type": msg_type
    }

    # 根据消息类型动态添加参数
    if msg_type == 0:  # 文本消息
        data["content"] = content
    elif msg_type == 2:  # Markdown 消息
        data["markdown"] = markdown
    elif msg_type == 3:  # Ark 消息
        data["ark"] = ark
    elif msg_type == 4:  # Embed 消息
        data["embed"] = embed
    elif msg_type == 7:  # 富媒体消息
        data["media"] = media
        data["content"] = " "  # 当 msg_type=7 时，content 字段需要填入一个值，如空格

    # 添加可选参数
    if msg_id:
        data["msg_id"] = msg_id
    if msg_seq:
        data["msg_seq"] = msg_seq
    if event_id:
        data["event_id"] = event_id

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                logger.debug("框架 >>> 群聊消息发送成功")
            else:
                logger.error(f"框架 >>> 群聊消息发送失败: {await response.text()}")

async def upload_media(group_openid, file_type: int, url: str, srv_send_msg: bool):
    """
    上传媒体资源到群聊并获取 file_info

    :param group_openid: 群聊的 openid

    :param file_type: 媒体类型（1: 图片, 2: 视频, 3: 语音）

    :param url: 媒体资源的 URL

    :param srv_send_msg: 是否直接发送消息（True/False）

    :return: 返回的 file_info 和其他信息
    """
    api_url = f"https://api.sgroup.qq.com/v2/groups/{group_openid}/files"
    access_token = get_current_access_token()
    headers = {
        "Authorization": f"QQBot {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "file_type": file_type,
        "url": url,
        "srv_send_msg": srv_send_msg
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, headers=headers, json=data) as response:
            if response.status == 200:
                response_data = await response.json()
                logger.debug(f"框架 >>> 上传媒体资源成功: {response_data}")
                return response_data
            else:
                logger.error(f"框架 >>> 上传媒体资源失败: {await response.text()}")
                return None