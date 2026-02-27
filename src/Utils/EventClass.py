import json, binascii
from nacl.signing import SigningKey
from nacl.exceptions import BadSignatureError
from fastapi import Request
from typing import Any, Dict, List, Union, Type, TypeVar, Optional
from pydantic import BaseModel

from src.Utils.Logger import logger
from src.Utils.Config import config

# 类型变量用于类方法
T = TypeVar("T", bound="QQBasePayload")

class QQBasePayload:
    """
    QQ开放平台通用Payload基类
    处理Webhook和WebSocket两种方式的数据
    """
    def __init__(self, payload: Union[Dict[str, Any], str]):
        """
        初始化Payload
        :param payload: 可以是字典或JSON字符串
        """
        # 处理输入数据
        if isinstance(payload, str):
            self._raw_data = json.loads(payload)
        else:
            self._raw_data = payload
        # 解析基础字段
        self.id: str = self._raw_data.get("id", "")
        """id字段通常是事件的唯一标识符"""
        self.op: int = self._raw_data.get("op", -1)
        """op字段 即OpCode，指示事件大类型"""
        self.s: int = self._raw_data.get("s", 0)
        """s字段 下行消息序列ID，用于标识消息"""
        self.t: str = self._raw_data.get("t", "")
        """t字段 事件类型名称（仅当op=0时有效）"""

        # 递归处理d字段
        self.d: dict = self._recursive_parse(self._raw_data.get("d", {}))
        """d字段 事件数据，嵌套的字典或列表"""

    def _recursive_parse(self, data: Any) -> Any:
        """递归解析嵌套数据结构"""
        if isinstance(data, dict):
            return AttrDict(data)
        elif isinstance(data, list):
            return [self._recursive_parse(item) for item in data]
        return data

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """从JSON字符串创建实例"""
        return cls(json.loads(json_str))

    @property
    def opcode_name(self) -> str:
        """获取OpCode的名称"""
        # OpCode名称映射表
        OPCODE_NAMES = {
            0: "Dispatch", # 服务端的消息推送
            12: "HTTP Callback ACK", # 仅用于HTTP回调模式数据包 代表机器人收到消息
            13: "Validation", # 开放平台进行服务端验证
        }
        return OPCODE_NAMES.get(self.op, f"Unknown({self.op})")

    @property
    def event_type(self) -> str:
        """获取事件类型名称（仅当op=0时有效）"""
        return self.t if self.op == 0 else ""

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典"""
        return {
            "id": self.id,
            "op": self.op,
            "s": self.s,
            "t": self.t,
            "d": self.d.to_dict() if isinstance(self.d, AttrDict) else self.d,
        }

    def to_json(self, indent: int = 2) -> str:
        """将对象转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def is_dispatch(self) -> bool:
        """是否是事件分发类型 (op=0)"""
        return self.op == 0

    def is_validation(self) -> bool:
        """是否是验证类型 (op=13)"""
        return self.op == 13

    def is_message_create(self) -> bool:
        """是否是消息创建事件"""
        return self.is_dispatch() and self.t in [
            "MESSAGE_CREATE",
            "AT_MESSAGE_CREATE",
            "DIRECT_MESSAGE_CREATE",
            "C2C_MESSAGE_CREATE",
            "GROUP_AT_MESSAGE_CREATE",
        ]

    @staticmethod
    async def generate_validation_response(
        request: Request
    ) -> Dict[str, str]:
        """验证开放平台提供的签名密钥，并对官方平台进行回应
        
        Args:
            request (Request): FastAPI请求对象，包含请求头和body

        Returns:
            dict: 返回一个字典，包含plain_token和signature

        Raises:
            BadSignatureError: 如果签名验证失败，抛出异常
            binascii.Error: 如果X-Signature-Ed25519长度不是64字节，抛出异常
        """
        _X_Signature_Ed25519 = request.headers.get("X-Signature-Ed25519").encode(
            "utf-8"
        )  # 读请求头中的Ed25519签名信息
        _X_Signature_Timestamp = request.headers.get("X-Signature-Timestamp").encode(
            "utf-8"
        )  # 读请求头中的时间戳 按理说等价于body["d"]["event_ts"]
        _body = await request.body()  # 先拿到手一个body用于检查证书是否正确
        _plain_token = json.loads(_body.decode("utf-8")).get("d").get("plain_token").encode(
            "utf-8"
        )
        QQ_BOT_SECRET = config.Bot.appsecret.encode(
            "utf-8"
        )
        while len(QQ_BOT_SECRET) < 32:
            QQ_BOT_SECRET += QQ_BOT_SECRET  # 按理说这里不用到32 但是开放平台这么要求的 防止出问题先这么写（
        QQ_BOT_SECRET = QQ_BOT_SECRET[:32]  # 合成、分割前32位 用于加解密
        _X_Signature_Ed25519 = binascii.unhexlify(
            _X_Signature_Ed25519
        )  # 给一下hex解码 对应官方文档的
        if len(_X_Signature_Ed25519) != 64:  # 官方文档提出解码后应该为64 bytes
            raise binascii.Error(
                "X-Signature-Ed25519 must be 64 bytes long, but received %d bytes."
                % len(_X_Signature_Ed25519)
            )
        _sign_key = SigningKey(QQ_BOT_SECRET)  # 先搞一个签名器
        try:
            _sign_key.verify_key.verify(
                _X_Signature_Timestamp + _body, _X_Signature_Ed25519
            )  # 前边是构建出来的时间戳+body消息串 后面是签名
        except BadSignatureError as e:
            raise BadSignatureError(
                "Signature verification failed! Please check your variable QQ_BOT_SECRET."
            )
        _message = _X_Signature_Timestamp + _plain_token  # 还需要再次用一下json的内容构建返回消息并加密
        _signature = _sign_key.sign(_message).signature.hex()
        return {"plain_token": _plain_token, "signature": _signature}

