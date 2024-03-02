import requests
import json

uapiurl = "https://uapis.cn/api/steamuserinfo?input="
async def get_steamid_info(steamid):
    split_str = steamid.split(" ")
    if len(split_str) < 2:
        return "\n未提供Steam ID或昵称，请输入正确的命令格式：/steam [Steam ID/昵称]"
    steamid = split_str[1]  # 获取分割后的第二个子字符串
    apiurl = uapiurl + str(steamid)
    response = requests.get(apiurl)
    if response.status_code == 200:
        data = json.loads(response.text)
        if data.get("code") == 200:
            communitystate = data.get("communitystate") if data.get("communitystate") !='N/A' else "未知"
            steamID64 = data.get("steamID64") if data.get("steamID64") !='N/A' else "未知"
            steamUsername = data.get("username") if data.get("username") !='N/A' else "未知"
            realname = data.get("realname") if data.get("realname") !='N/A' else "未知"
            accountcreationdate = data.get("accountcreationdate") if data.get("accountcreationdate") !='N/A' else "未知"
            lastlogoff = data.get("lastlogoff") if data.get("lastlogoff") != '1970-01-01 08:00:00' or 'N/A' else "未知"
            location = data.get("location") if data.get("location") !='N/A' else "未知"
        elif data.get("code") == 432:
            return f'''\n未查询到该玩家信息'''
        elif data.get("code") == 443:
            return f'''\n请输入Steam ID，当前用户名/用户ID {steamid} 输入有误'''
    else:
        return f'''
查询失败，请联系管理员处理
状态码：{response.status_code}'''
    return f'''
====Steam账户信息====
社区资料状态：{communitystate}
用户名：{steamUsername}
真实姓名：{realname}
Steam ID：{steamID64}
账户创建日期：{accountcreationdate}
最后下线日期：{lastlogoff}
地理位置：{location}'''