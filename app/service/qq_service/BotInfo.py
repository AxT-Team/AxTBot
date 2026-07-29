"""
Startup Get BotInfo Service for AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import aiohttp, time

from app.modules import logger
from app.modules import get_db, FrameConfig
async def get_qqbot_info():
    from app.service.qq_service.AccessToken import accesstoken
    logger.info("适配器 >>> 正在获取机器人信息")
    db = get_db()
    try:
        bot_username = db.get_frame_config_by_key("bot_username").value
        bot_username
        bot_openid = db.get_frame_config_by_key("bot_union_openid").value
        bot_openid
        bot_id = db.get_frame_config_by_key("bot_id").value
        bot_id
    except Exception as e:
        logger.error(f"数据库 >>> 配置项不存在，错误信息：{e}")
        logger.warning(f"数据库 >>> 重新加载数据...")
        db.add_frame_config(FrameConfig(key="bot_username", value="None", create_time=str(int(time.time())), update_time=str(int(time.time()))))
        bot_username = db.get_frame_config_by_key("bot_username").value
        db.add_frame_config(FrameConfig(key="bot_union_openid", value="None", create_time=str(int(time.time())), update_time=str(int(time.time()))))
        bot_openid = db.get_frame_config_by_key("bot_union_openid").value
        db.add_frame_config(FrameConfig(key="bot_id", value="None", create_time=str(int(time.time())), update_time=str(int(time.time()))))
        bot_id = db.get_frame_config_by_key("bot_id").value


    try:
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"QQBot {accesstoken.access_token}"}
            async with session.get("https://api.bot.qq.com/users/@me", headers=headers, timeout=1) as response:
                if response.status == 200:
                    data = await response.json()
                    bot_username = data["username"]
                    bot_id = data["id"]
                    bot_openid = data["union_openid"]
                    db.update_frame_config("bot_username", bot_username, int(time.time()))
                    db.update_frame_config("bot_union_openid", bot_openid, int(time.time()))
                    db.update_frame_config("bot_id", bot_id, int(time.time()))

                else:
                    data = response.text
                    logger.error(f"适配器 >>> 数据获取失败 接口返回错误：{response.status}")
                    logger.warning(f"适配器 >>> 将读取数据库内的缓存数据...")

                logger.info(f"适配器 >>> ID: {bot_id} | OpenID: {bot_openid} | 机器人 {bot_username} 登录成功！")
    except TimeoutError:
        logger.error(f"适配器 >>> 数据获取失败：连接超时")
        logger.warning(f"适配器 >>> 将读取数据库内的缓存数据...")
        logger.info(f"适配器 >>> ID: {bot_id} | OpenID: {bot_openid} | 机器人 {bot_username} 登录成功！")
    except Exception as e:
        logger.error(e)
        raise e