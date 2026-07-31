"""
Entry File For Validation Service

Author: Shanshui2024
Organization: AxT-Team
"""

from app.service.qq_service import service_validation, service_validation_msg, interaction_reply
from app.service.Message import message_process as service_message_process

__all__ = [service_validation, service_validation_msg, service_message_process, interaction_reply]