class AttrDict:
    """属性字典，允许通过点号访问嵌套属性"""

    def __init__(self, data: Dict[str, Any]):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, AttrDict(value))
            elif isinstance(value, list):
                # 处理列表中的嵌套字典
                processed_list = []
                for item in value:
                    if isinstance(item, dict):
                        processed_list.append(AttrDict(item))
                    else:
                        processed_list.append(item)
                setattr(self, key, processed_list)
            else:
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """转换为普通字典"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, AttrDict):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                # 处理列表中的AttrDict
                processed_list = []
                for item in value:
                    if isinstance(item, AttrDict):
                        processed_list.append(item.to_dict())
                    else:
                        processed_list.append(item)
                result[key] = processed_list
            else:
                result[key] = value
        return result

    def __repr__(self) -> str:
        """友好的对象表示形式"""
        return f"<AttrDict({self.to_dict()})>"

    def __getitem__(self, key):
        """支持字典式访问"""
        return getattr(self, key)

    def get(self, key, default=None):
        """安全的属性获取"""
        return getattr(self, key, default)

class MessageEventPayload(QQBasePayload):
    """消息体事件"""

    @property
    def event_type(self) -> str:
        """(转中文)事件类型"""
        if self.t == "MESSAGE_CREATE":
            return "私域频道"
        elif self.t == "AT_MESSAGE_CREATE":
            return "频道艾特"
        elif self.t == "DIRECT_MESSAGE_CREATE":
            return "频道私信"
        elif self.t == "GROUP_AT_MESSAGE_CREATE":
            return "群消息"
        elif self.t == "C2C_MESSAGE_CREATE":
            return "私信"
        else:
            return self.t

    @property
    def msg_id(self) -> str:
        """消息ID"""
        return self.d.get("id", "")
    @property
    def attachments(self) -> AttrDict:
        """附件"""
        return self.d.get("attachments", AttrDict({}))
    @property
    def content(self) -> str:
        """消息内容"""
        base_content = self.d.get("content", "")
        if self.event_type == "频道艾特":
            base_content = base_content.replace(f"<@!13449081469700666290>", "")
        while base_content.startswith(" "):  # 去掉开头的空格
            base_content = base_content[1:]
        attachments = self.attachments
        if not attachments or (isinstance(attachments, AttrDict) and not attachments.to_dict()):
            return base_content
        # 将attachments转换为可处理的格式
        if isinstance(attachments, AttrDict):
            attachment_data = attachments.to_dict()
        else:
            attachment_data = attachments
        
        # 处理附件
        if isinstance(attachment_data, list):
            for attachment in attachment_data:
                if isinstance(attachment, AttrDict):
                    attachment = attachment.to_dict()
                if isinstance(attachment, dict):
                    filename = attachment.get('filename', '')
                    file_url = attachment.get('url', '')
                    content_type = attachment.get('content_type', '')
                    attachment_str = ""
                    if "image" in content_type:
                        attachment_str += f"[图片:{filename}][URL: {file_url}]"
                    elif "file" in content_type:
                        attachment_str += f"[文件:{filename}][URL: {file_url}]"
                    elif "voice" in content_type:
                        attachment_str += f"[语音:{filename}][URL: {file_url}]"
                    elif "video" in content_type:
                        attachment_str += f"[视频:{filename}][URL: {file_url}]"
                    else:
                        attachment_str += f"[{content_type}附件: {filename}][URL: {file_url}]"
        return f"{base_content} {attachment_str}".strip()

    @property
    def timestamp(self) -> str:
        """消息时间戳"""
        return self.d.get("timestamp", "")
    @property
    def author(self) -> AttrDict:
        """消息作者列表（author）"""
        return self.d.get("author", AttrDict({}))
    @property
    def user_id(self) -> str:
        """消息发送者QQ互联ID"""
        return self.author.get("union_openid", "")
    
    def __init__(self, data: Union[Dict, str]):
        # 关键修复：调用父类构造函数初始化基础属性
        super().__init__(data)
        # 现在可以安全访问属性

class OpenAPIErrorPayload(BaseModel):
    """OpenAPI错误响应体"""
    message: str = ""
    code: int = 0

class MarkdownPayload:
    """Markdown消息体
    
    Markdown应符合以下规范：

    - content: str 无需填写
    - custom_template_id: str 自定义模板ID
    - params: Dict[str, List[str]] 自定义模板参数 以key values[]为一对填入

    详见：https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/type/markdown.html
    """
    def __init__(self, payload: Optional[Dict] = None):
        self._payload = payload or {}
        self.content: str = self._payload.get('content', None)
        self.custom_template_id: str = self._payload.get('custom_template_id', '')
        self.params: Dict[str, List[str]] = self._payload.get('params', {})
    
    def to_dict(self) -> Dict[str, Any]:
        if not self.custom_template_id:
            return None
        return {
            'content': self.content,
            'custom_template_id': self.custom_template_id,
            'params': self.params
        }

class KeyboardPayload:
    """消息按钮 消息体
    
    结构：
    - keyboard_id: str 按钮ID # 此为模板响应
    --- 
    - content: Dict 按钮内容 # 此为自定义响应
        - rows: List[Dict] 按钮行
            - buttons: List[Dict] 按钮列表
                - id: str 按钮ID
                - render_data: Dict 渲染数据
                    - label: str 按钮标签
                    - visited_label: str 点击后标签
                - action: Dict 按钮动作
                    - type: int 动作类型
                    - permission: Dict 权限
                        - type: int 权限类型
                    - data: str 动作数据
                    - reply: bool 是否回复
    
    详见：https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/trans/msg-btn.html
    """
    def __init__(self, keyboard_id: str = None, payload: Optional[Dict] = None):
        self.keyboard_id: str = keyboard_id
        self._payload = payload or {}
        self.content: Dict = self._payload.get('content', {})
        self.rows: List[Dict] = self.content.get('rows', [])
    
    def to_dict(self) -> Dict[str, Any]:
        if self.keyboard_id:
            return {
                'id': self.keyboard_id
            }
        if not self.rows: return None
        return {
            'content': {
                'rows': self.rows
            }
        }

class ArkPayload:
    """Ark 消息体
    
    - template_id: str 为模板ID 默认可用23/24/37
    - kv: List[Dict] 键值对列表 具体内容见开放平台
    
    详见：https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/type/ark.html
    """
    def __init__(self, payload: Optional[Dict] = None):
        self._payload = payload or {}
        self.template_id: str = self._payload.get('template_id', 0)
        self.kv: List[Dict] = self._payload.get('kv', [])
    
    def to_dict(self) -> Dict[str, Any]:
        if not self.template_id: return None
        return {
            'template_id': self.template_id,
            'kv': self.kv
        }

class MediaPayload:
    """从MediaUploadPayload中传回的数据塞这里"""
    def __init__(self, payload: Optional[Dict] = None):
        self._payload = payload or {}
        self.file_uuid: str = self._payload.get('file_uuid', '')
        self.file_info: str = self._payload.get('file_info', '')
        self.ttl: int = self._payload.get('ttl', 0)
        self.id: str = self._payload.get('id', '')
        self.url: str = self._payload.get('url', '')
    
    def to_dict(self) -> Dict[str, Any]:
        if not self.file_info: return None
        return {
            'file_uuid': self.file_uuid,
            'file_info': self.file_info,
            'ttl': self.ttl,
            'id': self.id
        }

class MediaUploadPayload:
    """媒体上传
    
    - file_type: int 1图片 2视频 3语音 4文件（不开放） 默认1
    - url: str 媒体资源URL
    - srv_send_msg: bool True会用主动方式发送 默认False
    - event: MessageEventPayload 事件对象 用于获取发送目标

    详见：https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/rich-media.html

    Powered by AxTn Network 2023-2025
    """
    def __init__(
        self,
        file_type: int = 1,
        url: str = None,
        srv_send_msg: bool = False,
        event: MessageEventPayload = None,
    ):
        self.file_type: int = file_type
        self.url: str = url
        self.srv_send_msg: bool = srv_send_msg
        self.event: Union[MessageEventPayload, GroupMessageEvent] = event

    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_type': self.file_type,
            'url': self.url,
            'srv_send_msg': self.srv_send_msg
        }

class AccessTokenPayload(BaseModel):
    """AccessToken 请求体"""
    access_token: str = ""
    expires_in: int = 114514

class AutoReplyPayload:
    def __init__(self, event, is_direct_message = False):
        self.event = event
        self.is_direct_message = bool(is_direct_message) if is_direct_message else False
        self.content = ""
        self.msg_id = event.msg_id if hasattr(event, 'msg_id') else None
        self.group_id = event.group_id if hasattr(event, 'group_id') else None
        self.channel_id = event.channel_id if hasattr(event, 'channel_id') else None
        self.guild_id = event.guild_id if hasattr(event, 'guild_id') else None
        self.user_id = event.user_id if hasattr(event, 'user_id') else None
        self.markdown: MarkdownPayload = None
        self.ark: ArkPayload = None
        self.media: MediaPayload = None
        self.keyboard: KeyboardPayload = None
        self.image = None
        self.event_id: str = None
        self.msg_seq: int = 1

    def set_content(self, content):
        self.content = content
        return self

    def set_markdown(self, markdown: MarkdownPayload = None):
        self.markdown = markdown
        return self

    def set_ark(self, ark: ArkPayload = None):
        self.ark = ark
        return self

    def set_media(self, media: MediaPayload = None):
        self.media = media
        return self
    def set_image(self, image: str = None):
        self.image = image
        return self

    def set_seq(self, msg_seq: int = None):
        self.msg_seq = msg_seq
        return self
    
    def set_keyboard(self, keyboard: KeyboardPayload = None):
        self.keyboard = keyboard
        return self


class MessageSenderBasePayload:    
    def __init__(self, payload: Union[Dict[str, Any], str] = None):
        """
        Payload基本格式规范

        详见 https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/send-receive/send.html

        :param payload: 可以是字典、JSON字符串或None（创建空对象）
        :param payload.msg_type: 消息类型 默认0文本 2markdown 3ark 4embed 7富媒体
        :param payload.event_id: 事件ID
        :param payload.msg_id: 消息ID
        :param payload.msg_seq: 消息序列号
        :param payload.markdown: Markdown消息体
        :param payload.keyboard: 按钮消息体
        :param payload.ark: Ark消息体
        :param payload.media: 媒体消息体
        :param payload.image: 图片URL（仅适用于频道/频私发送图片）

        Powered by [AxTn Network](https://www.axtrk.com) 2023-2025
        """
        if payload is None:
            self._raw_data = {}  # 支持创建空对象
        elif isinstance(payload, str):
            self._raw_data = json.loads(payload)
        else:
            self._raw_data = payload or {}

        self.content: str = self._raw_data.get('content', '')
        self.msg_type: int = self._raw_data.get('msg_type', 0)
        self.event_id: str = self._raw_data.get('event_id', '')
        self.msg_id: str = self._raw_data.get('msg_id', '')
        self.msg_seq: int = self._raw_data.get('msg_seq', 1)

        self.markdown: MarkdownPayload = MarkdownPayload(self._raw_data.get('markdown'))
        self.keyboard: KeyboardPayload = KeyboardPayload(self._raw_data.get('keyboard'))
        self.ark: ArkPayload = ArkPayload(self._raw_data.get('ark'))
        self.media: MediaPayload = MediaPayload(self._raw_data.get('media'))
        self.image: str = self._raw_data.get('image', '')

    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典"""
        result = {
            "content": self.content,
            'msg_type': self.msg_type,
            'msg_id': self.msg_id,
            'msg_seq': self.msg_seq
        }

        if self.markdown:
            result['markdown'] = self.markdown.to_dict()
        if self.event_id:
            result['event_id'] = self.event_id
        if self.keyboard.rows:
            result['keyboard'] = self.keyboard.to_dict()
        if self.ark.template_id or self.ark.kv:
            result['ark'] = self.ark.to_dict()
        if self.media.file_uuid:
            result['media'] = self.media.to_dict()
        if self.image:
            result['image'] = self.image
        if self.keyboard:
            result['keyboard'] = self.keyboard.to_dict()

        return result

class MessageSenderOverPayload:
    """QQ侧 消息发送结果"""
    id: str = ""
    timestamp: int = 0

# ====================== 具体事件子类 ======================

class GuildMessageEvent(MessageEventPayload):
    """频道消息事件处理"""
    def __init__(self, data: Union[Dict, str]):
        # 调用父类初始化链
        super().__init__(data)
        logger.info(f"频道消息 | 频道ID：{self.guild_id} | 用户ID：{self.user_id} >>> {self.content}")
    @property
    def channel_id(self) -> str:
        return self.d.get("channel_id", "")
    @property
    def guild_id(self) -> str:
        return self.d.get("guild_id", "")
    @property
    def mentions(self) -> List[AttrDict]:
        return self.d.get("mentions", [])
    def is_direct_message(self) -> bool:
        """是否是私信消息"""
        return self.t == "DIRECT_MESSAGE_CREATE"
    async def reply(self, content: str, markdown: MarkdownPayload = None, msg_id: str = None, ark: ArkPayload = None, media: MediaPayload = None, keyboard: KeyboardPayload = None, msg_seq: int = None):
        """快捷回复方法"""
        auto_payload = AutoReplyPayload(self, self.t == "DIRECT_MESSAGE_CREATE").set_content(content)
        if markdown:
            auto_payload.set_markdown(markdown)
        if ark:
            auto_payload.set_ark(ark)
        if media.url:
            auto_payload.set_image(media.url)
        if keyboard:
            auto_payload.set_keyboard(keyboard)
        if msg_seq:
            auto_payload.set_seq(msg_seq)

        from src.Utils.MessageSender import send_auto_reply
        await send_auto_reply(auto_payload)

class GroupMessageEvent(MessageEventPayload):
    """群消息事件处理"""
    def __init__(self, data: Union[Dict, str]):
        # 调用父类初始化链
        super().__init__(data)
        logger.info(f"群消息 | 群ID：{self.group_id} | 用户ID：{self.user_id} >>> {self.content}")
    @property
    def group_id(self) -> str:
        return self.d.get("group_id", "")

    async def reply(self, content: str = None, markdown: MarkdownPayload = None, msg_id: str = None, ark: ArkPayload = None, media: MediaPayload = None, keyboard: KeyboardPayload = None, msg_seq: int = None):
        """快捷回复方法"""
        auto_payload = AutoReplyPayload(self).set_content(content)
        if markdown:
            auto_payload.set_markdown(markdown)
        if ark:
            auto_payload.set_ark(ark)
        if media:
            auto_payload.set_media(media)
        if keyboard:
            auto_payload.set_keyboard(keyboard)
        if msg_seq:
            auto_payload.set_seq(msg_seq)
        from src.Utils.MessageSender import send_auto_reply
        await send_auto_reply(auto_payload)

class PrivateMessageEvent(MessageEventPayload):
    """私聊消息事件处理"""
    def __init__(self, data: Union[Dict, str]):
        # 调用父类初始化链
        super().__init__(data)
        logger.info(f"私聊消息 | 用户ID：{self.user_id} >>> {self.content}")

    async def reply(self, content: str, markdown: MarkdownPayload = None, msg_id: str = None, ark: ArkPayload = None, media: MediaPayload = None, keyboard: KeyboardPayload = None, msg_seq: int = None):
        """快捷回复方法"""
        auto_payload = AutoReplyPayload(self).set_content(content)
        if markdown:
            auto_payload.set_markdown(markdown)
        if ark:
            auto_payload.set_ark(ark)
        if media:
            auto_payload.set_media(media)
        if keyboard:
            auto_payload.set_keyboard(keyboard)
        if msg_seq:
            auto_payload.set_seq(msg_seq)
        from src.Utils.MessageSender import send_auto_reply
        await send_auto_reply(auto_payload)

class ValidationEvent(QQBasePayload):
    """验证事件处理"""
    def __init__(self, data: Union[Dict, str]):
        # 调用父类初始化链
        super().__init__(data)
        logger.debug(f"时间：{self.event_ts} | 事件：验证处理 | 验证段：{self.d.to_dict()}")
    @property
    def plain_token(self) -> str:
        return self.d.get("plain_token", "")

    @property
    def event_ts(self) -> str:
        return self.d.get("event_ts", "")

    def generate_response(self, request: Request) -> Dict[str, str]:
        """生成验证响应"""
        return QQBasePayload.generate_validation_response(request)

class GroupEvent(QQBasePayload):
    """群机器人事件处理"""
    def __init__(self, data: Union[Dict, str]):
        # 调用父类初始化链
        super().__init__(data)
        self.group_id = self.d.get("group_openid", "")
        self.op_member_id = self.d.get("op_member_openid", "")
        self.timestamp = self.d.get("timestamp", "")
        self.event_id = self.id

    async def reply(self, content: str, markdown: MarkdownPayload = None, msg_id: str = None, ark: ArkPayload = None, media: MediaPayload = None, keyboard: KeyboardPayload = None):
        """快捷回复方法"""
        auto_payload = AutoReplyPayload(self).set_content(content)
        auto_payload.event_id = self.event_id
        if markdown:
            auto_payload.set_markdown(markdown)
        if ark:
            auto_payload.set_ark(ark)
        if media:
            auto_payload.set_media(media)
        if keyboard:
            auto_payload.set_keyboard(keyboard)
        from src.Utils.MessageSender import send_auto_reply
        await send_auto_reply(auto_payload)

class GuildEvent(QQBasePayload):
    """频道管理事件处理"""
    def __init__(self, data: Union[Dict, str]):
        # 调用父类初始化链
        super().__init__(data)
        owner_id = self.d.get("owner_id", "")
        guide_name = self.d.get("name", "")
        if self.t == "GUILD_UPDATE":
            logger.info(f"频道更新 | 频道ID：{self.guild_id} | 频道主ID：{owner_id} | 频道名称：{guide_name}")
        if self.t == "GUILD_CREATE":
            logger.info(f"频道创建 | 频道ID：{self.guild_id} | 频道主ID：{owner_id} | 频道名称：{guide_name}")
        if self.t == "GUIDE_DELETE":
            logger.info(f"频道删除 | 频道ID：{self.guild_id} | 频道主ID：{owner_id} | 频道名称：{guide_name}")
    @property
    def guild_id(self) -> str:
        return self.d.get("guild_id", "")


class InterActionEvent(QQBasePayload):
    """互动事件处理"""
    def __init__(self, data: Union[Dict, str]):
        # 调用父类初始化链
        super().__init__(data)

        self.timestamp = self.d.get("timestamp", "")
        self.event_id = self.id
        self._data: dict = self.d.get("data", "")
        self._resolved: dict = self._data.get("resolved", "")
        self.button_data = self._resolved.get("button_data", "")
        self.button_id = self._resolved.get("button_id", "")
        self.scene = self.d.get("scene", "")
        if self.scene == "group":
            self.group_id = self.d.get("group_openid", "")
            self.user_id = self.d.get("group_member_openid", "")
        elif self.scene == "c2c":
            self.user_id = self.d.get("user_openid", "")
        elif self.scene == "guide":
            self.guide_id = self.d.get("guide_id", "")
            self.channel_id = self.d.get("channel_id", "")
            self.user_id = self._resolved.get("user_id", "")

    async def reply(self, content: str, markdown: MarkdownPayload = None, msg_id: str = None, ark: ArkPayload = None, media: MediaPayload = None, keyboard: KeyboardPayload = None):
        """快捷回复方法"""
        auto_payload = AutoReplyPayload(self).set_content(content)
        auto_payload.event_id = self.event_id
        if markdown:
            auto_payload.set_markdown(markdown)
        if ark:
            auto_payload.set_ark(ark)
        if media:
            auto_payload.set_media(media)
        if keyboard:
            auto_payload.set_keyboard(keyboard)
        from src.Utils.MessageSender import send_auto_reply # , accept_interaction
        # await accept_interaction(self.event_id)
        await send_auto_reply(auto_payload)





# ====================== 工厂函数 ======================
def create_payload(payload_data: Union[Dict, str]) -> Union[MessageEventPayload, QQBasePayload]:
    """
    根据Payload数据创建适当的子类实例

    :param payload_data: Payload数据（字典或JSON字符串）

    :return: 对应的Payload子类实例
    """
    # 如果是字符串，先转换为字典
    if isinstance(payload_data, str):
        payload_dict = json.loads(payload_data)
    else:
        payload_dict = payload_data

    # 获取op和t字段
    op = payload_dict.get("op", -1)
    t = payload_dict.get("t", "")

    # 根据op和t选择适当的子类
    if op == 0:  # Dispatch事件
        if t in ["MESSAGE_CREATE", "AT_MESSAGE_CREATE", "DIRECT_MESSAGE_CREATE"]: # 注意：MESSAGE_CREATE仅适用于私域
            return GuildMessageEvent(payload_dict)
        elif t in ["GROUP_AT_MESSAGE_CREATE"]: # 此消息为群聊
            return GroupMessageEvent(payload_dict)
        elif t in ["C2C_MESSAGE_CREATE"]:
            return PrivateMessageEvent(payload_dict)
        elif t in ["GUID_UPDATE", "GUILD_CREATE", "GUILD_DELETE"]:
            return GuildEvent(payload_dict)
        elif t in ["GROUP_ADD_ROBOT", "GROUP_DEL_ROBOT"]:
            return GroupEvent(payload_dict)
        elif t == "INTERACTION_CREATE":
            return InterActionEvent(payload_dict)  

    elif op == 13:  # 验证事件
        return ValidationEvent(payload_dict)

    # 默认返回基类
    return MessageEventPayload(payload_dict)
