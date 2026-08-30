"""
Entry File For Validation Service

Author: Shanshui2024
Organization: AxT-Team
"""

from app.service.qq_service import (
    service_validation,
    service_validation_msg,
    interaction_reply,
    send_message,
    send_group_message,
    send_c2c_message,
    reply_group_message,
    reply_c2c_message,
)
from app.service.Message import message_process as service_message_process
from app.service.cert_service import certificate_service
from app.service.qq_service import upload_media, upload_by_url, upload_local, upload_image_link

__all__ = [
    service_validation,
    service_validation_msg,
    service_message_process,
    certificate_service,
    interaction_reply,
    send_message,
    send_group_message,
    send_c2c_message,
    reply_group_message,
    reply_c2c_message,
    upload_media,
    upload_by_url,
    upload_local,
    upload_image_link,
]
