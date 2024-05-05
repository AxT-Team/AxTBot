import requests

# ------------------快速设置------------------
sv_api = "https://api.imlazy.ink/mcapi/?type=json" # mcping的API接口，备用接口为 https://api.lazy.ink/mcapi/?type=json

menu = '''使用方法:
/mcping [IP:端口] [类型]
可选择的类型有:java，be
端口不填默认25565 类型不填默认java''' # 如果只是/mcping，输出的帮助菜单为这个

error_no200 = "请求出错，请检查API是否可以访问！" # 当网站返回非200时，提示什么

error_notaprotocol = "请求出错，不是可用的类型！可用类型为java/be" # 当protocol被填且内容不为java/be时提示什么
# ----------------快速设置结束-----------------



# ------------------消息分段------------------
async def parse_mcping_command(command):
    parts = command.split()
    if len(parts) == 1: 
        return "default_address", "default_port", "default_protocol"
    address = parts[1].split(':')[0]
    port = '25565'
    if ':' in parts[1]: 
        port = parts[1].split(':')[1]
    protocol = 'java'
    if len(parts) > 2: 
        protocol = parts[2]
    return address, port, protocol
# -----------------消息分段结束----------------

# ------------------主程序------------------
async def mcping(msg):
    address, port,be = await parse_mcping_command(msg)
    if address == "default_address":
        return menu
    else:
        return await mainhandle(address,port,be)
# -----------------主程序结束----------------

# ------------------请求网站------------------
async def mainhandle(address,port,protocol):
    host = address
    if protocol == "java":
        url = sv_api + f'&host={host}&port={port}'
    elif protocol == "be":
        url = sv_api + f'&host={host}&port={port}&be=true'
    else:
        return error_notaprotocol
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        host1,port1,status1,players_max1,players_online1,version1 = data['host'],data['port'],data['status'],data['players_max'],data['players_online'],data['version']
        return await create_text(host1,port1,status1,players_max1,players_online1,version1)
    else:
        return error_no200
# ------------------请求结束------------------

# ------------------构造消息------------------
async def create_text(域名,端口,状态,最大玩家数,在线玩家数,版本):
    if 状态 == "在线":
        域名 = 域名.replace(".", ",")
        return f'''===MC服务器查询===
[状态] {状态}
[人数] {在线玩家数}/{最大玩家数}
[域名] {域名}
[端口] {端口}
[版本] {版本}
===============
'''
    else:
        return '''服务器状态为离线（或IP地址/端口错误）'''
# ------------------构造完毕------------------
