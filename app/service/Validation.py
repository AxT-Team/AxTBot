"""
Validation Service for AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from app.classes import ValidationEvent

async def validation(validate: ValidationEvent, headers: dict):
    """
    处理验证事件的函数，接收验证事件对象(ValidationEvent)和请求头信息作为参数

    Args:
        validate (ValidationEvent): 验证事件对象，包含验证事件的相关数据
        headers (dict): 请求头信息
    Returns:
        plain_token (str): 验证回包信息
        signature (str): 验证回包签名

    详细信息参见：
    - https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/event-emit.html#webhook方式
    """
    if headers.get("User-Agent") != "QQBot-Callback" or headers.get("X-Bot-Appid") != "appid":
        raise ValueError("Invalid User-Agent header or APPID.Please ensure that the request is coming from Tencent.")
    return "test1", "test2"