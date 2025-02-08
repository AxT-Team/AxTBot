from Core.Event import group_handle_event, send_group_message
from utils.remake import remake


@group_handle_event("/remake","remake")
async def remake_handler(event):
    msg = event.content
    if msg.startswith(("/remake","remake")):
        result = '\n' + await remake(str(event.user_id))
        await send_group_message(event.group_openid, msg_type=0, content=result, msg_id=event.msg_id)
        return