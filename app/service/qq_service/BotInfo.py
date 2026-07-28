"""
Startup Get BotInfo Service for AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import aiohttp

from app.modules import logger
async def get_qqbot_info():
    from app.service.qq_service.AccessToken import accesstoken
    logger.debug("适配器 >>> 正在获取机器人信息")
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"QQBot {accesstoken.access_token}"}
            async with session.get("https://api.bot.qq.com/users/@me", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    username = data["username"]
                    id = data["id"]
                    openid = data["union_openid"]
                    logger.info(f"适配器 >>> ID: {id} | OpenID: {openid} | 机器人 {username} 登录成功！")
                    logger.debug(data)
                else:
                    data = response.text
                    logger.error(f"Error fetching botinfo: {data}")
                    logger.info("Failed to fetch botinfo.")
    except Exception as e:
        logger.error(e)
        raise e