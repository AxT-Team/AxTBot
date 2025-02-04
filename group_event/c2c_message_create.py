from botpy.message import C2CMessage
from datetime import datetime

async def handle_c2c_message_create(client, message: C2CMessage):
    msg = message.content.lstrip()
    print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]" + "[私聊消息]" + " | 用户ID:" + message.author.member_openid + " | 消息ID:" + message.id + " | " + msg)
