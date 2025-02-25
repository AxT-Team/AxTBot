from Core.Event import group_handle_event, send_group_message
from utils.jrrp import get_jrrp
        
        
@group_handle_event('jrrp','/jrrp')
async def jrrp_handler(event):
    content1, msgtype = await get_jrrp(event.user_id)
    if not content1:
        return
    if msgtype == 0:
        content_str = str(content1) if isinstance(content1, dict) else content1
        await send_group_message(group_openid=event.group_openid, content=content_str, msg_type=0, msg_id=event.msg_id)
    elif msgtype == 2:
        await send_group_message(group_openid=event.group_openid, markdown=content1, content=" ", msg_type=2, msg_id=event.msg_id) # type: ignore