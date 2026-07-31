"""
Interaction Reply Payload for QQ Webhook event

Author: Shanshui2024
Organization: AxT-Team
"""
import aiohttp

from app.modules import logger
async def interaction_reply(inter_id: str, code: int = 0):
    from app.service.qq_service.AccessToken import accesstoken
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"QQBot {accesstoken.access_token}"}
            body = {"code": code}
            async with session.put(f"https://api.bot.qq.com/interactions/{inter_id}", headers=headers, timeout=1, body=body) as response:
                if response.status == 200:
                    logger.debug("适配器 >>> 互动消息回调结束，结果：成功")
                else:
                    data = await response.json()
                    logger.error(f"适配器 >>> 互动消息回调失败 接口返回错误：{data}")
    except TimeoutError:
        logger.error(f"适配器 >>> 互动消息回调失败：连接超时")
    except Exception as e:
        logger.error(e)
        raise e