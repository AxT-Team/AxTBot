from Core.Event import group_handle_event, send_group_message, upload_media
from utils.get_minecraft_info import get_minecraft_uuid, get_player_history, check_server


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
            response = await upload_media(event.group_openid, 1, image_url, False)
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