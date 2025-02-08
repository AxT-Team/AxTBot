from Core.Event import group_handle_event, send_group_message
from utils.get_hypixel_info import get_hypixel_info


@group_handle_event('hyp','/hyp')
async def hyp_handler(event):
    content="\n" + await get_hypixel_info(event.content, event.msg_id)
    await send_group_message(group_openid=event.group_openid, content=content, msg_type=0, msg_id=event.msg_id)

