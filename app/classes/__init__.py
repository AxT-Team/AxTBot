"""
Class File for the WebHook Logic

Author: Shanshui2024
Organization: AxT-Team

本模块是集成层，负责：
  1. 从 framework 引入通用地基模型
  2. 从 qq_adapter 引入 QQ 平台扩展字段
  3. 通过多重继承合并，生成最终可用的完整模型

依赖方向（单向无循环）：
  framework ◄── 集成层 ──► qq_adapter
  (framework 和 qq_adapter 互不依赖)
"""
from typing import Any

# ── 地基：framework 通用模型 ──
from app.classes.framework.Message import (
    Author as _FWAuthor,
    Mentions as _FWMentions,
    MessageScene as _FWMessageScene,
    Message as _FWMessage,
    GroupMessage as _FWGroupMessage,
    PrivateMessage as _FWPrivateMessage,
)

# ── 扩展：qq_adapter 特有字段 ──
from app.classes.qq_adapter.Message import QQAuthorExt, QQMessageExt
from app.classes.qq_adapter import (
    QQValidationEvent,
    BasePayload,
    AccessToken,
    QQInteraction
)

# ── 附件：QQ 适配器版本（含 content_type / size 等 QQ 特有字段）──
from app.classes.qq_adapter.Attachment import (
    Attachment,
    VoiceAttachment,
    ImageAttachment,
    VideoAttachment,
    FileAttachment,
    AttachmentList,
)

from app.classes.framework.Session import Session, SessionManager
from app.classes.framework import PluginMetadata


# ============================================================
#  合并模型：framework 地基 + qq_adapter 扩展 = 最终模型
# ============================================================

class Author(_FWAuthor, QQAuthorExt):
    """
    合并后的 Author = framework 通用字段 + QQ 扩展字段。

    framework 提供：id, username, bot, openid, role
    qq_adapter 补充：member_openid, union_openid, member_role
    """
    pass


class Mentions(_FWMentions):
    """Mentions 无 QQ 特有扩展，直接使用 framework 定义"""
    pass


class MessageScene(_FWMessageScene):
    """MessageScene 无 QQ 特有扩展，直接使用 framework 定义"""
    pass


class Message(_FWMessage, QQMessageExt):
    """
    合并后的 Message = framework 通用字段 + QQ 扩展字段。

    framework 提供：id, content, timestamp, author, mentions, message_scene, attachments
    qq_adapter 补充：message_type

    注意：author / mentions / message_scene / attachments 的类型注解
    需要覆盖为合并后的模型类型。
    """
    author: Author
    mentions: list[Mentions] | None = None
    message_scene: MessageScene | dict[str, Any]
    attachments: list[Attachment] | None = None
    is_you: bool | None = None


class GroupMessage(Message):
    """
    合并后的群聊消息。
    从 framework.GroupMessage 继承 group_id / group_openid。
    """
    group_id: str
    group_openid: str


class PrivateMessage(Message):
    """
    合并后的私聊消息。
    """
    pass


# ============================================================
#  对外导出
# ============================================================
__all__ = [
    # 合并后的消息模型（对外统一使用这些）
    "Author",
    "Mentions",
    "MessageScene",
    "Message",
    "GroupMessage",
    "PrivateMessage",
    # QQ 平台独有模型
    "QQValidationEvent",
    "BasePayload",
    "AccessToken",
    "QQInteraction"
    # 附件模型
    "Attachment",
    "VoiceAttachment",
    "ImageAttachment",
    "VideoAttachment",
    "FileAttachment",
    "AttachmentList",
    "Session",
    "SessionManager",
    "PluginMetadata"
]