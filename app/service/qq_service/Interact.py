"""
Interaction Reply Payload for QQ Webhook event

Author: Shanshui2024
Organization: AxT-Team
"""
import aiohttp

from app.modules import logger
async def interaction_reply(inter_id: str, code: int = 0) -> dict:
    """
    完成事件回调逻辑

    Args:
        inter_id (str): 互动消息ID，可从互动消息包中获取
        code (int): 返回内容 默认为0（成功）

    Returns:
        dict: 返回事件数据 成功为空（{}）

    Raises:
        TimeoutError: 如果回调超时，抛出异常
        Exception: 如果有其他错误，抛出异常

    ---
    详见官方文档：https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/interactions_interaction_id.put.html
    """
    
    from app.service.qq_service.AccessToken import accesstoken
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"QQBot {accesstoken.access_token}"}
            json = {"code": str(code)}
            async with session.put(f"https://api.bot.qq.com/interactions/{inter_id}", headers=headers, timeout=1, json=json) as response:
                if response.status == 200:
                    logger.debug("适配器 >>> 互动消息回调结束，结果：成功")
                    return {}
                else:
                    data = await response.json()
                    logger.error(f"适配器 >>> 互动消息回调失败 接口返回错误：{data}")
                    return data
    except TimeoutError:
        logger.error(f"适配器 >>> 互动消息回调失败：连接超时")
        return {"mesasge": "互动回调失败，连接超时", "code": 630005}
    except Exception as e:
        logger.error(e)
        raise e