"""
Class File for Webhook Message Payload

Author: Shanshui2024
Organization: AxT-Team
"""
from pydantic import BaseModel, field_validator
from typing import Any

from app.classes.Attachment import Attachment, VoiceAttachment, ImageAttachment, VideoAttachment, FileAttachment, AttachmentList

class Author(BaseModel):
    """
    消息作者的模型，包含uid、用户名、是否为机器人以及union_openid等信息
    """
    id: str
    username: str
    bot: bool = False
    union_openid: str

class MessageScene(BaseModel):
    """
    消息场景模型
    """
    source: str
    ext: list[str] = []


class Message(BaseModel):
    """
    通用消息模型
    """
    id: str
    content: str
    timestamp: str
    author: Author
    message_scene: MessageScene | dict[str, Any]
    message_type: int
    attachments: list[Attachment] | None = None

    @field_validator("content", mode="before")
    @classmethod
    def __strip_content_leading_spaces(cls, value: Any) -> str:
        return str(value).lstrip()


class GroupMessage(Message):
    """
    群聊消息模型
    """
    group_id: str
    group_openid: str


class PrivateMessage(Message):
    """
    私聊消息模型
    """
    pass