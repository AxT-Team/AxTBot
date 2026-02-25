from src.Utils.PluginBase import command
from src.Utils.EventClass import MessageEventPayload
from src.Utils.Logger import logger

from uapis_extension import get_from_api

__metadata__ = {
    "name": "[官方插件]Ping",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "获取网站到节点的延迟信息",
    "official": True,
}

@command(["ping", "/ping"])
async def ping_handler(event: MessageEventPayload):
    if event.content in ["/ping", "/ping ", "ping", "ping "]:
        content = "========Ping查询菜单========" + "\n" + \
                   "/ping [IP] [查询节点] - 查询IP地址延迟及归属地" + "\n" + \
                   "可选的查询节点有:" + "\n" + \
                   "- cn | 中国湖北十堰/电信" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ping 域名/IP cn" + "\n" + \
                   "=========================="
        await event.reply(content=content)
        return
    
    parts = event.content.split(" ")
    if len(parts) < 2 or not parts[1]:
        await event.reply(content="请提供IP地址或域名")
        return
    
    host = parts[1]
    checkpoint = "中国湖北十堰/电信"
    
    try:
        info = await get_from_api(f"/api/v1/network/ping?host={host}")
        
        if not info:
            await event.reply(content='未查询到该IP地址')
            return
        
        content = "=====Ping信息=====" + "\n" + \
                "主机名: " + info.get("host", "未知").replace('.', ',') + "\n" + \
                "| IP: " + info.get("ip", "未知") + "\n" + \
                "| 最大延迟: " + str(info.get("max", "未知")) + " ms\n" + \
                "| 平均延迟: " + str(info.get("avg", "未知")) + " ms\n" + \
                "| 最小延迟: " + str(info.get("min", "未知")) + " ms\n" + \
                "| 归属地: " + str(info.get("location", "未知")) + "\n" + \
                "| 检测点: " + checkpoint + "\n" + \
                "=============="
        
        await event.reply(content=content)
        
    except Exception as e:
        logger.error(f"Ping插件 >>> 查询失败")
        logger.error(f"  ├─ 主机: {host}")
        logger.error(f"  ├─ 错误类型: {type(e).__name__}")
        logger.error(f"  └─ 错误信息: {str(e)}")
        await event.reply(content=f'查询失败：{str(e)}')