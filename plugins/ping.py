from Core.Event import group_handle_event, send_group_message
from utils.get_uapis import get_ping_info

@group_handle_event("/ping", "/ping ", "ping", "ping ")
async def ping_handler(event):
    if event.content in ["/ping", "/ping ", "ping", "ping "]:
        content = "\n========Ping查询菜单========" + "\n" + \
                   "/ping [IP] [查询节点] - 查询IP地址延迟及归属地" + "\n" + \
                   "可选的查询节点有:" + "\n" + \
                   "- cn | 中国湖北十堰/电信" + "\n" + \
                   "- hk | 中国香港/腾讯云" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ping 域名/IP cn" + "\n" + \
                   "=========================="
        await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
    else:
        msg = event.content
        if msg.startswith(("/ping ","ping ")) and msg.split(" ")[1] is not None:
            info = checkpoint = None
            try:
                node = msg.split(" ")[2]
            except IndexError:
                node = 'cn'
            if node == "cn":
                try:
                    info = await get_ping_info(msg.split(" ")[1], "cn")
                    checkpoint = "中国湖北十堰/电信"
                except TypeError as e:
                    await send_group_message(event.group_openid, msg_type=0, content='未查询到该IP地址', msg_id=event.msg_id)
                    return
            elif node == "hk":
                try:
                    info = await get_ping_info(msg.split(" ")[1], "hk")
                    checkpoint = "中国香港/腾讯云"
                except TypeError as e:
                    await send_group_message(event.group_openid, msg_type=0, content='未查询到该IP地址', msg_id=event.msg_id)
                    return
            if info:
                content = "\n=====Ping信息=====" + "\n" + \
                        "主机名: " + info["host"].replace('.',',') + "\n" + \
                        "| IP: " + info["ip"] + "\n" + \
                        "| 最大延迟: " + str(info["max"]) + " ms\n" + \
                        "| 平均延迟: " + str(info["avg"]) + " ms\n" + \
                        "| 最小延迟: " + str(info["min"]) + " ms\n" + \
                        "| 归属地: " + str(info["location"]) + "\n" + \
                        "| 检测点: " + checkpoint + "\n" + \
                        "=============="

                await send_group_message(event.group_openid, msg_type=0, content=content, msg_id=event.msg_id)
                return
            else:
                await send_group_message(event.group_openid, msg_type=0, content='未查询到该IP地址', msg_id=event.msg_id)
                return