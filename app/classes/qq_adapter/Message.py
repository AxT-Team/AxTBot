"""
Class File for QQ Webhook Message Extension Fields

Author: Shanshui2024
Organization: AxT-Team

本模块仅定义 QQ 平台特有的扩展字段模型。
这些模型不依赖 framework，在 app/classes/__init__.py 中通过多重继承
与 framework 的通用基类合并，生成最终可用的消息模型。
"""
from typing import Optional
from pydantic import BaseModel


class QQAuthorExt(BaseModel):
    """
    QQ 平台为 Author 补充的扩展字段。
    在集成层与 framework.Author 合并使用。
    """
    member_openid: Optional[str] = None
    union_openid: Optional[str] = None
    member_role: Optional[str] = None


class QQMessageExt(BaseModel):
    """
    QQ 平台为 Message 补充的扩展字段。
    在集成层与 framework.Message 合并使用。
    """
    message_type: int