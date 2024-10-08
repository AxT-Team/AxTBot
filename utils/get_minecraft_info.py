import requests
from requests import HTTPError, Timeout, RequestException


async def get_minecraft_uuid(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('id')
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None


async def get_player_history(uuid):
    # url = f"https://api.axtn.net/api/mchistoryid?uuid={uuid}"
    url = f"https://api.uapis.cn/minecraft/history-username?info={uuid}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('history')
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None
