"""
Service for Access Token Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from app.classes import AccessToken
from app.modules import logger
import asyncio, aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

APPID = "APPID"
BOT_SECRET = "SECRET"

accesstoken = AccessToken()
lock = asyncio.Lock()
_shutdown = False  # 添加关闭标志

def shutdown_token_service():
    """停止 token 服务"""
    global _shutdown
    _shutdown = True
    logger.info("Waiting for token service to stop...")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=1))
async def get_access_token():
    """
    获取访问令牌的函数
    """
    global accesstoken, _shutdown
    while not _shutdown:  # 添加关闭检查
        async with lock:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://bots.qq.com/app/getAppAccessToken",
                        json={"appId": str(APPID), "clientSecret": BOT_SECRET},
                        timeout=3) as response:
                        if response.status == 200:
                            data = await response.json()
                            accesstoken = AccessToken(access_token=data["access_token"], expires_in=data["expires_in"])
                            logger.debug(f"Fetched new access token: {accesstoken}")
                        else:
                            data = await response.json()
                            logger.error(f"Error fetching access token: {data}")
                            logger.info("Failed to fetch access token, retrying in 10 seconds...")
                            accesstoken = AccessToken(access_token=None, expires_in=10)
            except Exception as e:
                if "shutdown" in str(e).lower():
                    break
                logger.error(f"Error fetching access token: {e}, retrying in 10 seconds...")
                accesstoken = AccessToken(access_token=None, expires_in=10)
        
        if not _shutdown:  # 只在未关闭时等待
            await asyncio.sleep(accesstoken.expires_in)