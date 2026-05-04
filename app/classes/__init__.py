"""
Class File for the WebHook Logic

Author: Shanshui2024
Organization: AxT-Team
"""

from app.classes.Validation import Validation as ValidationEvent
from app.classes.BasePayload import BasePayload
from app.classes.Message import Message, GroupMessage, PrivateMessage
from app.classes.AccessToken import AccessToken
from app.classes.Attachment import Attachment, VoiceAttachment, ImageAttachment, VideoAttachment, FileAttachment, AttachmentList

__all__ = ["ValidationEvent", "BasePayload", "Message", "GroupMessage", "PrivateMessage", "AccessToken", "Attachment", "VoiceAttachment", "ImageAttachment", "VideoAttachment", "FileAttachment", "AttachmentList"]