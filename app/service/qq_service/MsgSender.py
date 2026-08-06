"""
Core File for Sending QQ Messages

Author: Shanshui2024
Organization: AxT-Team

参考文档：
  https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_groups_group_openid_messages.post.html
  https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_users_openid_messages.post.html

本模块提供：
  - send_group_message()  → 发送群聊消息
  - send_c2c_message()    → 发送私聊消息
  - send_message()        → 通用发送（可指定任意 URL）
  - reply_group_message() → 快捷回复群聊（自动填写 msg_id）
  - reply_c2c_message()   → 快捷回复私聊（自动填写 msg_id）
"""

import aiohttp
from typing import Optional

from app.classes import Sender, GroupMessage, PrivateMessage
from app.modules import logger


API_BASE = "https://api.bot.qq.com"


# ============================================================
#  通用发送
# ============================================================

async def _do_send(url: str, payload: dict, headers: dict) -> Optional[dict]:
    """
    底层 HTTP 发送逻辑。

    Returns:
        dict  : 成功时返回响应 JSON
        None  : 失败时返回 None（已记录日志）
    """
    try:
        logger.debug(f"发信 >>> 尝试执行发信 {payload} 至 {url}")
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=5) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data
                else:
                    logger.error(
                        f"发信 >>> 发送失败 HTTP {resp.status}: {data}"
                    )
                    return None
    except aiohttp.ClientError as e:
        logger.error(f"发信 >>> 网络请求异常: {e}")
        return None
    except Exception as e:
        logger.error(f"发信 >>> 未知异常: {e}")
        return None


def _get_headers() -> dict:
    """获取带鉴权的请求头"""
    from app.service.qq_service.AccessToken import accesstoken
    return {
        "Authorization": f"QQBot {accesstoken.access_token}",
        "Content-Type": "application/json",
    }


async def send_message(url: str, sender: Sender) -> Optional[dict]:
    """
    向指定 URL 发送消息。这是底层方法，上层可按平台调用。

    Args:
        url    : 完整的 API 地址
        sender : 已构建好的 Sender 对象

    Returns:
        dict | None : 成功返回 API 响应，失败返回 None
    """
    payload = sender.model_dump(exclude_none=True)
    headers = _get_headers()
    return await _do_send(url, payload, headers)


# ============================================================
#  群聊消息
# ============================================================

async def send_group_message(
    group_openid: str,
    sender: Sender,
) -> Optional[dict]:
    """
    向指定群聊发送消息。

    Args:
        group_openid : 群 OpenID
        sender       : 消息内容（Sender 对象）

    Returns:
        dict | None : 成功返回 {id, timestamp, ...}，失败返回 None

    Example:
        sender = Sender(content="Hello!")
        result = await send_group_message("GROUP_OPENID_XXX", sender)
    """
    url = f"{API_BASE}/v2/groups/{group_openid}/messages"
    return await send_message(url, sender)


async def reply_group_message(
    msg: GroupMessage,
    content: str,
    msg_type: int = 0,
    msg_seq: int = 1,
) -> Optional[dict]:
    """
    快捷回复群聊消息：传入收到的 GroupMessage 即可自动填写 msg_id。

    Args:
        msg      : 收到的群聊消息对象（用于提取 msg_id / group_openid）
        content  : 回复文本内容
        msg_type : 消息类型，默认 0（纯文本）
        msg_seq  : 回复序号，默认 1

    Returns:
        dict | None
    """
    sender = Sender(
        msg_type=msg_type,
        content=content,
        msg_id=msg.id,
        msg_seq=msg_seq,
    )
    return await send_group_message(msg.group_openid, sender)


# ============================================================
#  私聊消息
# ============================================================

async def send_c2c_message(
    openid: str,
    sender: Sender,
) -> Optional[dict]:
    """
    向指定用户发送私聊消息。

    Args:
        openid : 用户 OpenID
        sender : 消息内容（Sender 对象）

    Returns:
        dict | None
    """
    url = f"{API_BASE}/v2/users/{openid}/messages"
    return await send_message(url, sender)


async def reply_c2c_message(
    msg: PrivateMessage,
    content: str,
    msg_type: int = 0,
    msg_seq: int = 1,
) -> Optional[dict]:
    """
    快捷回复私聊消息：传入收到的 PrivateMessage 即可自动填写 msg_id。

    Args:
        msg      : 收到的私聊消息对象（用于提取 msg_id / author.union_openid）
        content  : 回复文本内容
        msg_type : 消息类型，默认 0（纯文本）
        msg_seq  : 回复序号，默认 1

    Returns:
        dict | None
    """
    sender = Sender(
        msg_type=msg_type,
        content=content,
        msg_id=msg.id,
        msg_seq=msg_seq,
    )
    return await send_c2c_message(msg.author.union_openid, sender)


