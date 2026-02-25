import aiohttp, asyncio, os
from aiohttp import ClientError

from src.Utils.Logger import logger

def format_hot_search(data):
    items = data.get("list", [])[:10]
    formatted = []
    for item in items:
        index = item.get("index", "")
        title = item.get("title", "")
        hot = item.get("hot_value", None)
        if hot:
            formatted.append(f"{index} - {title} | {hot}")
        else:
            formatted.append(f"{index} - {title}")
    return "\n".join(formatted)

# 数字格式化（万单位）
def format_count(num):
    if num >= 10000:
        return f"{num/10000:.1f}万"
    return str(num)

async def get_hypixel_info(command, userid):
    url = "http://localhost:30001/hypixel?" + "command=" + command + "&userId=" + userid
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                # 先获取响应文本，用于错误日志
                response_text = await response.text()
                
                # 检查 HTTP 状态码
                if response.status != 200:
                    logger.error(f"❌ Hypixel API 返回错误状态码")
                    logger.error(f"  ├─ 插件: axt_plugin_minecraft")
                    logger.error(f"  ├─ 函数: get_hypixel_info")
                    logger.error(f"  ├─ URL: {url}")
                    logger.error(f"  ├─ 状态码: {response.status}")
                    logger.error(f"  ├─ 状态描述: {response.reason}")
                    logger.error(f"  ├─ 命令参数: {command}")
                    logger.error(f"  └─ 响应内容: {response_text[:300] if response_text else '(空响应)'}...")
                    return f"Hypixel API 请求失败！状态码: {response.status} ({response.reason})"
                
                # 尝试解析 JSON
                try:
                    import json
                    return json.loads(response_text)
                except json.JSONDecodeError as json_error:
                    logger.error(f"❌ Hypixel API JSON解析失败")
                    logger.error(f"  ├─ 插件: axt_plugin_minecraft")
                    logger.error(f"  ├─ 函数: get_hypixel_info")
                    logger.error(f"  ├─ URL: {url}")
                    logger.error(f"  ├─ 响应状态码: {response.status}")
                    logger.error(f"  ├─ 命令参数: {command}")
                    logger.error(f"  ├─ 响应内容: {response_text[:300]}...")
                    logger.error(f"  └─ 解析错误: {str(json_error)}")
                    return f"请求出错！服务器返回了无效的JSON格式数据。"
                    
        except asyncio.TimeoutError as e:
            logger.error(f"❌ Hypixel API 请求超时")
            logger.error(f"  ├─ 插件: axt_plugin_minecraft")
            logger.error(f"  ├─ 函数: get_hypixel_info")
            logger.error(f"  ├─ URL: {url}")
            logger.error(f"  ├─ 命令参数: {command}")
            logger.error(f"  └─ 错误信息: 请求超时")
            return f"请求超时！Hypixel API 服务器响应时间过长。"
            
        except ClientError as e:
            logger.error(f"❌ Hypixel API 网络请求失败")
            logger.error(f"  ├─ 插件: axt_plugin_minecraft")
            logger.error(f"  ├─ 函数: get_hypixel_info")
            logger.error(f"  ├─ URL: {url}")
            logger.error(f"  ├─ 命令参数: {command}")
            logger.error(f"  ├─ 错误类型: {type(e).__name__}")
            logger.error(f"  └─ 错误信息: {str(e)}")
            return f"网络请求失败！错误信息：{str(e)}"
            
        except Exception as e:
            logger.error(f"❌ Hypixel API 未知错误")
            logger.error(f"  ├─ 插件: axt_plugin_minecraft")
            logger.error(f"  ├─ 函数: get_hypixel_info")
            logger.error(f"  ├─ URL: {url}")
            logger.error(f"  ├─ 命令参数: {command}")
            logger.error(f"  ├─ 错误类型: {type(e).__name__}")
            logger.error(f"  └─ 错误信息: {str(e)}")
            return f"未知错误！错误信息：{str(e)}"

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
        "serverupdateprohibited": "服务器更新禁止",
    }

    translated_status = []
    for status in status_list:
        status_without_link = status.split(" ")[0]
        status_cn = status_translations.get(status_without_link, status_without_link)
        translated_status.append(status_cn)

    return translated_status

async def fetch_screenshot_from_service(html: str) -> bytes:
    timeout = aiohttp.ClientTimeout(total=20)  # 20秒
    async with aiohttp.ClientSession(timeout=timeout) as session:
        payload = {
            "html": html,
            "selector": ".card",
            "viewport_width": 850,
            "viewport_height": 1000,
            "timeout": 15000  # 传递给服务的页面超时（毫秒）
        }
        try:
            async with session.post("http://127.0.0.1:8021/screenshot", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return bytes.fromhex(data["image"])
                else:
                    text = await resp.text()
                    raise Exception(f"Screenshot service error {resp.status}: {text}")
        except asyncio.TimeoutError:
            raise Exception("Screenshot service timeout")

async def delayed_remove(path, delay=5):
    """延迟删除临时文件"""
    await asyncio.sleep(delay)
    try:
        os.unlink(path)
    except:
        pass

async def _upload(file_path):
    oss_access_key = "access_key"
    oss_secret_key = "secret_key"
    oss_bucket = "bucket_name"
    oss_public_url = "public_url"

    oss_key = os.path.basename(file_path)
    from src.Utils.ImageUploader import upload_file
    url = upload_file(oss_access_key, oss_secret_key, oss_bucket, oss_key, file_path, oss_public_url)
    return url

