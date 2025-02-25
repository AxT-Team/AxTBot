from Core.Event import group_handle_event, send_group_message, upload_media
from utils.get_minecraft_info import get_minecraft_uuid, get_player_history, check_server, get_mcserver_info
from utils.get_hypixel_info import get_hypixel_info


@group_handle_event("/mc", "mc", "/mchead", "mchead", "/mcskin", "mcskin", "/mcbody", "mcbody")
async def mc_handler(event):
    if event.content in ["/mc", "/mc ", "mc", "mc ", "/mchead ", "/mchead", "mchead ", "mchead", "/mcskin ", "/mcskin", "mcskin ","mcskin", "/mcbody ", "/mcbody", "mcbody ", "mcbody"]:
        content = "\n======Minecraft查询菜单======" + "\n" + \
                   "/mc [ID] - 查询玩家UUID及历史用户名" + "\n" + \
                   "/mcskin [ID] - 查询玩家皮肤" + "\n" + \
                   "/mchead [ID] - 查询玩家皮肤Head" + "\n" + \
                   "/mcbody [ID] - 查询玩家皮肤Body" + "\n" + \
                   "==========================" + "\n" + \
                   "[ID]为玩家用户名" + "\n" + \
                   "=========================="
        await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
    else:
        msg = event.content
        if msg.startswith(("/mc ","mc ")) and len(msg.split(" ")) > 1:
            player_name = msg.split(" ")[1]
            uuid = await get_minecraft_uuid(player_name)
            if uuid is None:
                await send_group_message(event.group_openid, msg_type=0, content="未查询到该玩家的信息", msg_id=event.msg_id)
                return
            history_info = await get_player_history(uuid)
            if history_info is not None:
                formatted_history = history_info
            else:
                formatted_history = "未查询到当前玩家的历史用户名信息"
            contents = f"\n===Minecraft玩家查询===\n| 玩家名: {player_name}\n| UUID: {uuid}\n===历史用户名===\n{formatted_history}"
            await send_group_message(event.group_openid, msg_type=0, content=contents, msg_id=event.msg_id)

        async def post_minecraft_image(avatar_type, content):
            player_name = msg.split(" ")[1]
            uuid = await get_minecraft_uuid(player_name)
            if uuid is None:
                await send_group_message(event.group_openid, msg_type=0, content="未查询到该玩家的信息", msg_id=event.msg_id)
                return
            image_url = f"https://crafatar.com/{avatar_type}{uuid}"
            response ,code = await upload_media(event.group_openid, 1, image_url, False)
            await send_group_message(event.group_openid, msg_type=7, content=" ", msg_id=event.msg_id, media=response)

        if msg.startswith(("/mchead ","mchead ")) and len(msg.split(" ")) > 1:
            await post_minecraft_image("avatars/", "未查询到该玩家的信息")
            return
        
        if msg.startswith(("/mcbody ","mcbody ")) and len(msg.split(" ")) > 1:
            await post_minecraft_image("renders/body/", "未查询到该玩家的信息")
            return

        if msg.startswith(("/mcskin ","mcskin ")) and len(msg.split(" ")) > 1:
            await post_minecraft_image("skins/", "未查询到该玩家的信息")
            return


@group_handle_event('/mcstatus', 'mcstatus')
async def mcstatus_handler(event):
    if event.content in ['/mcstatus','/mcstatus ', 'mcstatus', 'mcstatus ']:
        result = '\n' + await check_server()
        await send_group_message(event.group_openid, msg_type=0, content=result, msg_id=event.msg_id)
        return
    
@group_handle_event("/mcping","mcping")
async def mcping_handler(event):
    if event.content in ["/mcping","/mcping ","mcping","mcping "]:
        content = "\n=======服务器查询菜单=======" + "\n" + \
                   "/mcping [IP]:[端口] [服务器类型] - 请求该服务器信息" + "\n" + \
                   "可选的服务器类型有:" + "\n" + \
                   "- java | Java Edition服务器" + "\n" + \
                   "- be | BedRock 基岩服务器" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /mcping mc,hypixel,net" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，则可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "=========================="
        await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
    else:
        msg = event.content
        if msg.startswith(("/mcping ","mcping ")):
            await send_group_message(event.group_openid, msg_type=0, content=await get_mcserver_info(msg), msg_id=event.msg_id)
            return

@group_handle_event('hyp','/hyp')
async def hyp_handler(event):
    content="\n" + await get_hypixel_info(event.content, event.msg_id)
    await send_group_message(group_openid=event.group_openid, content=content, msg_type=0, msg_id=event.msg_id)