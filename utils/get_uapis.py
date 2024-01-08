import requests
from requests import HTTPError, Timeout, RequestException

uapi = "uapis.cn"
axtn = "api.axtn.net"


def get_ip_info(ip):
    url = "https://" + uapi + "/api/ipinfo?ip={}".format(ip)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


def get_ping_info(ip, node):
    url = None
    if node == "cn":
        url = "https://" + uapi + "/api/ping?host={}".format(ip)

    if node == "hk":
        url = "https://" + axtn + "/api/ping?host={}".format(ip)

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


def get_whois_info(domain):
    url = "https://" + uapi + "/api/whois?domain={}".format(domain)
    response = requests.get(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


def get_icp_info(domain):
    url = "https://" + uapi + "/api/icp?domain={}".format(domain)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


def get_hot_list(hot_type):
    url = "https://" + uapi + "/api/hotlist?type={}".format(hot_type)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


def get_answer_book():
    url = "https://" + uapi + "/api/answerbook"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("content")
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


def translate_domain_status(status_list):
    status_translations = {
        "clientDeleteProhibited": "客户端删除禁止",
        "clientTransferProhibited": "客户端转移禁止",
        "clientUpdateProhibited": "客户端更新禁止",
        "serverDeleteProhibited": "服务器删除禁止",
        "serverTransferProhibited": "服务器转移禁止",
        "serverUpdateProhibited": "服务器更新禁止"
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
