"""
Class File for InterAction Creation Payload

Author: Shanshui2024 & DeepSeek V4
Organization: AxT-Team
"""
from pydantic import BaseModel
from typing import Optional

# 1. 定义 data.resolved 内部的结构
class ResolvedData(BaseModel):
    button_data: str
    button_id: str

# 2. 定义 data 字段的结构（顶层 data 是一个对象）
class DataField(BaseModel):
    type: int
    resolved: ResolvedData

# 3. 定义最外层的完整数据包
class Interaction(BaseModel):
    id: str
    application_id: str | None = None
    type: int
    data: DataField
    version: int
    chat_type: int | None = None
    scene: str
    timestamp: str
    group_openid: str | None = None
    group_member_openid: str | None = None
    guild_id: str | None = None
    channel_id: str | None = None
    user_openid: str | None = None