import requests
from requests import HTTPError, Timeout, RequestException


async def get_hypixel_info(command, userid):
    url = 'http://localhost:30001/hypixel?' + 'command=' + command + '&userId=' + userid
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as e:
        print(f"请求错误: {e}")
        return None
