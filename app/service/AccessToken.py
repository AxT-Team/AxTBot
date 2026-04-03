"""
Service for Access Token Management in AxTBot

Author: Shanshui2023
Organization: AxT-Team
"""
from app.classes import AccessToken
import asyncio

accesstoken = AccessToken(access_token="initial_token", expires_in=3600) # 初始访问令牌
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
            accesstoken = AccessToken(access_token="new_token", expires_in=3600)
        await asyncio.sleep(accesstoken.expires_in) # 等待令牌过期时间