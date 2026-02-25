import aiohttp, asyncio, re
from aiohttp import ClientError

from src.Utils.Logger import logger
from uapis_extension.Config import apiconfig

from uapis_extension.functions import format_hot_search, translate_domain_status, get_hypixel_info, format_count, fetch_screenshot_from_service, delayed_remove, _upload


"""
根据Uapis、RFC 7231使用BaseResponseModel及其子类来验证网络响应
"""


async def post_for_api(url: str, body = None, headers = None) -> dict:
    """
    使用aiohttp获取URL并验证响应

    Args:
        url: 要请求的URL
        body: 请求体数据
        headers: 请求头

    Returns:
        验证后的响应模型实例

    Raises:
        aiohttp.ClientError: 如果请求失败或返回错误
        Exception: 如果请求过程中发生未知错误
    """
    if url.startswith("/"):
        url = url[1:]
    async with aiohttp.ClientSession() as session:
        try:
            if body:
                async with session.post(apiconfig.url + url, headers=headers, data=body) as response:
                    # 检查 Content-Type 来判断响应类型
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    if response.status == 200:
                        # 如果是 JSON 响应
                        if 'application/json' in content_type:
                            try:
                                import json
                                response_text = await response.text()
                                return json.loads(response_text)
                            except json.JSONDecodeError as e:
                                logger.error(f"❌ API POST JSON解析失败")
                                logger.error(f"  ├─ URL: {apiconfig.url + url}")
                                logger.error(f"  ├─ 响应状态码: {response.status}")
                                logger.error(f"  ├─ Content-Type: {content_type}")
                                logger.error(f"  └─ 错误: {str(e)}")
                                return None
                        # 如果是二进制数据（图片等）
                        elif 'image/' in content_type or 'application/octet-stream' in content_type:
                            logger.error(f"❌ API返回了二进制数据而不是JSON")
                            logger.error(f"  ├─ URL: {apiconfig.url + url}")
                            logger.error(f"  ├─ Content-Type: {content_type}")
                            logger.error(f"  └─ 提示: API应该返回包含图片URL的JSON，而不是直接返回图片")
                            return None
                        else:
                            # 尝试作为文本处理
                            try:
                                response_text = await response.text()
                                logger.error(f"❌ API POST返回了非JSON内容")
                                logger.error(f"  ├─ URL: {apiconfig.url + url}")
                                logger.error(f"  ├─ Content-Type: {content_type}")
                                logger.error(f"  └─ 响应内容: {response_text[:300]}...")
                                return None
                            except UnicodeDecodeError:
                                logger.error(f"❌ API POST返回了无法解码的二进制数据")
                                logger.error(f"  ├─ URL: {apiconfig.url + url}")
                                logger.error(f"  └─ Content-Type: {content_type}")
                                return None
                    else:
                        # 错误响应
                        try:
                            response_text = await response.text()
                        except UnicodeDecodeError:
                            response_text = "[二进制数据，无法显示]"
                        
                        logger.error(f"❌ API POST返回错误")
                        logger.error(f"  ├─ URL: {apiconfig.url + url}")
                        logger.error(f"  ├─ 状态码: {response.status}")
                        logger.error(f"  ├─ Content-Type: {content_type}")
                        logger.error(f"  └─ 响应内容: {response_text[:300]}...")
                        return None
            else:
                async with session.post(apiconfig.url + url, headers=headers) as response:
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    if response.status == 200:
                        if 'application/json' in content_type:
                            try:
                                import json
                                response_text = await response.text()
                                return json.loads(response_text)
                            except json.JSONDecodeError:
                                logger.error(f"❌ API POST JSON解析失败")
                                logger.error(f"  ├─ URL: {apiconfig.url + url}")
                                logger.error(f"  └─ Content-Type: {content_type}")
                                return None
                        else:
                            logger.error(f"❌ API POST返回了非JSON内容")
                            logger.error(f"  ├─ URL: {apiconfig.url + url}")
                            logger.error(f"  └─ Content-Type: {content_type}")
                            return None
                    else:
                        try:
                            response_text = await response.text()
                        except UnicodeDecodeError:
                            response_text = "[二进制数据，无法显示]"
                        
                        logger.error(f"❌ API POST返回错误")
                        logger.error(f"  ├─ URL: {apiconfig.url + url}")
                        logger.error(f"  ├─ 状态码: {response.status}")
                        logger.error(f"  └─ 响应内容: {response_text[:300]}...")
                        return None

        except aiohttp.ClientError as e:
            logger.error(f"❌ HTTP请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 请求过程中发生未知错误: {e}")
            raise


