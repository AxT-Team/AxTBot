from Core.Event import group_handle_event, send_group_message
from utils.get_uapis import get_whois_info, translate_domain_status

@group_handle_event("/whois", "/whois ", "whois", "whois ")
async def whois_handler(event):
    if event.content in ["/whois", "/whois ", "whois", "whois "]:
        content = "\n=======Whois查询菜单=======" + "\n" + \
                   "/whois [域名] - 查询域名信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /whois 域名" + "\n" + \
                   "=========================="
        await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
    else:
        msg = event.content
        if msg.startswith(("/whois ","whois ")) and msg.split(" ")[1] is not None:
            info = await get_whois_info(msg.split(" ")[1])
            if info is None:
                await send_group_message(event.group_openid, msg_type=0, content="未查询到该域名信息或暂不支持查询该格式", msg_id=event.msg_id)
                return
            else:
                if info in [{"error": "网络请求失败，请稍后再试。"},{"error": "SSL 证书验证失败，请稍后再试或联系管理员。"}]:
                    await send_group_message(event.group_openid, msg_type=0, content=f"请求失败，请稍后再试。\n详细信息：{info}", msg_id=event.msg_id)
                    return
                domain_status_translated = translate_domain_status(info["domain_status"])
                domain_status_str = "\n".join([status for status in domain_status_translated])
                dns_str = ", ".join([dns.replace(".", ",") for dns in info["dns"]])
                content = "\n=====Whois信息=====" + "\n" + \
                        "| 注册地址: " + info["reg_url"].replace("http://", "").replace("https://", "").replace(".",
                                                                                                                ",") + "\n" + \
                        "| 注册邮箱: " + info["email"].replace(".", ",") + "\n" + \
                        "| 注册电话: " + info["phone"] + "\n" + \
                        "| 注册公司: " + info["LLC"].replace(".", ",") + "\n" + \
                        "| 注册日期: " + info["reg_date"].replace("T", " ").replace("Z", "") + "\n" + \
                        "| 更新日期: " + info["updated_date"].replace("T", " ").replace("Z", "") + "\n" + \
                        "| 过期日期: " + info["exp_date"].replace("T", " ").replace("Z", "") + "\n" + \
                        "=====域名状态=====" + "\n" + \
                        domain_status_str + "\n" + \
                        "======DNS======" + "\n" + \
                        dns_str + "\n" + \
                        "==============" + "\n" + \
                        "由于QQ官方消息审核限制，域名相关的.已被替换为," + "\n" + \
                        "=============="

            await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
            return


