"""
Entry File For QQ Adapter Service

Author: Shanshui2024
Organization: AxT-Team
"""

from app.service.qq_service.Validation import validation as service_validation
from app.service.qq_service.Validation import validation_msg as service_validation_msg
from app.service.qq_service.Interact import interaction_reply
from app.service.qq_service.MsgSender import (
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