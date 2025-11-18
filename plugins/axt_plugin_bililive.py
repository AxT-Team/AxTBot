from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent

from uapis_extension import post_for_api, get_from_api


__metadata__ = {
    "name": "[社区插件]B站直播查询",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "从接口请求得到B站直播间开播状态等信息",
    "official": False,
}

@command(["bili", "/bili"])
async def bili_handler(event: GroupMessageEvent):
    msg = event.content.split(" ")[1] if len(event.content.split(" ")) > 1 else ""
    try:
        response = await get_from_api("/api/v1/social/bilibili/liveroom?mid=" + str(msg))
    except Exception as e:
        try:
            response = await get_from_api("/api/v1/social/bilibili/liveroom?room_id=" + str(msg))
        except Exception as e:
            await event.reply("房间信息获取失败，请确保您输入了正确的房间号/主播UID")
        raise
    uid = response["uid"]
    roomid = response["roomid"] if response["short_id"] == 0 else response["short_id"]
    attention = response["attention"]
    online = response["online"]
    if response["live_status"] == 1:
        online = f"开播中"
    elif response["live_status"] == 0:
        online = f"未开播"
    elif response["live_status"] == 2:
        online = f"轮播中"
    else:
        online = f"未知状态"
    area = response["parent_area_name"] + " > " + response["area_name"]
    title = response["title"]
    pic = response["background"]
    desc = response["description"]
    live_time = response["live_time"] if response["live_status"] == 1 else "N/A"
    tags = ", ".join(response["tags"])
    returns = f"""主播UID: {uid}
房间号: {roomid}
开播状态: {online}
直播标题: {title}
直播分区: {area}
直播时间: {live_time}
粉丝数: {attention}
当前人气: {online}
标签: {tags}
直播简介: {desc}
直播封面: {pic}"""
    await event.reply(returns)
