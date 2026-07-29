from app import on_command, on_message
from app.classes import GroupMessage
from app.modules import logger


@on_command("hello")
async def handle_function(event: GroupMessage):
    if event.is_you:
        logger.info("测试插件 >>> 收到AT消息！")
    else:
        logger.info("测试插件 >>> 收到测试消息")