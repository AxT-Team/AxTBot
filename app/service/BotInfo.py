"""
Startup Get BotInfo Service for AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import aiohttp

from app.modules import logger
async def get_qqbot_info():
    from app.service.AccessToken import accesstoken
    logger.debug("框架 >>> 正在获取机器人信息")
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"QQBot {accesstoken}"}
            async with session.get("https://api.bot.qq.com/users/@me", headers=headers) as response:
                data = response.text
                if response.status == 200:
                    logger.debug(f"Fetched bot info: {data}")
                else:
                    logger.error(f"Error fetching botinfo: {data}")
                    logger.info("Failed to fetch botinfo.")
    except Exception as e:
        logger.error(e)
        raise e