from src.Utils.PluginBase import command
from src.Utils.EventClass import GroupMessageEvent
from src.Utils.Logger import logger

from uapis_extension import get_from_api, translate_domain_status

__metadata__ = {
    "name": "[官方插件]获取Whois信息",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "通过Uapis获取Whois信息",
    "official": True,
}

@command(["whois", "/whois"])
async def whois_handler(event: GroupMessageEvent) -> str:
    if event.content in ["/whois", "/whois ", "whois", "whois "]:
        content =  "=======Whois查询菜单=======" + "\n" + \
                   "/whois [域名] - 查询域名信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /whois 域名" + "\n" + \
                   "=========================="
        await event.reply(content=content)
        return
    
    parts = event.content.split(" ")
    if len(parts) < 2 or not parts[1]:
        await event.reply(content="请提供域名")
        return
    
    domain_name = parts[1]
    
    try:
        info = await get_from_api(f"/api/v1/network/whois?domain={domain_name}&format=json")
        if info is None:
            await event.reply(content="未查询到该域名信息或暂不支持查询该格式")
            return
        
        # 安全地获取嵌套字典的值
        whois_info = info.get("whois", {})
        domain = whois_info.get("domain", {})
        registrar = whois_info.get("registrar", {})
        
        # 处理域名状态
        domain_status = domain.get("status", [])
        domain_status_translated = translate_domain_status(domain_status)
        domain_status_str = "\n".join([status for status in domain_status_translated])
        
        # 处理DNS服务器
        name_servers = domain.get("name_servers", [])
        dns_str = ", ".join([dns.replace(".", ",") for dns in name_servers])
        
        content = "=====Whois信息=====" + "\n" + \
                "| 注册邮箱: " + registrar.get("email", "未知").replace(".", ",") + "\n" + \
                "| 注册电话: " + registrar.get("phone", "未知") + "\n" + \
                "| 注册公司: " + registrar.get("name", "未知").replace(".", ",") + "\n" + \
                "| 注册日期: " + domain.get("created_date_in_time", "未知").replace("T", " ").replace("Z", "") + "\n" + \
                "| 更新日期: " + domain.get("updated_date_in_time", "未知").replace("T", " ").replace("Z", "") + "\n" + \
                "| 过期日期: " + domain.get("expiration_date_in_time", "未知").replace("T", " ").replace("Z", "") + "\n" + \
                "=====域名状态=====" + "\n" + \
                domain_status_str + "\n" + \
                "======DNS======" + "\n" + \
                dns_str + "\n" + \
                "==============" + "\n" + \
                "由于QQ官方消息审核限制，域名相关的.已被替换为," + "\n" + \
                "=============="
        await event.reply(content=content)
        
    except Exception as e:
        logger.error(f"Whois插件 >>> 查询域名信息失败")
        logger.error(f"  ├─ 域名: {domain_name}")
        logger.error(f"  ├─ 错误类型: {type(e).__name__}")
        logger.error(f"  └─ 错误信息: {str(e)}")
        await event.reply(content=f"查询域名信息失败：{str(e)}")