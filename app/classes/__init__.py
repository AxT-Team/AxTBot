"""
Class File for the WebHook Logic

Author: Shanshui2024
Organization: AxT-Team
"""

from .Validation import Validation as ValidationEvent
from .BaseWebhook import BaseWebhookEvent

__all__ = ["ValidationEvent", "BaseWebhookEvent"]