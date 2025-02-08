from Core.Event import group_handle_event, send_group_message
from utils.get_uapis import get_answer_book


@group_handle_event('/ask', 'ask')
async def steam_handler(event):
    msg = event.content
    if msg.startswith(("/ask ","ask ")):
        info = await get_answer_book()
        content = "\n" + info
        await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
        return