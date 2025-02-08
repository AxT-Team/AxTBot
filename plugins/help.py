from Core.Event import group_handle_event, send_group_message

@group_handle_event('/help', '/help ', 'help', 'help ')
async def help_handler(event):
    content = "\n=======AxT社区机器人=======" + "\n" + \
                   "| help | - 获取帮助菜单" + "\n" + \
                   "| ping | - 显示Ping菜单" + "\n" + \
                   "| ipinfo | - 显示IPInfo菜单" + "\n" + \
                   "| whois | - 显示Whois菜单" + "\n" + \
                   "| hotlist | - 显示每日热榜菜单" + "\n" + \
                   "| mc | - 查询Minecraft相关内容" + "\n" + \
                   "| jrrp | - 获取今日人品" + "\n" + \
                   "| remake | - 重来一世 你会变成什么" + "\n" + \
                   "| ask | - 读赛博之书 品百味人生" + "\n" + \
                   "===============" + "\n" + \
                   "官方社区群: 832275338" + "\n" + \
                   "===============" + "\n" + \
                   "AxTBot Public v 2.0"
    await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)