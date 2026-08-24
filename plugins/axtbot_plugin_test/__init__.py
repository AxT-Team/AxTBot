from fastapi import APIRouter

from app import on_command, on_message, on_interaction, on_all_message
from app.classes import GroupMessage, PrivateMessage, Message, QQInteraction, SessionManager, PluginMetadata, Markdown, Keyboard, KeyboardContent
from app.modules import logger, metadata_registry
from app.service import interaction_reply
from app.router import register_plugin_router

__meta__ = PluginMetadata(
    name="测试插件",
    version="1.0.0",
    author="Shanshui2024",
    description="测试使用的插件",
    # dependencies=["test"],  # 依赖 xxx 插件
    commands=["ask", "hello"],
    priority=5  # 较高优先级 优先级暂不可用
)

@on_command("hello")
async def handle_function(event: Message):
    if event.author.bot:
        logger.debug("测试插件 >>> 收到机器人消息，忽略") # 新增机器人消息验证
        return
    if event.is_you: # 只区分全量消息，非全量消息模式下默认是艾特的 所以不做区分
        logger.info("测试插件 >>> 收到AT消息！")
        await event.reply("收到AT消息！",quote=True)
        rows = {
            "rows": [
                                            {
                                                "buttons": [
                                                    {
                                                    "id": "button_1",
                                                    "render_data": {
                                                        "label": "确认",
                                                        "visited_label": "已确认",
                                                        "style": 1
                                                    },
                                                    "action": {
                                                        "type": 2,
                                                        "permission": {
                                                        "type": 2,
                                                        "specify_role_ids": [],
                                                        "specify_user_ids": []
                                                        },
                                                        "click_limit": 1,
                                                        "data": "/action_confirm",
                                                        "at_bot_show_channel_list": True,
                                                        "reply": True,
                                                        "enter": True
                                                    }
                                                    }
                                                ]
                                            }
                  ]
        }
        await event.reply(
            msg_type=2,
            markdown=Markdown(
                content="# 标题 \n 这是个测试内容 \n --- \n 阅读该内容即证明您已经同意相关协议"
            ), 
            keyboard=Keyboard(content=rows),
            msg_seq=2
        )
                              
        # await event.reply()
    else:
        logger.info("测试插件 >>> 收到测试消息")
        await event.reply("收到测试消息！",quote=True)
        rows = {
            "rows": [
                                            {
                                                "buttons": [
                                                    {
                                                    "id": "button_1",
                                                    "render_data": {
                                                        "label": "确认",
                                                        "visited_label": "已确认",
                                                        "style": 1
                                                    },
                                                    "action": {
                                                        "type": 2,
                                                        "permission": {
                                                        "type": 2,
                                                        "specify_role_ids": [],
                                                        "specify_user_ids": []
                                                        },
                                                        "click_limit": 1,
                                                        "data": "/action_confirm",
                                                        "at_bot_show_channel_list": True,
                                                        "reply": True,
                                                        "enter": True
                                                    }
                                                    }
                                                ]
                                            }
                  ]
        }
        await event.reply(
            msg_type=2,
            markdown=Markdown(
                content="# 标题 \n 这是个测试内容 \n --- \n 阅读该内容即证明您已经同意相关协议"
            ), 
            keyboard=Keyboard(content=rows),
            msg_seq=2
        )
@on_message("hello")
async def handle_function(event: Message):
    logger.info("测试插件 >>> 收到消息类命令！")

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


@on_command("ask") # Session消息 目前仅支持最大60秒的超时时间 过长会被函数处理器处理掉
async def ask(event: GroupMessage):
    session_id = f"{event.author.member_openid}_{event.group_id}"
    session = SessionManager.create(session_id, timeout=30)
    logger.debug("请告诉我你的问题（30秒内回复）")
    try:
        reply: GroupMessage = await session.wait_for_message()
        # 处理 reply
        logger.debug(f"你问了: {reply.content}")
    except TimeoutError:
        logger.debug("超时，会话结束")
    finally:
        SessionManager.remove(session_id)
@on_command("help")
async def show_help(event):
    help_text = "📚 可用插件列表:"
    for name, meta in metadata_registry.items():
        help_text += f"\n- {name} v{meta.version}: {meta.description}"
        for command in meta.commands:
            help_text += f"\n  - {command}"
    logger.info(help_text)



router = APIRouter(prefix="/test", tags=["Test"]) # 提供统一的注册挂靠

@router.get("/test")
def test():
    return None