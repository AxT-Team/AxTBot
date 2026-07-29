"""
Message Processing Service for QQ Bot

Author: Shanshui2024
Organization: AxT-Team
"""
import asyncio

from app.classes import GroupMessage, BasePayload, PrivateMessage
from app.modules import logger, database, User, Group, dispatch, get_db

async def message_process(payload: BasePayload) -> None:
    """
    Message Processing Service for QQ Bot

    Args:
        payload (BasePayload): BasePayload Object

    Returns:
        None
    """
    is_you = None
    message = payload.d
    logger.debug(f"Received message payload: {message}")
    db = get_db()
    if payload.t == "GROUP_AT_MESSAGE_CREATE":
        msg = GroupMessage(**message)
        content = msg.content
        if msg.mentions:
            for mention in msg.mentions:
                content = content.replace("<@" + str(mention.id) + ">" , "[@" + mention.username + "]")
        if len(content) <= 50:
            pass
        else:
            half = 47 // 2
            content = content[:half] + "..." + content[-half:]
        log = f"传入消息 >>> [群聊AT | 群ID：{msg.group_openid}] | "
        if msg.author.bot:
            log += f"[BOT]{msg.author.username} > {content}"
        else:
            log += f"[{msg.author.member_role.capitalize()}]{msg.author.username} > {content}"
        if msg.attachments:
            for attachment in msg.attachments:
                if attachment.content_type.startswith("image/"):
                    log += f" [图片: {attachment.filename}]"
                elif attachment.content_type.startswith("video/"):
                    log += f" [视频: {attachment.filename}]"
                elif attachment.content_type.startswith("voice"):
                    log += f" [语音: {attachment.filename}]"
                else:
                    log += f" [附件: {attachment.content_type} - {attachment.filename}] "
        group: Group | None = database.get_group_by_id(msg.group_id)
        user: User | None = database.get_user_by_openid(msg.author.union_openid)
        if not group:
            database.add_group(Group(group_id=msg.group_id, message = 1, create_time=msg.timestamp, update_time=msg.timestamp))
        else:
            database.update_group(Group(group_id=msg.group_id, message = group.message + 1, update_time=msg.timestamp))
        if not user:
            database.add_user(User(user_openid=msg.author.union_openid, message = 1, create_time=msg.timestamp, update_time=msg.timestamp, nickname=msg.author.username))
        else:
            database.update_user(User(user_openid=msg.author.union_openid, message = user.message + 1, update_time=msg.timestamp, nickname=msg.author.username))
        logger.info(log)
        asyncio.create_task(dispatch(message))
    elif payload.t == "GROUP_MESSAGE_CREATE":
        msg = GroupMessage(**message)
        content = msg.content
        if msg.mentions:
            for mention in msg.mentions:
                content = content.replace("<@" + str(mention.id) + ">" , "[@" + mention.username + "]")
                if mention.is_you:
                    is_you = True
                    bot_username = db.get_frame_config_by_key("bot_username").key
                    content = content.replace(f"[@{bot_username}]", "")
        if len(content) <= 50:
            pass
        else:
            half = 47 // 2
            content = content[:half] + "..." + content[-half:]
        if is_you:
            log = f"传入消息 >>> [群聊AT | 群ID：{msg.group_openid}] | "
        else:
            log = f"传入消息 >>> [群聊消息 | 群ID：{msg.group_openid}] | "
        if msg.author.bot:
            log += f"[BOT]{msg.author.username} > {content}"
        else:
            log += f"[{msg.author.member_role.capitalize()}]{msg.author.username} > {content}"
        if msg.attachments:
            for attachment in msg.attachments:
                if attachment.content_type.startswith("image/"):
                    log += f" [图片: {attachment.filename}]"
                elif attachment.content_type.startswith("video/"):
                    log += f" [视频: {attachment.filename}]"
                elif attachment.content_type.startswith("voice"):
                    log += f" [语音: {attachment.filename}]"
                else:
                    log += f" [附件: {attachment.content_type} - {attachment.filename}] "
        group: Group | None = database.get_group_by_id(msg.group_id)
        user: User | None = database.get_user_by_openid(msg.author.union_openid)
        if not group:
            database.add_group(Group(group_id=msg.group_id, message = 1, create_time=msg.timestamp, update_time=msg.timestamp))
        else:
            database.update_group(Group(group_id=msg.group_id, message = group.message + 1, update_time=msg.timestamp))
        if not user:
            database.add_user(User(user_openid=msg.author.union_openid, message = 1, create_time=msg.timestamp, update_time=msg.timestamp, nickname=msg.author.username))
        else:
            database.update_user(User(user_openid=msg.author.union_openid, message = user.message + 1, update_time=msg.timestamp, nickname=msg.author.username))
        logger.info(log)
        asyncio.create_task(dispatch(message))
    elif payload.t == "C2C_MESSAGE_CREATE":
        msg = PrivateMessage(**message)
        text= msg.content
        if len(text) <= 50:
            pass
        else:
            half = 47 // 2
            text = text[:half] + "..." + text[-half:]
        log = f"传入消息 >>> [私聊消息] | "
        if msg.author.bot:
            log += f"[BOT]{msg.author.username} > {text}"
        else:
            log += f"{msg.author.username} > {text}"
        if msg.attachments:
            for attachment in msg.attachments:
                if attachment.content_type.startswith("image/"):
                    log += f" [图片: {attachment.filename}]"
                elif attachment.content_type.startswith("video/"):
                    log += f" [视频: {attachment.filename}]"
                elif attachment.content_type.startswith("voice"):
                    log += f" [语音: {attachment.filename}]"
                else:
                    log += f" [附件: {attachment.content_type} - {attachment.filename}]"
        user: User | None = database.get_user_by_openid(msg.author.union_openid)
        if not user:
            database.add_user(User(user_openid=msg.author.union_openid, message = 1, create_time=msg.timestamp, update_time=msg.timestamp, nickname=msg.author.username))
        else:
            database.update_user(User(user_openid=msg.author.union_openid, message = user.message + 1, update_time=msg.timestamp, nickname=msg.author.username))
        logger.info(log)
        asyncio.create_task(dispatch(message))