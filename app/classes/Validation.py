"""
Class File for Webhook Validation Event

Author: Shanshui2023
Organization: AxT-Team
"""


from pydantic import BaseModel

class Validation(BaseModel):
    """
    用于验证Webhook事件数据的Pydantic模型
    """
    plain_token: str
    event_ts: str