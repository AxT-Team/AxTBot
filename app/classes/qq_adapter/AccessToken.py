"""
Class File For the AccessToken Model

Author: Shanshui2024
Organization: AxT-Team
"""
from pydantic import BaseModel

class AccessToken(BaseModel):
    """
    AccessToken模型，用于存储和验证访问令牌
    """
    access_token: str | None = None
    expires_in: int | None = None