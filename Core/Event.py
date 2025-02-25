import importlib
import os
from Core.Auth import auth
from typing import Callable, Dict, List
from functools import wraps
import aiohttp, asyncio
import re
from Core.Logger import logger
from Core.Config import config
from typing import Optional, List

# 用于存储插件的字典，按事件类型分组
plugin_registry: Dict[str, Dict[str, List[Callable]]] = {
    "group": {},
    "private": {},
    "channel": {},
    "private_channel": {},
    "generic": []
}

# 线程安全的全局消息计数字典
message_count: Dict[str, int] = {}
message_count_lock = asyncio.Lock()

def group_handle_event(*commands):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(event):
            await func(event)

        # 注册命令
        for command in commands:
            if command not in plugin_registry["group"]:
                plugin_registry["group"][command] = []
            plugin_registry["group"][command].append(wrapper)
            logger.debug(f"框架 >>> 注册群聊事件处理器：{command}")
        return wrapper
    return decorator


def private_handle_event(*commands):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(event):
            await func(event)

        # 注册命令到私聊命名空间
        for command in commands:
            if command not in plugin_registry["private"]:
                plugin_registry["private"][command] = []
            plugin_registry["private"][command].append(wrapper)
            logger.debug(f"框架 >>> 注册私聊事件处理器：{command}")
        return wrapper
    return decorator


def channel_handle_event(*commands):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(event):
            await func(event)

        # 注册命令到频道命名空间
        for command in commands:
            if command not in plugin_registry["channel"]:
                plugin_registry["channel"][command] = []
            plugin_registry["channel"][command].append(wrapper)
            logger.debug(f"框架 >>> 注册频道事件处理器：{command}")
        return wrapper
    return decorator

def pchannel_handle_event(*commands):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(event):
            await func(event)

        # 注册命令到频私命名空间
        for command in commands:
            if command not in plugin_registry["private_channel"]:
                plugin_registry["private_channel"][command] = []
            plugin_registry["private_channel"][command].append(wrapper)
            logger.debug(f"框架 >>> 注册频私事件处理器：{command}")
        return wrapper
    return decorator

def generic_handle_event():
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(event):
            await func(event)

        # 注册通用事件处理器
        if "generic" not in plugin_registry:
            plugin_registry["generic"] = []
        plugin_registry["generic"].append(wrapper)
        logger.debug(f"框架 >>> 注册通用事件处理器")
        return wrapper
    return decorator







