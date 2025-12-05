import time

from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent

from uapis_extension import post_for_api, get_from_api


__metadata__ = {
    "name": "[社区插件]B站视频查询",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "从接口请求解析B站视频信息",
    "official": False,
}

@command(["bili", "/bili"])
async def bili_handler(event: GroupMessageEvent):
    msg = event.content.split(" ")[1] if len(event.content.split(" ")) > 1 else ""
    if msg.lower().startswith("bv"):
        url = "bvid"
    elif msg.lower().startswith("av") or msg.isdigit():
        msg = msg.replace("av", "")
        url = "aid"
    try:
        response = await get_from_api(f"/api/v1/social/bilibili/videoinfo?{url}=" + str(msg))
    except Exception as e:
        await event.reply("视频信息获取失败，请确保您输入了正确的AV/BV号！")
        raise
    bvid = response["bvid"]
    avid = response["aid"]
    part = response["videos"]
    part_name = response["tname"]
    if response["copyright"] == 1:
        copyright = "原创"
    elif response["copyright"] == 2:
        copyright = "转载"
    else:
        copyright = "未知"
    
    pic = response["pic"]
    title = response["title"]
    pubtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response["pubdate"]))
    createtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(response["ctime"]))
    desc = response["desc"]
    duration = str(int(response["duration"] // 60)) + "分" + str(int(response["duration"] % 60)) + "秒"
    owner_name = response["owner"]["name"]
    owner_mid = response["owner"]["mid"]
    stat_view = response["stat"]["view"]
    stat_danmaku = response["stat"]["danmaku"]
    stat_reply = response["stat"]["reply"]
    stat_favorite = response["stat"]["favorite"]
    stat_coin = response["stat"]["coin"]
    stat_share = response["stat"]["share"]
    stat_like = response["stat"]["like"]

    returns = f"""视频标题：{response['title']}
视频AV号：av{avid}  BV号：{bvid}
分P数：{part}  分区：{part_name}
{copyright} | 时长：{duration}"""
    await event.reply(returns)