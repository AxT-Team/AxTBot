"""
Entry File For QQ Adapter Service

Author: Shanshui2024
Organization: AxT-Team
"""

from app.service.qq_service.Validation import validation as service_validation
from app.service.qq_service.Validation import validation_msg as service_validation_msg
from app.service.Message import message_process as service_message_process

__all__ = [service_validation, service_validation_msg, service_message_process]