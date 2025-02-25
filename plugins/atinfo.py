from Core.Event import group_handle_event, get_message_count, send_group_message
from utils.get_system_info import get_system_info
from Core.Auth import auth


@group_handle_event("/atinfo","atinfo")
async def atinfo(event):
    info = await get_system_info()
    gr = await get_message_count("GROUP_AT_MESSAGE_CREATE")
    gs = await get_message_count("GROUP_AT_MESSAGE_SEND")
    pr = await get_message_count("C2C_MESSAGE_CREATE")
    guildr = await get_message_count("DIRECT_MESSAGE_CREATE")
    guilds = await get_message_count("AT_MESSAGE_CREATE")
    reply = "\nAxTBot Public v 2.0\n" + \
              "===============" + "\n" + \
              "CPU: " + info["cpu_usage"] + "\n" + \
              "RAM: " + info["ram_usage"] + "\n" + \
              "====消息数统计====" + "\n" + \
              "群聊收/发: " + str(gr) + "/" + str(gs) + "\n" + \
              "私聊收/发: " + str(pr) + "\n" + \
              "频道收/发: " + str(guilds) + "\n" + \
              "频道私聊收/发: " + str(guildr) + "\n" + \
              "===============" + "\n" + \
              "已正常运行" + "\n" + \
              str(auth.get_current_run_time()) + "\n" + \
              "===============" + "\n" + \
              "官方社区群: 832275338" + "\n" + \
              "==============="

    await send_group_message(event.group_openid, msg_type=0, content=reply, msg_id=event.msg_id)
    return