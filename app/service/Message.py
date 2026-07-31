"""
Message Processing Service for QQ Bot

Author: Shanshui2024
Organization: AxT-Team
"""
import asyncio

from app.classes import GroupMessage, BasePayload, PrivateMessage, QQInteraction
from app.modules import logger, database, User, Group, dispatch, get_db, config

async def message_process(payload: BasePayload) -> None:
    """
    Message Processing Service for QQ Bot

    Args:
        payload (BasePayload): BasePayload Object

    Returns:
        None
    """
    message = payload.d
    logger.debug(f"Received payload: {payload}")
    db = get_db()
    if payload.t == "GROUP_AT_MESSAGE_CREATE":
        msg = GroupMessage(**message)
        content = msg.content
        # if msg.mentions:  # <-- 这里开放平台还没有办法读取到任何艾特形式消息，只有全量消息可以收到。。。
        #     for mention in msg.mentions:
        #         content = content.replace("<@" + str(mention.id) + ">" , "[@" + mention.username + "]")
        if len(content) <= 200:
            pass
        else:
            half = 100 // 2
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
        is_you = None
        if msg.mentions:
            for mention in msg.mentions:
                content = content.replace("<@" + str(mention.id) + ">" , "[@" + mention.username + "]")
                if mention.is_you:
                    is_you = True
                    bot_username = db.get_frame_config_by_key("bot_username").key
                    content = content.replace(f"[@{bot_username}]", "")
        if len(content) <= 200:
            pass
        else:
            half = 100 // 2
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
        if len(text) <= 200:
            pass
        else:
            half = 100 // 2
            text = text[:half] + "..." + text[-half:]
        log = f"传入消息 >>> [私聊消息] | "
        if msg.author.bot:
            log += f"[BOT][用户ID：{msg.author.union_openid}] > {text}"
        else:
            log += f"[用户ID：{msg.author.union_openid}] > {text}"
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
    elif payload.t == "INTERACTION_CREATE":
        interaction = QQInteraction(**message)
        if config.appid == interaction.application_id:
            if interaction.type == 11:
                log = f"互动 >>> [按钮"
            elif interaction.type == 12:
                log = f"互动 >>> [菜单"
            else:
                logger.warning("互动 >>> 接收到未归类的互动，请查看控制台")
                return
            if interaction.chat_type == 1:
                log += f" | 群：{interaction.group_openid} | 用户：{interaction.group_member_openid}] >"
            elif interaction.chat_type == 0:
                log += f" | 频：{interaction.guild_id} | 子频：{interaction.channel_id}] >"
            elif interaction.chat_type == 2:
                log += f" | 用户ID：{interaction.user_openid}] >"
            else:
                log += "] >"
            log += f" ID:{interaction.data.resolved.button_id} 数据:{interaction.data.resolved.button_data}"
            logger.info(log)