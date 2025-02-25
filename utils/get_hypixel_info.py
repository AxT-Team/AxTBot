import aiohttp
from aiohttp import ClientError
import asyncio
from Core.Logger import logger


async def get_hypixel_info(command, userid):
    url = 'http://localhost:30001/hypixel?' + 'command=' + command + '&userId=' + userid
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except (ClientError, asyncio.TimeoutError) as e:
            logger.error(f"请求错误: {e}")
            return "请求出错！具体信息：" + str(e)