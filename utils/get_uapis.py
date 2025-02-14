import json
import aiohttp
from aiohttp import ClientError, ClientSSLError, ClientSession
import asyncio


uapi = "api.uapis.cn"
uapi_old = "uapis.cn"
axtn = "api.axtn.net"


async def get_ip_info(ip):
    url = f"https://{uapi}/ipinfo?ip={ip}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            return None


async def get_ping_info(ip, node):
    url = None
    if node == "cn":
        url = f"https://{uapi}/ping?host={ip}"
    elif node == "hk":
        url = f"https://{axtn}/ping?host={ip}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            return None


async def get_whois_info(domain):
    url = f"https://{uapi}/whois?domain={domain}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except ClientSSLError as e:
            print(f"SSL 错误：{e}")
            return {"error": "SSL 证书验证失败，请稍后再试或联系管理员。"}
        except ClientError as e:
            print(f"请求错误：{e}")
            return {"error": "网络请求失败，请稍后再试。"}


async def get_icp_info(domain):
    url = f"https://{uapi_old}/api/icp?domain={domain}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            return None


async def get_hot_list(hot_type):
    url = f"https://{uapi_old}/api/hotlist?type={hot_type}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            return None


async def get_answer_book():
    url = f"https://{uapi_old}/api/answerbook"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return (await response.json()).get("content")
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            return "获取失败，请联系管理员寻求帮助"


async def get_touch_url(qqid):
    url = f"https://{uapi_old}/api/mt?qq={str(qqid)}"
    return url


async def get_steamid_info(steamid):
    split_str = steamid.split(" ")
    steamid = split_str[1]  # 获取分割后的第二个子字符串
    url = f"https://{uapi_old}/api/steamuserinfo?input={steamid}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("code") == 200:
                        communitystate = data.get("communitystate") if data.get("communitystate") != 'N/A' else "未知"
                        steamID64 = data.get("steamID64") if data.get("steamID64") != 'N/A' else "未知"
                        steamUsername = data.get("username") if data.get("username") != 'N/A' else "未知"
                        realname = data.get("realname") if data.get("realname") != 'N/A' else "未知"
                        accountcreationdate = data.get("accountcreationdate") if data.get("accountcreationdate") != 'N/A' else "未知"
                        lastlogoff = data.get("lastlogoff") if data.get("lastlogoff") != '1970-01-01 08:00:00' and data.get("lastlogoff") != 'N/A' else "未知"
                        location = data(".getlocation") if data.get("location") != 'N/A' else "未知"
                        return f"""
====Steam账户信息====
| 社区资料状态：{communitystate}
| 用户名：{steamUsername}
| 真实姓名：{realname}
| Steam ID：{steamID64}
| 账户创建日期：{accountcreationdate}
| 最后下线日期：{lastlogoff}
| 地理位置：{location}
=====================
"""
                    elif data.get("code") == 432:
                        return "\n未查询到该玩家信息"
                    elif data.get("code") == 443:
                        return f"\n请输入Steam ID，当前用户名/用户ID {steamid} 输入有误"
                else:
                    return f"\n查询失败，请联系管理员处理\n状态码：{response.status}"
        except (ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            return "\n查询失败，请联系管理员处理"


def translate_domain_status(status_list):
    status_translations = {
        "clientDeleteProhibited": "客户端删除禁止",
        "clientdeleteprohibited": "客户端删除禁止",
        "clientTransferProhibited": "客户端转移禁止",
        "clienttransferprohibited": "客户端转移禁止",
        "clientUpdateProhibited": "客户端更新禁止",
        "clientupdateprohibited": "客户端更新禁止",
        "serverDeleteProhibited": "服务器删除禁止",
        "serverdeleteprohibited": "服务器删除禁止",
        "serverTransferProhibited": "服务器转移禁止",
        "servertransferprohibited": "服务器转移禁止",
        "serverUpdateProhibited": "服务器更新禁止",
        "serverupdateprohibited": "服务器更新禁止"
    }

    translated_status = []
    for status in status_list:
        status_without_link = status.split(" ")[0]
        status_cn = status_translations.get(status_without_link, status_without_link)
        translated_status.append(status_cn)

    return translated_status


def format_hot_search(data):
    items = data.get("data", [])[:10]
    formatted = []
    for item in items:
        index = item.get("index", "")
        title = item.get("title", "")
        hot = item.get("hot", None)
        if hot:
            formatted.append(f"{index} - {title} | {hot}")
        else:
            formatted.append(f"{index} - {title}")
    return "\n".join(formatted)


def format_history_today(data):
    items = data.get("data", [])
    formatted = []
    for item in items:
        index = item.get("index", "")
        title = item.get("title", "")
        formatted.append(f"{index}: {title}")
    return "\n".join(formatted)