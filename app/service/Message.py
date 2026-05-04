"""
Message Processing Service for QQ Bot

Author: Shanshui2024
Organization: AxT-Team
"""
from app.classes import GroupMessage, BasePayload, PrivateMessage
from app.modules import logger, db, User, Group


async def message_process(payload: BasePayload) -> None:
    """
    Message Processing Service for QQ Bot

    Args:
        payload (BasePayload): BasePayload Object

    Returns:
        None
    """
    message = payload.d
    logger.debug(f"Received message payload: {message}")
    if payload.t == "GROUP_AT_MESSAGE_CREATE":
        msg = GroupMessage(**message)
        log = f"传入消息 >>> [群聊消息 | 群ID：{msg.group_openid}] | "
        if msg.author.bot:
            log += f"[BOT]{msg.author.username} > {msg.content}"
        else:
            log += f"{msg.author.username} > {msg.content}"
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
        if not Group.get_group_by_id(msg.group_id):
            Group.add_group(Group(group_id=msg.group_id, group_openid=msg.group_openid, message = 0, create_time=msg.timestamp, update_time=msg.timestamp))
        if not User.get_user_by_openid(msg.author.union_openid):
            User.add_user(User(user_openid=msg.author.union_openid, message = 0, create_time=msg.timestamp, update_time=msg.timestamp))
        # 如果有用户消息或群聊消息查询记录，则添加计数 但这里暂时没写完 先空着
        logger.info(log)
    elif payload.t == "C2C_MESSAGE_CREATE":
        msg = PrivateMessage(**message)
        log = f"传入消息 >>> [私聊消息] | "
        if msg.author.bot:
            log += f"[BOT]{msg.author.username} > {msg.content}"
        else:
            log += f"{msg.author.username} > {msg.content}"
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
        if not User.get_user_by_openid(msg.author.union_openid):
            User.add_user(User(user_openid=msg.author.union_openid, message = 0, create_time=msg.timestamp, update_time=msg.timestamp))
        logger.info(log)

    