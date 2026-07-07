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

_hypixel_checker = None

async def get_hypixel_info(command, userid):
    global _hypixel_checker
    try:
        if _hypixel_checker is None:
            from hypixelcheck import HypixelCheck
            _hypixel_checker = HypixelCheck()
        result = await _hypixel_checker.execute_async(command, userid)
        if result is None:
            return "未知的命令。"
        return result
    except Exception as e:
        logger.error(f"❌ Hypixel 查询失败")
        logger.error(f"  ├─ 插件: axt_plugin_minecraft")
        logger.error(f"  ├─ 函数: get_hypixel_info")
        logger.error(f"  ├─ 命令参数: {command}")
        logger.error(f"  ├─ 错误类型: {type(e).__name__}")
        logger.error(f"  └─ 错误信息: {str(e)}")
        return f"查询出错！错误信息：{str(e)}"

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

