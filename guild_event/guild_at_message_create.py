from datetime import datetime

from botpy.message import Message
from botpy.types.message import Reference

from utils.get_hypixel_info import get_hypixel_info
from utils.get_minecraft_info import get_minecraft_uuid, get_player_history
from utils.get_system_info import get_system_info
from utils.get_uapis import get_ip_info, get_ping_info, get_whois_info, get_hot_list, format_hot_search, \
    translate_domain_status, get_answer_book


async def handle_guild_at_message_create(client, message: Message):
    msg = " ".join(message.content.split()[1:])
    message_reference = Reference(message_id=message.id, ignore_get_message_error=False)
    print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]" + "[GuildAtMessage]"
          + " | GuildID:" + message.guild_id
          + " | ChannelID:" + message.channel_id
          + " | MsgID:" + message.id
          + " | " + msg)

    if msg.startswith("/atinfo"):
        info = await get_system_info()
        contents = "AxTBot Public v" + str(client.get_version()) + "\n" + \
                   "===============" + "\n" + \
                   "CPU: " + info["cpu_usage"] + "\n" + \
                   "RAM: " + info["ram_usage"] + "\n" + \
                   "====消息数统计====" + "\n" + \
                   "群聊收/发: " + str(client.get_group_message_number()) + "\n" + \
                   "私聊收/发: " + str(client.get_friend_message_number()) + "\n" + \
                   "频道收/发: " + str(client.get_guild_group_message_number()) + "\n" + \
                   "频道私聊收/发: " + str(client.get_guild_friend_message_number()) + "\n" + \
                   "===============" + "\n" + \
                   "已正常运行" + "\n" + \
                   client.get_run_time() + "\n" + \
                   "===============" + "\n" + \
                   "官方社区群: 832275338" + "\n" + \
                   "==============="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=contents,
            msg_id=message.id
        )

    # 菜单列表
    if msg == "/mc" or msg == "/mc ":
        contents = "======Minecraft查询菜单======" + "\n" + \
                   "/mc [ID] - 查询玩家UUID及历史用户名" + "\n" + \
                   "#mcskin [ID] - 查询玩家皮肤" + "\n" + \
                   "#mchead [ID] - 查询玩家皮肤Head" + "\n" + \
                   "#mcbody [ID] - 查询玩家皮肤Body" + "\n" + \
                   "==========================" + "\n" + \
                   "[ID]为玩家用户名" + "\n" + \
                   "=========================="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=contents,
            msg_id=message.id
        )

    if msg == "/ping" or msg == "/ping ":
        contents = "========Ping查询菜单========" + "\n" + \
                   "/ping [IP] [查询节点] - 查询IP地址延迟及归属地" + "\n" + \
                   "可选的查询节点有:" + "\n" + \
                   "- cn | 中国湖北十堰/电信" + "\n" + \
                   "- hk | 中国香港/腾讯云" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ping 域名/IP cn" + "\n" + \
                   "=========================="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=contents,
            msg_id=message.id
        )

    if msg == "/ipinfo" or msg == "/ipinfo ":
        contents = "=======IPInfo查询菜单=======" + "\n" + \
                   "/ipinfo [IP] - 查询IP详细信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ipinfo IP" + "\n" + \
                   "=========================="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=contents,
            msg_id=message.id
        )

    if msg == "/whois" or msg == "/whois ":
        contents = "=======Whois查询菜单=======" + "\n" + \
                   "/whois [域名] - 查询域名信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /whois 域名" + "\n" + \
                   "=========================="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=contents,
            msg_id=message.id
        )

    if msg == "/hotlist" or msg == "/hotlist ":
        contents = "=======每日热榜菜单=======" + "\n" + \
                   "/hotlist [热榜类型] - 查询指定热榜信息" + "\n" + \
                   "可选的热榜类型有:" + "\n" + \
                   "- weibo | 微博热搜榜" + "\n" + \
                   "- bilibili | 哔哩哔哩全站日榜" + "\n" + \
                   "- bilihot | 哔哩哔哩热搜榜" + "\n" + \
                   "- zhihu | 知乎热搜榜" + "\n" + \
                   "- douyin | 抖音热搜榜" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /hotlist weibo" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，视为热榜内含有违规信息，被QQ消息审核拦截" + "\n" + \
                   "=========================="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=contents,
            msg_id=message.id
        )

    # 功能区域
    if msg.startswith("/hyp"):
        await client.api.post_group_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=get_hypixel_info(msg, message.id),
            msg_id=message.id
        )

    if msg.startswith("/mc ") and msg.split(" ")[1] is not None:
        uuid = await get_minecraft_uuid(msg.split(" ")[1])
        history_info = await get_player_history(uuid)

        # 用于存储格式化的历史记录
        formatted_history = []

        for record in history_info:
            name = record.get("name", "")
            changed_to_at = record.get("changedToAt", "")
            formatted_history.append(f"{name} - {changed_to_at}")

        if uuid is None:
            await client.api.post_message(
                channel_id=message.channel_id,
                message_reference=message_reference,
                content="未查询到该玩家的信息",
                msg_id=message.id
            )
            return

        if history_info is None:
            formatted_history = "未查询到当前玩家的历史用户名信息"

        contents = "===Minecraft玩家查询===" + "\n" + \
                   "| 玩家ID: " + msg.split(" ")[1] + "\n" + \
                   "| UUID: " + uuid + "\n" + \
                   "===历史用户名===\n" + "\n".join(formatted_history)

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=contents,
            msg_id=message.id
        )

    if msg.startswith("#mchead ") and msg.split(" ")[1] is not None:
        uuid = await get_minecraft_uuid(msg.split(" ")[1])
        if uuid is None:
            await client.api.post_message(
                channel_id=message.channel_id,
                message_reference=message_reference,
                content="未查询到该玩家的信息",
                msg_id=message.id
            )
            return

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            msg_id=message.id,
            image="https://crafatar.com/avatars/" + uuid
        )

    if msg.startswith("#mcbody ") and msg.split(" ")[1] is not None:
        uuid = await get_minecraft_uuid(msg.split(" ")[1])
        if uuid is None:
            await client.api.post_message(
                channel_id=message.channel_id,
                message_reference=message_reference,
                content="未查询到该玩家的信息",
                msg_id=message.id
            )
            return

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            msg_id=message.id,
            image="https://crafatar.com/renders/body/" + uuid
        )

    if msg.startswith("#mcskin ") and msg.split(" ")[1] is not None:
        uuid = await get_minecraft_uuid(msg.split(" ")[1])
        if uuid is None:
            await client.api.post_message(
                channel_id=message.channel_id,
                message_reference=message_reference,
                content="未查询到该玩家的信息",
                msg_id=message.id
            )
            return

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            msg_id=message.id,
            image="https://crafatar.com/skins/" + uuid
        )

    if msg.startswith("/ipinfo ") and msg.split(" ")[1] is not None:
        info = await get_ip_info(msg.split(" ")[1])
        if info is None:
            await client.api.post_message(
                channel_id=message.channel_id,
                message_reference=message_reference,
                content="未查询到该IP信息",
                msg_id=message.id
            )
            return
        else:
            content = "=====IP信息=====" + "\n" + \
                      "IP: " + info["ip"] + "\n" + \
                      "| 开始 IP: " + info["beginip"] + "\n" + \
                      "| 结束 IP: " + info["endip"] + "\n" + \
                      "| 归属地: " + info["region"] + "\n" + \
                      "| 纬度: " + str(info["latitude"]) + "\n" + \
                      "| 经度: " + str(info["longitude"]) + "\n" + \
                      "| ISP: " + info["isp"] + "\n" + \
                      "| LLC: " + info["LLC"] + "\n" + \
                      "| ASN: " + info["asn"] + "\n" + \
                      "=============="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=content,
            msg_id=message.id
        )

    if msg.startswith("/ping ") and msg.split(" ")[1] is not None:
        info = None
        checkpoint = None
        ipinfo = await get_ip_info(msg.split(" ")[1])
        node = msg.split(" ")[2]
        if node == "cn":
            info = await get_ping_info(ipinfo["ip"], "cn")
            checkpoint = "中国湖北十堰/电信"
        elif node == "hk":
            info = await get_ping_info(ipinfo["ip"], "hk")
            checkpoint = "中国香港/腾讯云"

        content = "=====Ping信息=====" + "\n" + \
                  "主机名: " + info["host"] + "\n" + \
                  "| IP: " + info["ip"] + "\n" + \
                  "| 最大延迟: " + str(info["max"]) + "\n" + \
                  "| 平均延迟: " + str(info["avg"]) + "\n" + \
                  "| 最小延迟: " + str(info["min"]) + "\n" + \
                  "| 归属地: " + ipinfo["region"] + ipinfo["isp"] + "\n" + \
                  "| 检测点: " + checkpoint + "\n" + \
                  "=============="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=content,
            msg_id=message.id
        )

    if msg.startswith("/whois ") and msg.split(" ")[1] is not None:
        info = await get_whois_info(msg.split(" ")[1])
        if info is None:
            await client.api.post_message(
                channel_id=message.channel_id,
                message_reference=message_reference,
                content="未查询到该域名信息或暂不支持查询该格式",
                msg_id=message.id
            )
            return
        else:
            domain_status_translated = translate_domain_status(info["domain_status"])
            domain_status_str = "\n".join([status for status in domain_status_translated])
            dns_str = ", ".join([dns.replace(".", ",") for dns in info["dns"]])
            content = "=====Whois信息=====" + "\n" + \
                      "| 注册地址: " + info["reg_url"].replace("http://", "").replace("https://", "").replace(".",
                                                                                                              ",") + "\n" + \
                      "| 注册邮箱: " + info["email"].replace(".", ",") + "\n" + \
                      "| 注册电话: " + info["phone"] + "\n" + \
                      "| 注册公司: " + info["LLC"] + "\n" + \
                      "| 注册日期: " + info["reg_date"] + "\n" + \
                      "| 更新日期: " + info["updated_date"] + "\n" + \
                      "| 过期日期: " + info["exp_date"] + "\n" + \
                      "=====域名状态=====" + "\n" + \
                      domain_status_str + "\n" + \
                      "======DNS======" + "\n" + \
                      dns_str + "\n" + \
                      "==============" + "\n" + \
                      "由于QQ官方消息审核限制，域名相关的.已被替换为," + "\n" + \
                      "=============="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=content,
            msg_id=message.id
        )

    if msg.startswith("/hotlist ") and msg.split(" ")[1] is not None:
        hot_list = None
        hot_type = None

        if msg.split(" ")[1] == "bilibili":
            hot_list = await get_hot_list("bilibili")
            hot_type = "B站-日榜"
        elif msg.split(" ")[1] == "bilihot":
            hot_list = await get_hot_list("bilihot")
            hot_type = "B站-热搜榜"
        elif msg.split(" ")[1] == "weibo":
            hot_list = await get_hot_list("weibo")
            hot_type = "微博-热搜榜"
        elif msg.split(" ")[1] == "zhihu":
            hot_list = await get_hot_list("zhihu")
            hot_type = "知乎-热搜榜"
        elif msg.split(" ")[1] == "douyin":
            hot_list = await get_hot_list("douyin")
            hot_type = "抖音-热搜榜"

        if hot_list is None:
            await client.api.post_message(
                channel_id=message.channel_id,
                message_reference=message_reference,
                content="未查询到该热搜信息",
                msg_id=message.id
            )
            return
        else:
            content = "===" + hot_type + "===" + "\n" + \
                      format_hot_search(hot_list) + "\n" + \
                      "=============" + "\n" + \
                      hot_list["update_time"] + "\n" + \
                      "============="

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=content,
            msg_id=message.id
        )

    if msg.startswith("/ask ") and msg.split(" ")[1] is not None:
        info = await get_answer_book()
        if info is None:
            await client.api.post_message(
                channel_id=message.channel_id,
                message_reference=message_reference,
                content="获取失败，请联系管理员修复",
                msg_id=message.id
            )
            return
        else:
            content = "\n" + info

        await client.api.post_message(
            channel_id=message.channel_id,
            message_reference=message_reference,
            content=content,
            msg_id=message.id
        )
