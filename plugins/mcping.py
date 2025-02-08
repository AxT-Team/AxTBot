from Core.Event import group_handle_event, send_group_message
from utils.mcping import mcping


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
            await send_group_message(event.group_openid, msg_type=0, content=await mcping(msg), msg_id=event.msg_id)
            return