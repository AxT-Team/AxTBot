import json
import requests
from requests import HTTPError, Timeout, RequestException


uapi = "api.uapis.cn"
uapi_old = "uapis.cn"
axtn = "api.axtn.net"


async def get_ip_info(ip):
    url = "https://" + uapi + "/ipinfo?ip={}".format(ip)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


async def get_ping_info(ip, node):
    url = None
    if node == "cn":
        url = "https://" + uapi + "/ping?host={}".format(ip)

    if node == "hk":
        url = "https://" + axtn + "/ping?host={}".format(ip)

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


async def get_whois_info(domain):
    url = "https://" + uapi + "/whois?domain={}".format(domain)
    response = requests.get(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


async def get_icp_info(domain):
    url = "https://" + uapi_old + "/api/icp?domain={}".format(domain)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


async def get_hot_list(hot_type):
    url = "https://" + uapi_old + "/api/hotlist?type={}".format(hot_type)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


async def get_answer_book():
    url = "https://" + uapi_old + "/api/answerbook"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("content")
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return '获取失败，请联系管理员寻求帮助'

async def get_touch_url(qqid):
    url = "https://" + uapi_old + "/api/mt?qq=" + str(qqid)
    return url

async def get_steamid_info(steamid):
    
    split_str = steamid.split(" ")
    steamid = split_str[1]  # 获取分割后的第二个子字符串
    response = requests.get("https://" + uapi_old + "/api/steamuserinfo?input=" + str(steamid))
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
| 社区资料状态：{communitystate}
| 用户名：{steamUsername}
| 真实姓名：{realname}
| Steam ID：{steamID64}
| 账户创建日期：{accountcreationdate}
| 最后下线日期：{lastlogoff}
| 地理位置：{location}
=====================''' 



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

    # 翻译状态列表
    translated_status = []
    for status in status_list:
        # 移除HTTPS链接
        status_without_link = status.split(" ")[0]
        # 翻译状态
        status_cn = status_translations.get(status_without_link, status_without_link)
        translated_status.append(status_cn)

    return translated_status


def format_hot_search(data):
    """
    格式化热搜榜信息，根据是否包含热度（hot）字段来调整格式。
    """
    items = data.get("data", [])[:10]  # 获取前十个热搜项目

    # 用于存储格式化的热搜信息
    formatted = []

    for item in items:
        index = item.get("index", "")
        title = item.get("title", "")
        hot = item.get("hot", None)

        # 根据是否有热度信息调整输出格式
        if hot:
            formatted.append(f"{index} - {title} | {hot}")
        else:
            formatted.append(f"{index} - {title}")

    return "\n".join(formatted)


def format_history_today(data):
    """
    格式化历史上的今天数据
    """
    items = data.get("data", [])

    formatted = []

    for item in items:
        index = item.get("index", "")
        title = item.get("title", "")
        formatted.append(f"{index}: {title}")

    return "\n".join(formatted)
