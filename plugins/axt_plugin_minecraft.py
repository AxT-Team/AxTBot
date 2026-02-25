from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent, MediaUploadPayload
from src.Utils.MessageSender import upload_file

from uapis_extension import (
    get_minecraft_uuid,
    get_player_history,
    check_minecraft_online,
    get_minecraft_info,
    get_hypixel_info,
)


__metadata__ = {
    "name": "[官方插件]Minecraft 信息读取",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "从Uapis请求得到的Minecraft用户账户信息",
    "official": True,
}

@command(["/mc", "mc", "/mchead", "mchead", "/mcskin", "mcskin", "/mcbody", "mcbody"])
async def mc_handler(event: GroupMessageEvent):
    if event.content in ["/mc", "/mc ", "mc", "mc ", "/mchead ", "/mchead", "mchead ", "mchead", "/mcskin ", "/mcskin", "mcskin ","mcskin", "/mcbody ", "/mcbody", "mcbody ", "mcbody"]:
        content = "======Minecraft查询菜单======" + "\n" + \
                   "/mc [ID] - 查询玩家UUID及历史用户名" + "\n" + \
                   "/mcskin [ID] - 查询玩家皮肤" + "\n" + \
                   "/mchead [ID] - 查询玩家皮肤Head" + "\n" + \
                   "/mcbody [ID] - 查询玩家皮肤Body" + "\n" + \
                   "==========================" + "\n" + \
                   "[ID]为玩家用户名" + "\n" + \
                   "=========================="
        await event.reply(content=content)
    else:
        msg = event.content
        if msg.startswith(("/mc ","mc ")) and len(msg.split(" ")) > 1:
            player_name = msg.split(" ")[1]
            uuid = await get_minecraft_uuid(player_name)
            if uuid is None:
                await event.reply(content="未查询到该玩家的信息")
                return
            try:
                history_info = await get_player_history(uuid)
                if history_info is not None:
                    formatted_history = history_info
                else:
                    formatted_history = "未查询到当前玩家的历史用户名信息"
            except Exception:
                formatted_history = "未查询到当前玩家的历史用户名信息"
            contents = f"===Minecraft玩家查询===\n| 玩家名: {player_name}\n| UUID: {uuid}\n===历史用户名===\n{formatted_history}"
            await event.reply(content=contents)

        async def post_minecraft_image(avatar_type, content):
            player_name = msg.split(" ")[1]
            uuid = await get_minecraft_uuid(player_name)
            if uuid is None:
                await event.reply(content="未查询到该玩家的信息")
                return
            image_url = f"https://mc-api.io/render/{avatar_type}{uuid}"
            
            # 记录上传尝试
            from src.Utils.Logger import logger
            logger.debug(f"Minecraft插件 >>> 尝试上传玩家皮肤")
            logger.debug(f"  ├─ 玩家名: {player_name}")
            logger.debug(f"  ├─ UUID: {uuid}")
            logger.debug(f"  ├─ 图片类型: {avatar_type}")
            logger.debug(f"  └─ 图片URL: {image_url}")
            
            response = await upload_file(
                MediaUploadPayload(file_type=1, url=image_url, event=event)
            )
            if response:
                await event.reply(content=
    """请注意：您使用本功能即默认当前玩家贴图无任何不良信息，并允许当前机器人主体进行消息审查。
一切由于贴图存在不良信息导致机器人不可用的行为将受到管控和二次审查，严重者将上报腾讯""", media=response)
            else:
                if event.event_type in ["频道私信", "频道艾特", "私域频道"]:
                    await event.reply(content="上传失败，频道-文字子频道和频道私聊不支持富媒体，请转到群/私聊请求")
                else:
                    logger.error(f"Minecraft插件 >>> 皮肤上传失败")
                    logger.error(f"  ├─ 玩家名: {player_name}")
                    logger.error(f"  ├─ UUID: {uuid}")
                    logger.error(f"  └─ 图片URL: {image_url}")
                    await event.reply(content="获取贴图失败，富媒体文件上传失败。请查看日志了解详情。")

        if msg.startswith(("/mchead ","mchead ")) and len(msg.split(" ")) > 1:
            await post_minecraft_image("face/", "未查询到该玩家的信息")

        if msg.startswith(("/mcbody ","mcbody ")) and len(msg.split(" ")) > 1:
            await post_minecraft_image("bust/", "未查询到该玩家的信息")

        if msg.startswith(("/mcskin ","mcskin ")) and len(msg.split(" ")) > 1:
            await post_minecraft_image("full/", "未查询到该玩家的信息")


@command(["/mcstatus", "mcstatus"])
async def mcstatus_handler(event: GroupMessageEvent):
    if event.content in ['/mcstatus','/mcstatus ', 'mcstatus', 'mcstatus ']:
        result = await check_minecraft_online()
        await event.reply(content=result)

@command(["/mcping","mcping"])
async def mcping_handler(event: GroupMessageEvent):
    if event.content in ["/mcping","/mcping ","mcping","mcping "]:
        content = "=======服务器查询菜单=======" + "\n" + \
                   "/mcping [IP]:[端口] [服务器类型] - 请求该服务器信息" + "\n" + \
                   "可选的服务器类型有:" + "\n" + \
                   "- java | Java Edition服务器" + "\n" + \
                   "- be | BedRock 基岩服务器" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /mcping mc,hypixel,net" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，则可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "=========================="
        await event.reply(content=content)
    else:
        msg = event.content
        if msg.startswith(("/mcping ","mcping ")):
            msg = msg.split(" ")[1]
            await event.reply(content=await get_minecraft_info(msg))

@command(['hyp','/hyp'])
async def hyp_handler(event: GroupMessageEvent):
    content=await get_hypixel_info(event.content, event.msg_id)
    await event.reply(content=content)
