"""
Class File for Message Attachment

Author: Shanshui2024
Organization: AxT-Team
"""
from pydantic import BaseModel

class Attachment(BaseModel):
    """
    消息附件模型，包含文件名、URL和大小等信息
    """
    filename: str
    url: str
    size: int
    content_type: str
    content: str | None = None

class VoiceAttachment(Attachment):
    """
    语音消息附件模型，继承自Attachment，包含语音时长等信息
    """
    voice_wav_url: str
    asr_refer_text: str | None = None

class ImageAttachment(Attachment):
    """
    图片消息附件模型，继承自Attachment，包含图片宽高等信息
    """
    width: int
    height: int

class VideoAttachment(Attachment):
    """
    视频消息附件模型，继承自Attachment，包含视频时长等信息
    """
    width: int
    height: int

class FileAttachment(Attachment):
    """
    文件消息附件模型，继承自Attachment，包含文件大小等信息
    """
    pass

class AttachmentList(BaseModel):
    """
    消息附件模型
    """
    file: Attachment