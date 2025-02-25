from Core.Event import group_handle_event, send_group_message
from utils.get_uapis import get_steamid_info


@group_handle_event('/steam', 'steam')
async def steam_handler(event):
    if event.content in ['/steam', '/steam ', 'steam', 'steam ']:
        content = "\n=======Steam账户查询=======" + "\n" + \
                   "/steam [昵称/ID] - 查询指定Steam账户信息" + "\n" + \
                   "=======================" + "\n" + \
                   "使用示例: /steam 114514" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "如果指令发送后提示被去重，则可能是QQ开放平台侧的问题，请等1分钟左右再重试一次" + "\n" + \
                   "======================="
        await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
    else:
        msg = event.content
        if msg.startswith(("/steam ","steam ")):
            result = await get_steamid_info(msg)
            if result:
                await send_group_message(event.group_openid, msg_type=0, content=result, msg_id=event.msg_id)
                return


