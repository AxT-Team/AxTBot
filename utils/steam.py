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
        communitystate = data.get("communitystate")
        steamID64 = data.get("steamID64")
        steamUsername = data.get("username")
        realname = data.get("realname")
        accountcreationdate = data.get("accountcreationdate")
        lastlogoff = data.get("lastlogoff")
        location = data.get("location")
        return f'''
====Steam账户信息====
社区资料状态：{communitystate}
用户名：{steamUsername}
真实姓名：{realname}
Steam ID：{steamID64}
账户创建日期：{accountcreationdate}
最后下线日期：{lastlogoff}
地理位置：{location}'''
    else:
        return "\n无法访问Uapi，请检查控制台"
