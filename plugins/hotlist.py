from Core.Event import group_handle_event, send_group_message
from utils.get_uapis import get_hot_list, format_hot_search


@group_handle_event("/hotlist", "hotlist")
async def hotlist_handler(event):
    if event.content in ["/hotlist", "/hotlist ", "hotlist", "hotlist "]:
        content = "\n=======每日热榜菜单=======" + "\n" + \
                   "/hotlist [热榜类型] - 查询指定热榜信息" + "\n" + \
                   "可选的热榜类型有:" + "\n" + \
                   "- weibo | 微博热搜榜" + "\n" + \
                   "- bilibili | 哔哩哔哩全站日榜" + "\n" + \
                   "- bilihot | 哔哩哔哩热搜榜" + "\n" + \
                   "- zhihu | 知乎热搜榜" + "\n" + \
                   "- douyin | 抖音热搜榜" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /hotlist weibo" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，视为热榜内含有违规信息，被QQ消息审核拦截" + "\n" + \
                   "=========================="
        await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
    else:
        msg: str = event.content
        if msg.startswith(("/hotlist ","hotlist ")) and msg.split(" ")[1] is not None:
            hot_list = None
            hot_type = None

            if msg.split(" ")[1] == "bilibili":
                hot_list = await get_hot_list("bilibili")
                hot_type = "B站-日榜"
            elif msg.split(" ")[1] == "bilihot":
                hot_list = await get_hot_list("bilihot")
                hot_type = "B站-热搜榜"
            elif msg.split(" ")[1] == "weibo":
                hot_list = await get_hot_list("weibo")
                hot_type = "微博-热搜榜"
            elif msg.split(" ")[1] == "zhihu":
                hot_list = await get_hot_list("zhihu")
                hot_type = "知乎-热搜榜"
            elif msg.split(" ")[1] == "douyin":
                hot_list = await get_hot_list("douyin")
                hot_type = "抖音-热搜榜"

            if hot_list is None:
                await send_group_message(event.group_openid, msg_type=0, content='未查询到该热搜信息', msg_id=event.msg_id)
                return
            else:
                content = "\n===" + hot_type + "===" + "\n" + \
                        format_hot_search(hot_list) + "\n" + \
                        "=============" + "\n" + \
                        hot_list["update_time"] + "\n" + \
                        "============="

            await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
            return


