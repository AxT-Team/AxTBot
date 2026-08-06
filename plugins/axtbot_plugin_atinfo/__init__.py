from app import on_command
from app.classes import Message, PluginMetadata
from app.modules import get_uptime, counter

from .function import get_system_info
__meta__ = PluginMetadata(
    name="状态信息",
    version="1.0.0",
    author="Shanshui2024",
    description="该插件通过'/atinfo' 获取当前机器人的在线时间、群聊/私聊收发消息数"
)

@on_command("atinfo")
async def handle_function(event: Message):
    stats = counter.get_stats()
    system = await get_system_info()
    uptime = get_uptime()
    content = f"""
AxTBot v2.1.1 系统状态
===============
CPU：{system["cpu_usage"]}
RAM：{system["ram_usage"]}
====消息数统计====
群聊收/发：{stats["group_received"]}/{stats["group_sent"]}
私聊收/发：{stats["private_received"]}/{stats["private_sent"]}
===============
已正常运行
{uptime}
===============
官方社区群：832275338
==============="""
    await event.reply(content=content, quote=False)