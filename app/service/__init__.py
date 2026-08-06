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

__all__ = [
    service_validation,
    service_validation_msg,
    service_message_process,
    interaction_reply,
    send_message,
    send_group_message,
    send_c2c_message,
    reply_group_message,
    reply_c2c_message,
]