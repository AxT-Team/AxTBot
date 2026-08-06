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
    QQInteraction,
    Sender,
    Markdown,
    Keyboard,
    KeyboardContent,
    Row,
    Button,
    RenderData,
    Action,
    Permission,
    MediaInfo,
    MessageReference,
    Card,
    CardContent,
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

    # ── 内部工具 ──

    @staticmethod
    def _build_content(
        content: str | None,
        mention: bool,
        author_id: str,
        mention_users: list[str] | None,
    ) -> str | None:
        """在 content 前拼接 @ 提及文本链（新格式）。"""
        parts = []
        if mention:
            parts.append(f'<qqbot-at-user id="{author_id}" />')
        if mention_users:
            for uid in mention_users:
                parts.append(f'<qqbot-at-user id="{uid}" />')
        if not parts:
            return content
        return " ".join(parts) + " " + (content or "")

    def _get_msg_idx(self) -> str | None:
        """
        从 message_scene.ext 中提取 msg_idx，用于正确的引用回复。

        QQ API 的引用链通过 msg_idx 传递，而非消息 id。
        """
        ext = None
        if isinstance(self.message_scene, MessageScene):
            ext = self.message_scene.ext
        elif isinstance(self.message_scene, dict):
            ext = self.message_scene.get("ext", [])
        if ext:
            for item in ext:
                if isinstance(item, str) and item.startswith("msg_idx="):
                    return item[len("msg_idx="):]
        return None

    @staticmethod
    def _auto_msg_type(kwargs: dict) -> None:
        """传了 markdown 未传 msg_type → 自动设为 2；否则默认 0。"""
        if "markdown" in kwargs and "msg_type" not in kwargs:
            kwargs["msg_type"] = 2

    # ── 公开 API ──

    async def reply(
        self,
        content: str | None = None,
        *,
        quote: bool = True,
        mention: bool = False,
        mention_users: list[str] | None = None,
        **kwargs,
    ) -> dict | None:
        """
        被动回复本消息（自动填 msg_id）。

        Args:
            content       : 回复文本（可为 None，纯发 markdown / 键盘时）
            quote         : 是否引用原消息显示引用样式，默认 True
            mention       : 是否在消息开头 @ 消息作者
            mention_users : 额外 @ 的用户 ID 列表
            **kwargs      : 透传给 Sender（markdown, keyboard, msg_type 等）

        Returns:
            API 响应 dict 或 None
        """
        from app.service.qq_service.MsgSender import send_group_message, send_c2c_message

        content = self._build_content(content, mention, self.author.id, mention_users)
        self._auto_msg_type(kwargs)
        sender = Sender(
            content=content,
            msg_id=self.id,
            msg_seq=kwargs.pop("msg_seq", 1),
            **kwargs,
        )
        if quote:
            ref_idx = self._get_msg_idx()
            if ref_idx:
                sender.message_reference = MessageReference(message_id=ref_idx)

        if isinstance(self, GroupMessage):
            return await send_group_message(self.group_openid, sender)
        else:
            return await send_c2c_message(self.author.union_openid, sender)

    async def send(
        self,
        content: str | None = None,
        *,
        mention: bool = False,
        mention_users: list[str] | None = None,
        **kwargs,
    ) -> dict | None:
        """
        主动发送消息（不填 msg_id，不受 5 分钟限制）。

        Args:
            content       : 消息文本
            mention       : 是否 @ 消息作者
            mention_users : 额外 @ 的用户 ID 列表
            **kwargs      : 透传给 Sender 构造器

        Returns:
            API 响应 dict 或 None
        """
        from app.service.qq_service.MsgSender import send_group_message, send_c2c_message

        content = self._build_content(content, mention, self.author.id, mention_users)
        self._auto_msg_type(kwargs)
        sender = Sender(content=content, **kwargs)

        if isinstance(self, GroupMessage):
            return await send_group_message(self.group_openid, sender)
        else:
            return await send_c2c_message(self.author.union_openid, sender)


