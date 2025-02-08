import json
import re
from Core.Event import group_handle_event, send_group_message, upload_media
from utils.get_uapis import get_touch_url


@group_handle_event('摸','/摸')
async def touch_handler(event):
    if event.content in ['摸','/摸','/摸 ','摸 ']:
        content = "\n=======摸一摸菜单=======" + "\n" + \
                   "/摸 [QQ号] - 生成摸一摸GIF" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /摸 3889003621" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "如果指令发送后提示被去重，则可能是QQ开放平台侧的问题，请等1分钟左右再重试一次" + "\n" + \
                   "=========================="
        await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
    else:
        if re.match(r"(?:/)?摸\s*(\d+)", event.content):
            try:
                qqid = int(re.match(r"(?:/)?摸\s*(\d+)", event.content).group(1))
            except ValueError:
                await send_group_message(event.group_openid, msg_type=0, content="输入值有误，请输入QQ号。", msg_id=event.msg_id)
                return
            response = await upload_media(event.group_openid, 1, await get_touch_url(qqid), False)
            await send_group_message(event.group_openid, msg_type=7, content=" ", msg_id=event.msg_id, media=response)
