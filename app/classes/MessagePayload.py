"""
Class File for Webhook Message Payload

Author: Shanshui2024
Organization: AxT-Team
"""
from app.classes import BasePayload

class Message(BasePayload):
    """
    消息事件的模型，包含消息相关字段
    """
    message_id: str
    content: str
    type: int
    channel_id: str
    guild_id: str | None = None