async def load_plugins(plugins_dir: str = config.plugins_dir):
    """
    加载插件函数，用于动态加载目录下的插件

    Args:
        plugins_dir (str): 插件目录路径

    Returns:
        None
    """
    plugins_dir = re.sub(r'^(\.\/|\.\\)', '', plugins_dir)
    plugins_dir = re.sub(r'[\/\\]', '.', plugins_dir)
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            logger.debug(f"框架 >>> 加载插件 {module_name}")
            importlib.import_module(f"{plugins_dir}.{module_name}")

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
        channel_id (str): 子频道 ID（如果适用）
        guild_id (str): 频道 ID（如果适用）
        user_id (int): 用户ID（如果适用）
        seq (int): 消息序列号（如果适用）
        event_type (str): 事件类型
    """

    def __init__(self, msg_id: str, content: str, timestamp: str, author: dict, attachments: Optional[List] = None, group_openid: Optional[str] = None, channel_id: Optional[str] = None, guild_id: Optional[str] = None, user_id: Optional[str] = None, seq: Optional[int] = None, event_type: Optional[str] = None):
        """
        初始化事件类

        Args:
            msg_id (str): 事件回传message_id，用于区分不同消息
            content (str): 用户消息
            timestamp (str): 事件时间戳
            author (dict): 发送者信息
            attachments (list): 富媒体文件附件
            group_openid (str): 群聊的 openid（如果适用）
            channel_id (str): 子频道 ID（如果适用）
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
    timestamp = event_data.get('timestamp', "")
    if event_type in ['GROUP_ADD_ROBOT','GROUP_DEL_ROBOT','GROUP_MSG_REJECT','GROUP_MSG_RECEIVE']:
        group_openid = event_data.get('group_openid', "")
        op_member_id = event_data.get('op_member_openid', "")
        logger.info(f'框架 >>> [事件类型:{event_type}][群:{group_openid}][操作成员:{op_member_id}]')
        return
    elif event_type in ['FRIEND_ADD','FRIEND_DEL','C2C_MSG_REJECT','C2C_MSG_RECEIVE']:
        op_member_id = event_data.get('openid', "")
        logger.info(f'框架 >>> [事件类型:{event_type}][用户:{op_member_id}]')
        return
    # 更新消息计数
    async with message_count_lock:
        if event_type not in message_count:
            message_count[event_type] = 0
        message_count[event_type] += 1
    event = Event(
        msg_id=event_data.get('id', ""),
        content=event_data.get('content', ""),
        timestamp=timestamp,
        author=event_data.get('author', {}),
        attachments=event_data.get('attachments', []),
        group_openid=event_data.get('group_openid', ""),
        channel_id=event_data.get('channel_id', ""),
        guild_id=event_data.get('guild_id', ""),
        user_id=event_data.get('author', {}).get('member_openid', ""),
        seq=event_data.get('seq', ""),
        event_type=event_type
    )
    await load_plugins()

    cleaned_content = re.sub(r'\s+$', '', event.content)
    split_content = re.split(r'\s', cleaned_content, maxsplit=1)
    key = split_content[0] if split_content else cleaned_content


    # 调用通用事件处理器
    if "generic" in plugin_registry:
        for handler in plugin_registry["generic"]:
            await handler(event)

    if event_type == "C2C_MESSAGE_CREATE":
        # 私聊消息
        user_id = event.author.get('user_openid')
        logger.info(f'框架 >>> [私聊消息][用户:{user_id}][MsgID:{event.msg_id}] >>> {event.content}')
        if key in plugin_registry["private"]:
            for handler in plugin_registry["private"][key]:
                await handler(event)
        else:
            logger.debug(f"无事件处理器，当前处理器：" + str(list(plugin_registry["private"].keys())))
    elif event_type == "GROUP_AT_MESSAGE_CREATE":
        # 群聊 @ 机器人消息
        user_id = event.author.get('member_openid')
        group_id = event.group_openid
        logger.info(f'框架 >>> [群聊消息][群组:{group_id}][用户:{user_id}][MsgID:{event.msg_id}] >>> {event.content}')
        if key in plugin_registry["group"]:
            for handler in plugin_registry["group"][key]:
                await handler(event)
        else:
            logger.debug(f"无事件处理器，当前处理器：" + str(list(plugin_registry["group"].keys())))
    elif event_type == "DIRECT_MESSAGE_CREATE":
        # 频道私信消息
        user_id = event.author.get('id')
        logger.info(f'框架 >>> [频道私信][用户:{user_id}][MsgID:{event.msg_id}] >>> {event.content}')
        if key in plugin_registry["private_channel"]:
            for handler in plugin_registry["private_channel"][key]:
                await handler(event)
        else:
            logger.debug(f"无事件处理器，当前处理器：" + str(list(plugin_registry["private_channel"].keys())))
    elif event_type == "AT_MESSAGE_CREATE":
        # 文字子频道 @ 机器人消息
        user_id = event.author.get('id')
        channel_id = event.channel_id
        logger.info(f'框架 >>> [频道消息][频道:{channel_id}][用户:{user_id}][MsgID:{event.msg_id}] >>> {event.content}')
        if key in plugin_registry["channel"]:
            for handler in plugin_registry["channel"][key]:
                await handler(event)
        else:
            logger.debug(f"无事件处理器，当前处理器：" + str(list(plugin_registry["channel"].keys())))
    else:
        # 未知消息
        logger.info(f'框架 >>> [未知消息][用户未知][MsgID:{event.msg_id}] >>> {event.content}')


async def get_message_count(event_type: str) -> int:
    """
    获取指定消息类型的总消息数（线程安全）
    """
    async with message_count_lock:
        return int(message_count.get(event_type, 0))



