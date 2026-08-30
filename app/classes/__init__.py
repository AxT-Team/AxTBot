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

    @staticmethod
    def _merge_image_markdown(
        content: str | None,
        markdown: "Markdown | None",
        image_url: str,
        file_name: str | None,
    ) -> str:
        """把可访问图片链接与已有文本/Markdown 合并成一段 Markdown 文本。"""
        base = markdown.content if markdown is not None else (content or "")
        img_md = f"![{file_name or 'image'}]({image_url})"
        return (base + "\n\n" + img_md) if base else img_md

    async def upload_image(
        self,
        source: "str | Path",
        *,
        file_type: int | None = None,
        file_name: str | None = None,
    ) -> "str | None":
        """
        仅上传图片并返回可访问链接，**不自动发送**，由插件自行决定如何发送。

        流程：上传到 QQ 远端（读取内容分片上传）→ 写入缓存表（带 TTL）→ 返回 raw_url。
        返回的链接可直接嵌入 Markdown：``![alt](url)``。

        Args:
            source   : 本地文件路径（str/Path）或网络图片 URL
            file_type: 1=图片 2=视频 3=语音 4=文件，缺省按扩展名推断
            file_name: 可选文件名

        Returns:
            可访问的图片链接字符串（图片类）；文件类（file_type=4）返回 file_info；
            失败返回 None

        Example:
            url = await event.upload_image("./a.png")
            if url:
                await event.reply(markdown=Markdown(content=f"![图]({url})"))

            # 以文件格式上传（不转码，原样发送）
            file_info = await event.upload_image("./a.gif", file_type=4)
        """
        from app.service.qq_service.FileUpload import upload_image_link, upload_media

        scene = "group" if isinstance(self, GroupMessage) else "user"
        openid = self.group_openid if isinstance(self, GroupMessage) else self.author.union_openid
        if file_type == 4:
            return await upload_media(openid, scene, source, file_type=4, file_name=file_name)
        return await upload_image_link(openid, scene, source, file_type=file_type, file_name=file_name)

    async def _apply_media(
        self,
        image: "str | Path | None",
        file_type: int | None,
        file_name: str | None,
    ) -> "tuple[str, str] | None":
        """
        若传入了 image，则上传到 QQ 远端，并返回 (mode, payload)：

        QQ 的 Markdown 消息无法渲染外链/动图，因此无论哪种模式，图片/视频/语音
        都返回 ("media", file_info)，由调用方以 msg_type=7 富媒体消息发送（动图会保留）。
        file_type=4（文件）同样返回 ("media", file_info)，以文件消息发送。

        另外，分片上传拿到的 raw_url 会被写入缓存表（带 TTL），插件仍可通过
        event.upload_image(...) 取得该链接用于其它用途。

        失败返回 None。
        """
        if image is None:
            return None
        from app.classes import MediaInfo
        from app.modules import config_loader, logger
        from app.service.qq_service.FileUpload import upload_image_link, upload_media

        scene = "group" if isinstance(self, GroupMessage) else "user"
        openid = self.group_openid if isinstance(self, GroupMessage) else self.author.union_openid
        try:
            local_mode = config_loader.get_core_config().media_local_upload
        except Exception:
            local_mode = True

        if local_mode:
            # file_type=4（文件）：原样以文件上传，不做图片转换，也不走 Markdown 链接
            if file_type == 4:
                file_info = await upload_media(openid, scene, image, file_type=4, file_name=file_name)
                if not file_info:
                    logger.error("消息 >>> 文件上传失败，无法发送")
                    return None
                return ("media", file_info)
            # 图片/视频/语音：QQ 的 Markdown 无法渲染外链/动图，必须以富媒体消息
            # (msg_type=7 + file_info) 发送才能正常展示（动图也会保留）。
            # 注意：upload_media 内部已把 raw_url 写入缓存表，仍可用 event.upload_image 取链接。
            file_info = await upload_media(openid, scene, image, file_type=file_type, file_name=file_name)
            if not file_info:
                logger.error("消息 >>> 图片上传失败，无法发送富媒体")
                return None
            return ("media", file_info)
        else:
            file_info = await upload_media(openid, scene, image, file_type=file_type, file_name=file_name)
            if not file_info:
                logger.error("消息 >>> 图片 URL 上传失败，无法发送富媒体")
                return None
            return ("media", file_info)

    # ── 公开 API ──

    async def reply(
        self,
        content: str | None = None,
        *,
        quote: bool = True,
        mention: bool = False,
        mention_users: list[str] | None = None,
        image: "str | Path | None" = None,
        file_type: int | None = None,
        file_name: str | None = None,
        ref_idx: str | None = None,
        **kwargs,
    ) -> dict | None:
        """
        被动回复本消息（自动填 msg_id）。

        Args:
            content       : 回复文本（可为 None，纯发 markdown / 键盘时）
            quote         : 是否引用原消息显示引用样式，默认 True
            mention       : 是否在消息开头 @ 消息作者
            mention_users : 额外 @ 的用户 ID 列表
            image         : 富媒体来源（URL 链接或本地文件路径），自动上传并发送
            file_type     : 1=图片 2=视频 3=语音 4=文件，缺省按扩展名推断
            file_name     : 可选文件名
            **kwargs      : 透传给 Sender（markdown, keyboard, msg_type 等）

        Returns:
            API 响应 dict 或 None
        """
        from app.service.qq_service.MsgSender import send_group_message, send_c2c_message
        content = self._build_content(content, mention, self.author.id, mention_users)
        self._auto_msg_type(kwargs)
        media_result = await self._apply_media(image, file_type, file_name)
        if media_result is not None:
            mode, payload = media_result
            if mode == "markdown":
                md = kwargs.pop("markdown", None)
                kwargs["markdown"] = Markdown(content=self._merge_image_markdown(content, md, payload, file_name))
                kwargs["msg_type"] = 2
                content = None
            else:
                kwargs["media"] = MediaInfo(file_info=payload)
                kwargs["msg_type"] = 7
        sender = Sender(
            content=content,
            msg_id=self.id,
            msg_seq=kwargs.pop("msg_seq", 1),
            message_reference=MessageReference(message_id=ref_idx)
            **kwargs,
        )
        if quote:
            if not ref_idx:
                ref_idx = self._get_msg_idx()
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
        image: "str | Path | None" = None,
        file_type: int | None = None,
        file_name: str | None = None,
        **kwargs,
    ) -> dict | None:
        """
        主动发送消息（不填 msg_id，不受 5 分钟限制）。

        Args:
            content       : 消息文本
            mention       : 是否 @ 消息作者
            mention_users : 额外 @ 的用户 ID 列表
            image         : 富媒体来源（URL 链接或本地文件路径），自动上传并发送
            file_type     : 1=图片 2=视频 3=语音 4=文件，缺省按扩展名推断
            file_name     : 可选文件名
            **kwargs      : 透传给 Sender 构造器

        Returns:
            API 响应 dict 或 None
        """
        from app.service.qq_service.MsgSender import send_group_message, send_c2c_message

        content = self._build_content(content, mention, self.author.id, mention_users)
        self._auto_msg_type(kwargs)
        media_result = await self._apply_media(image, file_type, file_name)
        if media_result is not None:
            mode, payload = media_result
            if mode == "markdown":
                md = kwargs.pop("markdown", None)
                kwargs["markdown"] = Markdown(content=self._merge_image_markdown(content, md, payload, file_name))
                kwargs["msg_type"] = 2
                content = None
            else:
                kwargs["media"] = MediaInfo(file_info=payload)
                kwargs["msg_type"] = 7
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
        image: "str | Path | None" = None,
        file_type: int | None = None,
        file_name: str | None = None,
        ref_idx: str | None = None,
        **kwargs,
    ) -> dict | None:
        """
        被动回复本群消息（自动填 msg_id / group_openid）。

        Args:
            content       : 回复文本
            quote         : 是否引用原消息，默认 True
            mention       : 是否 @ 消息作者（群聊中适用）
            mention_users : 额外 @ 的用户 ID 列表
            image         : 富媒体来源（URL 链接或本地文件路径），自动上传并发送
            file_type     : 1=图片 2=视频 3=语音 4=文件，缺省按扩展名推断
            file_name     : 可选文件名
            **kwargs      : 透传给 Sender（markdown, keyboard, msg_type 等）

        Example:
            await msg.reply("收到！")                            # 引用回复
            await msg.reply("你好", quote=False)                 # 不引用
            await msg.reply("请查看", mention=True)              # 引用 + @作者
            await msg.reply(markdown=Markdown(...), keyboard=kb) # 复杂消息
            await msg.reply(image="https://x/y.png")            # 发送网络图片
            await msg.reply(image="./local.jpg")               # 发送本地图片
        """
        from app.service.qq_service.MsgSender import send_group_message

        content = self._build_content(content, mention, self.author.id, mention_users)
        self._auto_msg_type(kwargs)
        media_result = await self._apply_media(image, file_type, file_name)
        if media_result is not None:
            mode, payload = media_result
            if mode == "markdown":
                md = kwargs.pop("markdown", None)
                kwargs["markdown"] = Markdown(content=self._merge_image_markdown(content, md, payload, file_name))
                kwargs["msg_type"] = 2
                content = None
            else:
                kwargs["media"] = MediaInfo(file_info=payload)
                kwargs["msg_type"] = 7
        sender = Sender(
            content=content,
            msg_id=self.id,
            msg_seq=kwargs.pop("msg_seq", 1),
            **kwargs,
        )
        if quote:
            if not ref_idx:
                ref_idx = self._get_msg_idx()
            sender.message_reference = MessageReference(message_id=ref_idx)

        return await send_group_message(self.group_openid, sender)

    async def send(
        self,
        content: str | None = None,
        *,
        mention: bool = False,
        mention_users: list[str] | None = None,
        image: "str | Path | None" = None,
        file_type: int | None = None,
        file_name: str | None = None,
        **kwargs,
    ) -> dict | None:
        """
        主动向本群发送消息（不填 msg_id，不受 5 分钟限制）。

        Args:
            content       : 消息文本
            mention       : 是否 @ 消息作者
            mention_users : 额外 @ 的用户 ID 列表
            image         : 富媒体来源（URL 链接或本地文件路径），自动上传并发送
            file_type     : 1=图片 2=视频 3=语音 4=文件，缺省按扩展名推断
            file_name     : 可选文件名
            **kwargs      : 透传给 Sender 构造器

        Example:
            await msg.send("推送通知")
            await msg.send("开会了", mention=True)
            await msg.send(image="./poster.png")
        """
        from app.service.qq_service.MsgSender import send_group_message

        content = self._build_content(content, mention, self.author.id, mention_users)
        self._auto_msg_type(kwargs)
        media_result = await self._apply_media(image, file_type, file_name)
        if media_result is not None:
            mode, payload = media_result
            if mode == "markdown":
                md = kwargs.pop("markdown", None)
                kwargs["markdown"] = Markdown(content=self._merge_image_markdown(content, md, payload, file_name))
                kwargs["msg_type"] = 2
                content = None
            else:
                kwargs["media"] = MediaInfo(file_info=payload)
                kwargs["msg_type"] = 7
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
        image: "str | Path | None" = None,
        file_type: int | None = None,
        file_name: str | None = None,
        ref_idx: str | None = None,
        **kwargs,
    ) -> dict | None:
        """
        被动回复本私聊消息（自动填 msg_id / user_openid）。

        私聊中 mention 无意义（仅双方对话），忽略该参数。

        Args:
            content  : 回复文本
            quote    : 是否引用原消息，默认 True
            image    : 富媒体来源（URL 链接或本地文件路径），自动上传并发送
            file_type: 1=图片 2=视频 3=语音 4=文件，缺省按扩展名推断
            file_name: 可选文件名
            **kwargs : 透传给 Sender 构造器
        """
        from app.service.qq_service.MsgSender import send_c2c_message

        self._auto_msg_type(kwargs)
        media_result = await self._apply_media(image, file_type, file_name)
        if media_result is not None:
            mode, payload = media_result
            if mode == "markdown":
                md = kwargs.pop("markdown", None)
                kwargs["markdown"] = Markdown(content=self._merge_image_markdown(content, md, payload, file_name))
                kwargs["msg_type"] = 2
                content = None
            else:
                kwargs["media"] = MediaInfo(file_info=payload)
                kwargs["msg_type"] = 7
        sender = Sender(
            content=content,
            msg_id=self.id,
            msg_seq=kwargs.pop("msg_seq", 1),
            **kwargs,
        )
        if quote:
            if not ref_idx:
                ref_idx = self._get_msg_idx()
            sender.message_reference = MessageReference(message_id=ref_idx)

        return await send_c2c_message(self.author.union_openid, sender)

    async def send(
        self,
        content: str | None = None,
        *,
        image: "str | Path | None" = None,
        file_type: int | None = None,
        file_name: str | None = None,
        **kwargs,
    ) -> dict | None:
        """
        主动向本用户发送私聊消息。

        Args:
            content  : 消息文本
            image    : 富媒体来源（URL 链接或本地文件路径），自动上传并发送
            file_type: 1=图片 2=视频 3=语音 4=文件，缺省按扩展名推断
            file_name: 可选文件名
            **kwargs : 透传给 Sender 构造器
        """
        from app.service.qq_service.MsgSender import send_c2c_message

        self._auto_msg_type(kwargs)
        media_result = await self._apply_media(image, file_type, file_name)
        if media_result is not None:
            mode, payload = media_result
            if mode == "markdown":
                md = kwargs.pop("markdown", None)
                kwargs["markdown"] = Markdown(content=self._merge_image_markdown(content, md, payload, file_name))
                kwargs["msg_type"] = 2
                content = None
            else:
                kwargs["media"] = MediaInfo(file_info=payload)
                kwargs["msg_type"] = 7
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