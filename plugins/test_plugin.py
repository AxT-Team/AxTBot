from app import on_command, on_message, on_interaction, on_all_message
from app.classes import GroupMessage, PrivateMessage, Message, QQInteraction, SessionManager
from app.modules import logger
from app.service import interaction_reply


@on_command("hello")
async def handle_function(event: Message):
    if event.author.bot:
        logger.debug("测试插件 >>> 收到机器人消息，忽略") # 新增机器人消息验证
        return
    if event.is_you:
        logger.info("测试插件 >>> 收到AT消息！")
    else:
        logger.info("测试插件 >>> 收到测试消息")

@on_command("hello")
async def handle_function(event: PrivateMessage): # 请注意 此处有先后顺序 如果上面的Message先被处理，则该行不被处理
    logger.info("测试插件 >>> 接收到私聊消息")

@on_interaction(11)
async def handle_button_click(event: QQInteraction):
    resolved = event.data.resolved
    logger.debug(f"测试插件 >>> 你点击了: {resolved.button_id} | 数据为: {resolved.button_data}")
    if resolved.button_data == "同意协议" and resolved.button_id == "read_and_agree":
        await interaction_reply(event.id, 1) # 数字似乎无效 不清楚开放平台这么做的目的是什么

@on_all_message()
async def handle_function(event):
    logger.debug("测试插件 >>> 收到消息！")   # 接收所有文字消息！


@on_command("ask") # Session消息（测试中）
async def ask(event: GroupMessage):
    session_id = f"{event.author.member_openid}_{event.group_id}"
    session = SessionManager.create(session_id, timeout=30)
    await event.reply("请告诉我你的问题（30秒内回复）")
    try:
        reply = await session.wait_for_message()
        # 处理 reply
        await event.reply(f"你问了: {reply.content}")
    except TimeoutError:
        await event.reply("超时，会话结束")
    finally:
        SessionManager.remove(session_id)