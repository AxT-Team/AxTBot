from src.Utils.PluginBase import command
from src.Utils.EventClass import MessageEventPayload

from uapis_extension import get_from_api

__metaresult__ = {
    "name": "[官方插件]Steam 查询",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "查询公开的Steam账户信息",
    "official": True,
}


@command(["steam", "/steam"])
async def ping_handler(event: MessageEventPayload):
    if event.content in ['/steam', '/steam ', 'steam', 'steam ']:
        content = "=======Steam账户查询=======" + "\n" + \
                   "/steam [SteamID64/用户自定义URL名称/完整的个人资料链接/SteamID3] - 查询指定Steam账户信息" + "\n" + \
                   "=======================" + "\n" + \
                   "使用示例: /steam 114514" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "如果指令发送后提示被去重，则可能是QQ开放平台侧的问题，请等1分钟左右再重试一次" + "\n" + \
                   "注意！由于Steam API限制，此处暂不支持使用昵称查询" + "\n" + \
                   "======================="
        await event.reply(content=content)
    else:
        msg = event.content
        if msg.startswith(("/steam ","steam ")):
            result = await get_steamid_info(msg)
            if result:
                await event.reply(content=result)
                return


async def get_steamid_info(steamid):
    split_str = steamid.split(" ")
    steamid = split_str[1]  # 获取分割后的第二个子字符串
    result = await get_from_api(f"/api/v1/game/steam/summary?steamid={steamid}")
    if result:
        communitystate = result.get("communityvisibilitystate") if result.get("communityvisibilitystate") != 'N/A' else "未知"
        if communitystate == 3:
            communitystate = "公开"
        elif communitystate == 2:
            communitystate = "好友可见"
        elif communitystate == 1:
            communitystate = "私密"
        personalstate = result.get("personastate") if result.get("personastate") != 'N/A' else "未知"
        if personalstate == 0:
            personalstate = "离线"
        elif personalstate == 1:
            personalstate = "在线"
        elif personalstate == 2:
            personalstate = "忙碌"
        elif personalstate == 3:
            personalstate = "离开"
        elif personalstate == 4:
            personalstate = "打盹"
        elif personalstate == 5:
            personalstate = "想交易"
        elif personalstate == 6:
            personalstate = "想玩游戏"

        steamID64 = result.get("steamid") if result.get("steamid") != 'N/A' else "未知"
        steamUsername = result.get("personaname") if result.get("personaname") != 'N/A' else "未知"
        realname = result.get("realname") if result.get("realname") != 'N/A' else "未知"
        accountcreationdate = result.get("timecreated_str") if result.get("timecreated_str") != 'N/A' else "未知"
        # lastlogoff = result.get("lastlogoff") if result.get("lastlogoff") != '1970-01-01 08:00:00' and result.get("lastlogoff") != 'N/A' else "未知"
        location = result.get("loccountrycode") if result.get("loccountrycode") != 'N/A' else "未知"
        return f"""====Steam账户信息====
| 社区资料状态：{communitystate}
| 用户状态：{personalstate}
| 用户名：{steamUsername}
| 真实姓名：{realname}
| Steam ID：{steamID64}
| 账户创建日期：{accountcreationdate}
| 地理位置：{location}
====================="""

    else:
        return f"""查询失败，可能是输入有误或 Steam 账户不存在。
若确认当前账户存在，请稍后重试或联系管理员。
请注意：由于 Steam API 限制，此处暂不支持使用昵称查询。请通过SteamID查询，详见/steam菜单"""