async def send_group_message(group_openid: str, msg_type: int, content: str, msg_id: str, msg_seq: Optional[int] = None, event_id: Optional[str]=None, markdown: Optional[str]=None, ark=None, embed=None, media=None, depth: int = 0) -> tuple[str , str]:
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
    logger.debug(f"框架 >>> [SEND MESSAGE] 发送消息到群组: {group_openid}, 消息类型: {msg_type}, 消息内容: {content}")
    url = f"https://api.sgroup.qq.com/v2/groups/{group_openid}/messages"
    access_token = auth.get_current_access_token()
    headers = {
        "Authorization": f"QQBot {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "msg_type": msg_type
    }

    # 根据消息类型动态添加参数
    if msg_type == 0:  # 文本消息
        data["content"] = str(content) if content else "" # type: ignore
    elif msg_type == 2:  # Markdown 消息
        data["markdown"] = markdown # type: ignore
    elif msg_type == 3:  # Ark 消息
        data["ark"] = ark # type: ignore
    elif msg_type == 4:  # Embed 消息
        data["embed"] = embed # type: ignore
    elif msg_type == 7:  # 富媒体消息
        data["media"] = media # type: ignore
        data["content"] = " "  # 当 msg_type=7 时，content 字段需要填入一个值，如空格  # type: ignore

    # 添加可选参数
    if msg_id:
        data["msg_id"] = msg_id # type: ignore
    if msg_seq:
        data["msg_seq"] = msg_seq
    if event_id:
        data["event_id"] = event_id # type: ignore

    if depth > 5:  # 限制递归深度
        logger.error(f"递归调用深度超限！尝试发送{content}次数大于五次！")
        return ("", "")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    messages = await response.json()
                    return_id = messages['id']
                    timestamp = messages['timestamp']
                    logger.debug(f"框架 >>> 群聊消息发送成功")
                    async with message_count_lock:
                        if "GROUP_AT_MESSAGE_SEND" not in message_count:
                            message_count["GROUP_AT_MESSAGE_SEND"] = 0
                        message_count["GROUP_AT_MESSAGE_SEND"] += 1
                    return (return_id, timestamp)
                else:
                    message = await response.json()
                    return_code = message["code"]
                    return_errcode = message["errcode"] if message.get('errcode') else "未知错误码"
                    traceid = message["trace_id"]
                    if message['message'] == 'invalid file_info':
                        logger.error(f'框架 >>> 文件发送失败：无效的file info回传！返回码：{return_code}，错误码：{return_errcode}，TraceID：{traceid}')
                    elif message['message'] == '消息被去重，请检查请求msgseq':
                        logger.error(f'框架 >>> 群聊消息发送失败：消息被去重！返回码：{return_code}，错误码：{return_errcode}，TraceID：{traceid}')
                    elif str(message['message']).startswith('消息发送失败, 不允许发送url'):
                        logger.error(f'框架 >>> 群聊消息发送失败：不允许发送url！返回码：{return_code}，错误码：{return_errcode}，TraceID：{traceid}')
                        logger.warning(f'框架 >>> 尝试重新发送消息...')
                        await send_group_message(group_openid, 0, content.replace(message['message'][17:], message['message'][17:].replace('.', ',')), msg_id, depth=depth + 1)
                    elif message['message'] == '请求数据异常':
                        logger.error(f'框架 >>> 群聊消息发送失败：请求数据异常！返回码：{return_code}，错误码：{return_errcode}，TraceID：{traceid}')
                    elif message['message'] == 'msgid已经过期,不能回复':
                        logger.error(f'框架 >>> 群聊消息发送失败：msgid已经过期,不能回复！返回码：{return_code}，错误码：{return_errcode}，TraceID：{traceid}')
                    else:
                        logger.error(f"框架 >>> 群聊消息发送失败: {await response.text()}")
                    return ("", "")
    except asyncio.TimeoutError:
        logger.error("网络请求超时")
        return ("", "")
    except asyncio.exceptions.CancelledError:
        logger.error("网络请求被取消")
        return ("", "")
    except Exception as e:
        logger.error(f"发送消息时发生错误：{e}")
        return ("", "")
    

async def upload_media(group_openid, file_type: int, url: str, srv_send_msg: bool) -> tuple[str, int]:
    """
    上传媒体资源到群聊并获取 file_info

    :param group_openid: 群聊的 openid

    :param file_type: 媒体类型（1: 图片, 2: 视频, 3: 语音）

    :param url: 媒体资源的 URL

    :param srv_send_msg: 是否直接发送消息（True/False）

    :return: 返回整个组
    """
    api_url = f"https://api.sgroup.qq.com/v2/groups/{group_openid}/files"
    access_token = auth.get_current_access_token()
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
                return response_data, 1
            else:
                message = await response.json()
                return_msg = message["message"]
                return_code = message["code"]
                return_errcode = message["errcode"] if message.get('errcode') else "未知错误码"
                traceid = message["trace_id"]
                logger.error(f"框架 >>> 上传媒体资源失败！返回码：{return_code}，错误码：{return_errcode}，错误描述：{return_msg}，TraceID：{traceid}")
                return message, 0