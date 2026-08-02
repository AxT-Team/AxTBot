"""
Class File for the WebHook Logic

Author: Shanshui2024
Organization: AxT-Team
"""

from app.classes.framework.Attachment import Attachment, VoiceAttachment, ImageAttachment, VideoAttachment, FileAttachment, AttachmentList
from app.classes.framework.Message import Author as UnionAuthor, Message as UnionMessage, Mentions as UnionMentions, MessageScene as UnionMessageScene
from app.classes.framework.Metadata import PluginMetadata



__all__ = [
    "Attachment", 
    "VoiceAttachment", 
    "ImageAttachment", 
    "VideoAttachment", 
    "FileAttachment", 
    "AttachmentList", 
    "UnionAuthor", 
    "UnionMessage", 
    "UnionMentions", 
    "UnionMessageScene",
    "PluginMetadata"
]