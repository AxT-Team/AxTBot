"""
Service for Access Token Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import asyncio, aiohttp, time
from tenacity import retry, stop_after_attempt, wait_exponential

from app.classes import AccessToken
from app.modules import logger, config, get_db, FrameConfig

APPID = config.appid
BOT_SECRET = config.botsecret

accesstoken = AccessToken()
lock = asyncio.Lock()
_shutdown = False  # 添加关闭标志

def shutdown_token_service():
    """停止 token 服务"""
    global _shutdown
    _shutdown = True

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=1))
async def get_access_token():
    """
    获取访问令牌的函数
    """
    global accesstoken, _shutdown
    while not _shutdown:  # 添加关闭检查
        db = get_db()
        try:
            db_access_token = db.get_frame_config_by_key("access_token")
            db_access_token.create_time
        except Exception as e:
            logger.error(f"数据库 >>> 配置项不存在，错误信息：{e}")
            logger.warning(f"数据库 >>> 重新加载数据...")
            db.add_frame_config(FrameConfig(key="access_token", value="None", create_time=str(int(time.time())), update_time=str(int(time.time()))))
            db_access_token = db.get_frame_config_by_key("access_token")
        async with lock:
            try:
                if int(db_access_token.update_time) - 40 > int(time.time()) and db_access_token.value:
                    accesstoken = AccessToken(access_token=db_access_token.value, expires_in=int(db_access_token.update_time) - int(time.time()))
                    logger.debug(f"Get cached AccessToken: {accesstoken}")
                else:
                    logger.debug(f"Cached accessToken expired! Retring")
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "https://bots.qq.com/app/getAppAccessToken",
                            json={"appId": str(APPID), "clientSecret": BOT_SECRET},
                            timeout=3) as response:
                            if response.status == 200:
                                data = await response.json()
                                accesstoken = AccessToken(access_token=data["access_token"], expires_in=data["expires_in"])
                                db.update_frame_config("access_token", data["access_token"], int(time.time()) + int(data["expires_in"]))
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