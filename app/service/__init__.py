"""
Entry File For Validation Service

Author: Shanshui2023
Organization: AxT-Team
"""

from app.service.Validation import validation as service_validation
from app.service.Validation import validation_msg as service_validation_msg

__all__ = [service_validation, service_validation_msg]