class GroupMessage(Message):
    """
    合并后的群聊消息。
    从 framework.GroupMessage 继承 group_id / group_openid。
    """
    group_id: str
    group_openid: str

    async def reply(
        self,
        content: str | None = None,
        *,
        quote: bool = True,
        mention: bool = False,
        mention_users: list[str] | None = None,
        **kwargs,
    ) -> dict | None:
        """
        被动回复本群消息（自动填 msg_id / group_openid）。

        Args:
            content       : 回复文本
            quote         : 是否引用原消息，默认 True
            mention       : 是否 @ 消息作者（群聊中适用）
            mention_users : 额外 @ 的用户 ID 列表
            **kwargs      : 透传给 Sender（markdown, keyboard, msg_type 等）

        Example:
            await msg.reply("收到！")                            # 引用回复
            await msg.reply("你好", quote=False)                 # 不引用
            await msg.reply("请查看", mention=True)              # 引用 + @作者
            await msg.reply(markdown=Markdown(...), keyboard=kb) # 复杂消息
        """
        from app.service.qq_service.MsgSender import send_group_message

        content = self._build_content(content, mention, self.author.id, mention_users)
        self._auto_msg_type(kwargs)
        sender = Sender(
            content=content,
            msg_id=self.id,
            msg_seq=kwargs.pop("msg_seq", 1),
            **kwargs,
        )
        if quote:
            ref_idx = self._get_msg_idx()
            if ref_idx:
                sender.message_reference = MessageReference(message_id=ref_idx)

        return await send_group_message(self.group_openid, sender)

    async def send(
        self,
        content: str | None = None,
        *,
        mention: bool = False,
        mention_users: list[str] | None = None,
        **kwargs,
    ) -> dict | None:
        """
        主动向本群发送消息（不填 msg_id，不受 5 分钟限制）。

        Args:
            content       : 消息文本
            mention       : 是否 @ 消息作者
            mention_users : 额外 @ 的用户 ID 列表
            **kwargs      : 透传给 Sender 构造器

        Example:
            await msg.send("推送通知")
            await msg.send("开会了", mention=True)
        """
        from app.service.qq_service.MsgSender import send_group_message

        content = self._build_content(content, mention, self.author.id, mention_users)
        self._auto_msg_type(kwargs)
        sender = Sender(content=content, **kwargs)

        return await send_group_message(self.group_openid, sender)


class PrivateMessage(Message):
    """
    合并后的私聊消息。
    """

    async def reply(
        self,
        content: str | None = None,
        *,
        quote: bool = True,
        **kwargs,
    ) -> dict | None:
        """
        被动回复本私聊消息（自动填 msg_id / user_openid）。

        私聊中 mention 无意义（仅双方对话），忽略该参数。

        Args:
            content  : 回复文本
            quote    : 是否引用原消息，默认 True
            **kwargs : 透传给 Sender 构造器
        """
        from app.service.qq_service.MsgSender import send_c2c_message

        self._auto_msg_type(kwargs)
        sender = Sender(
            content=content,
            msg_id=self.id,
            msg_seq=kwargs.pop("msg_seq", 1),
            **kwargs,
        )
        if quote:
            ref_idx = self._get_msg_idx()
            if ref_idx:
                sender.message_reference = MessageReference(message_id=ref_idx)

        return await send_c2c_message(self.author.union_openid, sender)

    async def send(
        self,
        content: str | None = None,
        **kwargs,
    ) -> dict | None:
        """
        主动向本用户发送私聊消息。

        Args:
            content  : 消息文本
            **kwargs : 透传给 Sender 构造器
        """
        from app.service.qq_service.MsgSender import send_c2c_message

        self._auto_msg_type(kwargs)
        sender = Sender(content=content, **kwargs)
        return await send_c2c_message(self.author.union_openid, sender)


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
    "QQInteraction",
    # 发送消息相关模型
    "Sender",
    "Markdown",
    "Keyboard",
    "KeyboardContent",
    "Row",
    "Button",
    "RenderData",
    "Action",
    "Permission",
    "MediaInfo",
    "MessageReference",
    "Card",
    "CardContent",
    # 附件模型
    "Attachment",
    "VoiceAttachment",
    "ImageAttachment",
    "VideoAttachment",
    "FileAttachment",
    "AttachmentList",
    # Framework 模型
    "Session",
    "SessionManager",
    "PluginMetadata",
]