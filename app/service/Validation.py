"""
Validation Service for AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import binascii

from app.classes import ValidationEvent
from app.modules import config

APPID = config.appid
BOT_SECRET = config.botsecret

async def validation(validate: ValidationEvent, headers: dict, body: bytes):
    """
    处理验证事件的函数，接收验证事件对象(ValidationEvent)和请求头信息作为参数

    Args:
        validate (ValidationEvent): 验证事件对象，包含验证事件的相关数据
        headers (dict): 请求头信息
        body (bytes): 请求体信息
    Returns:
        plain_token (str): 验证回包信息
        signature (str): 验证回包签名

    详细信息参见：
    - https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/event-emit.html#webhook方式
    """
    if headers.get("User-Agent") != "QQBot-Callback" or headers.get("x-bot-appid") != APPID or headers.get("X-Signature-Method") != "Ed25519":
        raise ValueError("Invalid User-Agent header or APPID. Please ensure that the request is coming from Tencent.")
    ed25519 = headers.get("X-Signature-Ed25519")
    timestamp = validate.event_ts
    message = f"{timestamp}{validate.plain_token}".encode("utf-8")
    bot_secret = BOT_SECRET.encode("utf-8")
    while len(bot_secret) < 32:
        bot_secret += bot_secret
        bot_secret = bot_secret[:32]
    signature = Ed25519PrivateKey.from_private_bytes(bot_secret).sign(message).hex()
    signature_bytes = binascii.unhexlify(ed25519)
    private_key = Ed25519PrivateKey.from_private_bytes(bot_secret)
    public_key = private_key.public_key()
    message2 = timestamp.encode("utf-8") + body
    try:
        public_key.verify(signature_bytes, message2)
    except:
        raise ValueError("Invalid signature. Please ensure that the request is properly signed.")
    return validate.plain_token, signature

async def validation_msg(headers: dict, body: bytes) -> bool:
    """
    处理消息事件的函数，接收消息事件对象和请求头信息作为参数

    Args:
        message (Message): 消息事件对象，包含消息事件的相关数据
        headers (dict): 请求头信息
        body (bytes): 请求体信息
    Returns:
        plain_token (str): 验证回包信息
        signature (str): 验证回包签名

    详细信息参见：
    - https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/event-emit.html#webhook方式
    """
    if headers.get("x-bot-appid") != APPID or headers.get("X-Signature-Method") != "Ed25519" or headers.get("User-Agent") != "QQBot-Callback":
        raise ValueError("Invalid User-Agent header. Please ensure that the request is coming from Tencent QQ Bot.")
    ed25519 = headers.get("X-Signature-Ed25519")
    timestamp = headers.get("X-Signature-Timestamp")
    signature_bytes = binascii.unhexlify(ed25519)
    bot_secret = BOT_SECRET.encode("utf-8")
    while len(bot_secret) < 32:
        bot_secret += bot_secret
        bot_secret = bot_secret[:32]
    private_key = Ed25519PrivateKey.from_private_bytes(bot_secret)
    public_key = private_key.public_key()
    message2 = timestamp.encode("utf-8") + body
    try:
        public_key.verify(signature_bytes, message2)
    except:
        raise ValueError("Invalid signature. Please ensure that the request is properly signed.")
    return True