from Core.Event import group_handle_event, send_group_message
from utils.jrrp import get_jrrp


@group_handle_event('jrrp','/jrrp')
async def jrrp_handler(event):
    content1, msgtype = await get_jrrp(event.user_id)
    if msgtype == 0:
        await send_group_message(group_openid=event.group_openid, content=content1, msg_type=0, msg_id=event.msg_id)
    elif msgtype == 2:
        await send_group_message(group_openid=event.group_openid, markdown=content1, content=" ", msg_type=2, msg_id=event.msg_id)

