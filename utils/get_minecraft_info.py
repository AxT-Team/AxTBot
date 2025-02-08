import aiohttp
import asyncio

async def get_minecraft_uuid(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('id')
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            return None

async def get_player_history(uuid):
    url = f"https://uapis.cn/api/mchistoryid?uuid={uuid}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url) as response:
                response.raise_for_status()
                data = await response.json()
                if data.get('code') == 200:
                    history = data.get('history', [])
                    # 格式化历史记录
                    formatted_history = "\n".join([
                        f"{entry['name']} - {entry['changedToAt'] if entry['changedToAt'] else '未变更'}"
                        for entry in history
                    ])
                    return formatted_history
                else:
                    print(f"无法获取历史信息，返回代码: {data.get('code')}")
                    return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            return None


async def check_server():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post('https://sessionserver.mojang.com/') as response:
                code = response.status
                if code == 403:
                    status1 = '正常'
                else:
                    status1 = f'异常，返回码{code}'
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            status1 = f'请求出错：{e}'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://api.mojang.com/') as response:
                code = response.status
                statusall = await response.json()
                statusall = statusall.get('Status')
                if code == 200 and statusall == 'OK':
                    status2 = '正常'
                else:
                    status2 = f'异常，返回码{code}，在线状态{statusall}'
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"请求错误: {e}")
            status2 = f'请求出错：{e}'
    result = f'''===MC验证服务器在线状态===
| 会话验证：{status1}
| API服务：{status2}'''
    return result