"""
Class File for the QQ WebHook Logic

Author: Shanshui2024
Organization: AxT-Team

本包提供 QQ 平台的基础模型（独立，不依赖 framework）：
  - 验证 / Token / Payload 等 QQ 独有模型
  - QQ 扩展字段模型（用于在集成层与 framework 合并）
  - QQ 附件模型
"""
from app.classes.qq_adapter.Validation import Validation as QQValidationEvent
from app.classes.qq_adapter.BasePayload import BasePayload
from app.classes.qq_adapter.Message import QQAuthorExt, QQMessageExt
from app.classes.qq_adapter.AccessToken import AccessToken
from app.classes.qq_adapter.Attachment import (
    Attachment as QQAttachment,
    VoiceAttachment as QQVoiceAttachment,
    ImageAttachment as QQImageAttachment,
    VideoAttachment as QQVideoAttachment,
    FileAttachment as QQFileAttachment,
    AttachmentList as QQAttachmentList,
)

__all__ = [
    "QQValidationEvent",
    "BasePayload",
    "QQAuthorExt",
    "QQMessageExt",
    "AccessToken",
    "QQAttachment",
    "QQVoiceAttachment",
    "QQImageAttachment",
    "QQVideoAttachment",
    "QQFileAttachment",
    "QQAttachmentList",
]