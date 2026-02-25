from src.Utils.PluginBase import command
from src.Utils.EventClass import MessageEventPayload

from uapis_extension import format_hot_search, get_from_api

__metadata__ = {
    "name": "[官方插件]获取今日热榜",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "获取多平台热榜信息",
    "official": True,
}

@command(["hotlist", "/hotlist"])
async def hotlist_handler(event: MessageEventPayload):
    content =   "=======每日热榜菜单=======" + "\n" + \
                "/hotlist [热榜类型] - 查询指定热榜信息" + "\n" + \
                "可选的热榜类型有:" + "\n" + \
                "- acfun | AcFun热搜榜" + "\n" + \
                "- weibo | 微博热搜榜" + "\n" + \
                "- bilibili | 哔哩哔哩全站日榜" + "\n" + \
                "- zhihu | 知乎热搜榜" + "\n" + \
                "- douyin | 抖音热搜榜" + "\n" + \
                "==========================" + "\n" + \
                "使用示例: /hotlist weibo" + "\n" + \
                "注:如果指令发送后无返回且无获取错误信息，视为热榜内含有违规信息，被QQ消息审核拦截" + "\n" + \
                "=========================="
    if event.content.startswith(("/hotlist ","hotlist ")) and event.content.split(" ")[1]:
        hot_list = None
        hot_type = None
        msg = event.content
        async def get_hot_list(hot_type: str) -> dict:
            returns = await get_from_api(f"/api/v1/misc/hotboard?type={hot_type}")
            return returns
        if msg.split(" ")[1] == "bilibili":
            hot_list = await get_hot_list("bilibili")
            hot_type = "B站-日榜"
        elif msg.split(" ")[1] == "acfun":
            hot_list = await get_hot_list("acfun")
            hot_type = "A站-热搜榜"
        elif msg.split(" ")[1] == "weibo":
            hot_list = await get_hot_list("weibo")
            hot_type = "微博-热搜榜"
        elif msg.split(" ")[1] == "zhihu":
            hot_list = await get_hot_list("zhihu")
            hot_type = "知乎-热搜榜"
        elif msg.split(" ")[1] == "douyin":
            hot_list = await get_hot_list("douyin")
            hot_type = "抖音-热搜榜"
        else:
            await event.reply('请指定热榜类型')
            return

        if hot_list is None:
            await event.reply('未查询到该热搜信息')
            return
        else:
            update_time = hot_list.get("update_time", "未知")
            content = "===" + hot_type + "===" + "\n" + \
                    format_hot_search(hot_list) + "\n" + \
                    "=============" + "\n" + \
                    update_time + "\n" + \
                    "============="
        await event.reply(content)
    else:
        await event.reply(content)



