from Core.Event import group_handle_event, send_group_message
from utils.get_uapis import get_ip_info


@group_handle_event("/ipinfo", "ipinfo")
async def ipinfo_handler(event):
    if event.content in ["/ipinfo", "/ipinfo ", "ipinfo", "ipinfo "]:
        contents = "\n=======IPInfo查询菜单=======" + "\n" + \
                   "/ipinfo [IP] - 查询IP详细信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ipinfo IP" + "\n" + \
                   "=========================="
        await send_group_message(event.group_openid, msg_type=0, content=contents, msg_id=event.msg_id)
        return
    else:
        msg = event.content
        if msg.startswith(("/ipinfo ", "ipinfo ")) and len(msg.split(" ")) > 1:
            ip = msg.split(" ")[1]
            info = await get_ip_info(ip)
            if info is None:
                contents = "未查询到该IP的信息"
            else:
                contents = "\n=====IP信息=====" + "\n" + \
                        "IP: " + info["ip"] + "\n" + \
                        "| 开始 IP: " + info["start_ip"] + "\n" + \
                        "| 结束 IP: " + info["end_ip"] + "\n" + \
                        "| 归属地: " + info["country"] + " " + info["region"] + "\n" + \
                        "| 纬度: " + str(info["latitude"]) + "\n" + \
                        "| 经度: " + str(info["longitude"]) + "\n" + \
                        "| LLC: " + info["company"] + "\n" + \
                        "| ASN: " + 'AS' + str(info["asn"]) + "\n" + \
                        "=============="
            await send_group_message(event.group_openid, msg_type=0, content=contents, msg_id=event.msg_id)
            return