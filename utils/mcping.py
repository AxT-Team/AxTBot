import aiohttp
import re

# ------------------快速设置------------------
sv_api = "https://api.uapis.cn/minecraft/status?address="
error_no200 = "请求出错，请检查服务器是否在线！"  # 请求失败时的提示
error_notaprotocol = "请求出错，不是可用的类型！可用类型为java/be"  # 当protocol字段不是java或be时的提示
# ------------------快速设置结束-----------------

# ------------------消息分段------------------
async def parse_mcping_command(command):
    parts = command.split()
    address = parts[1].split(':')[0]
    port = '25565'
    if ':' in parts[1]:
        port = parts[1].split(':')[1]
    protocol = 'java'
    if len(parts) > 2:
        protocol = parts[2]
    return address, port, protocol
# ------------------消息分段结束------------------

# ------------------主程序------------------
async def mcping(msg):
    address, port, protocol = await parse_mcping_command(msg)
    return await mainhandle(address, port, protocol)
# ------------------主程序结束------------------

# ------------------请求网站------------------
async def mainhandle(address, port, protocol):
    host = address
    if protocol == "java":
        url = sv_api + str(host) + ":" + str(port)
    elif protocol == "be":
        url = sv_api + str(host) + ":" + str(port) + "&be=true"
    else:
        return error_notaprotocol

    # 使用aiohttp进行异步请求
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return await create_text(data)
                else:
                    return error_no200
    except aiohttp.ClientError as e:
        return f"请求错误: {e}"
# ------------------请求结束------------------

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
