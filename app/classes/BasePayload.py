"""
Class File for Webhook Base Payload

Author: Shanshui2023
Organization: AxT-Team
"""
from pydantic import BaseModel

class BasePayload(BaseModel):
    """
    所有Webhook事件的基础模型，包含公共字段
    """
    id: str | None = None
    op: int = 0
    s: int | None = None
    t: str | None = None
    d: dict