async def get_from_api(url: str) -> dict:
    """
    使用aiohttp获取URL并验证响应

    Args:
        url: 要请求的URL

    Returns:
        验证后的响应模型实例

    Raises:
        aiohttp.ClientError: 如果请求失败或返回错误
        Exception: 如果请求过程中发生未知错误
    """
    if url.startswith("/"):
        url = url[1:]
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(apiconfig.url + url) as response:
                data = await response.json()
                if response.status == 200:
                    return data
                else:
                    logger.error(
                        f"""❌ 请求失败，状态码: {response.status}
API GET返回错误 (HTTP {response.status}): Code: {data.get('code')}, Message: {data.get('message')}"""
                    )
        except aiohttp.ClientError as e:
            logger.error(f"❌ HTTP请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 请求过程中发生未知错误: {e}")
            raise


async def get_minecraft_uuid(username: str) -> str:
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("id")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return None

async def get_player_history(uuid):
    url = f"api/v1/game/minecraft/historyid?uuid={uuid}"
    result = await get_from_api(url)
    history = result.get('history', [])
    formatted_history = "\n".join([
        f"{entry['name']} - {entry['changedToAt'] if entry['changedToAt'] else '未变更'}"
        for entry in history
    ])
    return formatted_history


async def check_minecraft_online():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("https://sessionserver.mojang.com/") as response:
                code = response.status
                if code == 403:
                    status1 = "正常"
                else:
                    status1 = f"异常，返回码{code}"
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            status1 = f"请求出错：{e}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://api.mojang.com/") as response:
                code = response.status
                statusall = await response.json()
                statusall = statusall.get("Status")
                if code == 200 and statusall == "OK":
                    status2 = "正常"
                else:
                    status2 = f"异常，返回码{code}，在线状态{statusall}"
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            status2 = f"请求出错：{e}"
    result = f"""===MC验证服务器在线状态===
| 会话验证：{status1}
| API服务：{status2}"""
    return result

async def get_minecraft_info(address: int) -> str:
    result = await get_from_api(f"api/v1/game/minecraft/serverstatus?server={address}")
    result = (
        await create_text(result) if result else """很抱歉，您所查询的服务器不在线！"""
    )
    return result


async def create_text(data):
    status = data["online"]
    if status == False:
        return """很抱歉，您所查询的服务器不在线！"""
    description = data.get("motd_clean", "空")
    ip = data.get("ip", "未知")
    port = data.get("port", "未知")
    players_online = data.get("players", "0")
    players_max = data.get("max_players", "未知")
    version = data.get("version", "未知")
    if not isinstance(description, str):
        description = str(description)
    # 处理描述中的特殊字符和颜色代码（例如 §a, §c等）
    description = re.sub(r"§[0-9a-fk-or]", "", description)

    # 格式化返回消息
    return f"""=====MC服务器查询=====
| 状态: 在线
| IP: {ip} 
| 端口: {port}
| 人数: {players_online}/{players_max}
| 服务器描述: 
{description}
| 版本: {version}
=====================
请注意：请确保您的服务器描述、版本或其他信息合法。
任何由于查询信息中含有违规内容而导致的封禁行为，将受到管控和消息二审"""
