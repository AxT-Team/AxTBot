"""
Service for Access Token Management in AxTBot

Author: Shanshui2023
Organization: AxT-Team
"""
from app.classes import AccessToken
import asyncio, aiohttp

APPID = "appid"
APPSECRET = "clientSecret"


accesstoken = AccessToken() # 定义初始访问令牌
lock = asyncio.Lock()

async def get_access_token() -> AccessToken:
    """
    获取访问令牌的函数
    
    Returns:
        AccessToken: 包含访问令牌和过期时间的AccessToken对象

    详细信息：https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/api-use.html
    """
    global accesstoken
    while True:
        async with lock: # 异步锁
            async with aiohttp.ClientSession() as session:
                # 模拟获取新令牌的API请求
                async with session.post(
                    "https://bots.qq.com/app/getAppAccessToken",
                    json={"appId": str(APPID), "clientSecret": APPSECRET},
                    timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        accesstoken = AccessToken(access_token=data["access_token"], expires_in=data["expires_in"])
                    else:
                        print("Failed to fetch access token, retrying in 10 seconds...")
                        accesstoken = AccessToken(access_token=None, expires_in=10)
        await asyncio.sleep(accesstoken.expires_in) # 等待令牌过期时间