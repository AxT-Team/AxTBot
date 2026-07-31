from app import on_command, on_message
from app.classes import GroupMessage
from app.modules import logger
from app.service import interaction_reply


@on_command("hello")
async def handle_function(event: GroupMessage):
    if event.author.bot:
        logger.debug("测试插件 >>> 收到机器人消息，忽略") # 新增机器人消息验证
        return
    if event.is_you:
        logger.info("测试插件 >>> 收到AT消息！")
    else:
        logger.info("测试插件 >>> 收到测试消息")

# 计划开发新的装饰器 包括互动信息回调