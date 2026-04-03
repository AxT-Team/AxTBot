"""
Class File For the AccessToken Model

Author: Shanshui2023
Organization: AxT-Team
"""
from pydantic import BaseModel

class AccessToken(BaseModel):
    """
    AccessToken模型，用于存储和验证访问令牌
    """
    access_token: str
    expires_in: int