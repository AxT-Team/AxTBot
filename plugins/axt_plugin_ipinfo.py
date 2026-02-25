import re

from src.Utils.PluginBase import command
from src.Utils.EventClass import MessageEventPayload
from src.Utils.Logger import logger

from uapis_extension import get_from_api

__metadata__ = {
    "name": "[官方插件]获取IP地址信息",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "获取IP地址信息",
    "official": True,
}

@command(["ipinfo", "/ipinfo"])
async def ipinfo_handler(event: MessageEventPayload):
    parts = event.content.split(" ")
    if len(parts) < 2 or not parts[1]:
        contents = "=======IPInfo查询菜单=======" + "\n" + \
                   "/ipinfo [IP] - 查询IP详细信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ipinfo 1.1.1.1" + "\n" + \
                   "=========================="
        await event.reply(contents)
        return
    
    host = parts[1]
    host = re.sub(r'^https?://', '', host, flags=re.IGNORECASE)
    
    try:
        info = await get_from_api(f"api/v1/network/ipinfo?ip={host}")
        if info is None:
            await event.reply('未查询到该IP信息')
            return
        
        # 使用 .get() 方法安全地获取字段，提供默认值
        contents = "=====IP信息=====" + "\n" + \
                "IP: " + info.get("ip", "未知") + "\n" + \
                "| 开始 IP: " + info.get("beginip", "未知") + "\n" + \
                "| 结束 IP: " + info.get("endip", "未知") + "\n" + \
                "| 归属地: " + info.get("region", "未知") + "\n" + \
                "| 纬度: " + str(info.get("latitude", "未知")) + "\n" + \
                "| 经度: " + str(info.get("longitude", "未知")) + "\n" + \
                "| ISP: " + str(info.get("isp", "未知")) + "\n" + \
                "| LLC: " + info.get("llc", "未知") + "\n" + \
                "| ASN: " + str(info.get("asn", "未知")) + "\n" + \
                "=============="
        await event.reply(contents)
        
    except Exception as e:
        logger.error(f"IPInfo插件 >>> 查询IP信息失败")
        logger.error(f"  ├─ IP地址: {host}")
        logger.error(f"  ├─ 错误类型: {type(e).__name__}")
        logger.error(f"  └─ 错误信息: {str(e)}")
        await event.reply(f"查询IP信息失败：{str(e)}")