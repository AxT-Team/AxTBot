import aiohttp
import asyncio
from Core.Logger import logger
import re

async def get_minecraft_uuid(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('id')
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
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
                    logger.error(f"无法获取历史信息，返回代码: {data.get('code')}")
                    return None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
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
            logger.error(f"请求错误: {e}")
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
            logger.error(f"请求错误: {e}")
            status2 = f'请求出错：{e}'
    result = f'''===MC验证服务器在线状态===
| 会话验证：{status1}
| API服务：{status2}'''
    return result



# ------------------快速设置------------------
sv_api = "https://api.uapis.cn/minecraft/status?address="
error_no200 = "请求出错，请检查服务器是否在线！"  # 请求失败时的提示
error_notaprotocol = "请求出错，不是可用的类型！可用类型为java/be"  # 当protocol字段不是java或be时的提示
# ------------------快速设置结束-----------------

# ------------------主程序------------------
async def get_mcserver_info(msg):
    # 消息分段处理
    address = msg.split()[1].split(':')[0]
    port = '25565'
    if ':' in msg.split()[1]:
        port = msg.split()[1].split(':')[1]
    protocol = 'java'
    if len(msg.split()) > 2:
        protocol = msg.split()[2]
    # 处理类型
    if protocol == "java":
        url = sv_api + str(address) + ":" + str(port)
    elif protocol == "be":
        url = sv_api + str(address) + ":" + str(port) + "&be=true"
    else:
        return error_notaprotocol
    # 使用aiohttp进行异步请求
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as response: # type: ignore
                if response.status == 200:
                    data = await response.json()
                    return await create_text(data) # 构造消息
                else:
                    return error_no200
    except asyncio.TimeoutError as e:
        logger.error(f"请求超时：{e}")
        return "请求超时，请稍后重试"
    except aiohttp.ClientError as e:
        logger.error(f"请求错误: {e}")
        return f"请求错误: {e}"
# ------------------主程序结束------------------

# ------------------构造消息------------------
async def create_text(data):
    description = data['response'].get('description', '空')
    players_online = data['response']['players'].get('online', '未知')
    players_max = data['response']['players'].get('max', '未知')
    version = data['response']['version'].get('name', '未知')
    if not isinstance(description, str):
        description = str(description)
    # 处理描述中的特殊字符和颜色代码（例如 §a, §c等）
    description = re.sub(r'§[0-9a-fk-or]', '', description)

    # 格式化返回消息
    return f'''
=====MC服务器查询=====
| 状态: 在线
| 人数: {players_online}/{players_max}
| 服务器描述: 
{description}
| 版本: {version}
====================='''
# ------------------构造完毕------------------
