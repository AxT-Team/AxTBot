from botpy.message import GroupMessage, Message, DirectMessage
from utils.get_system_info import get_system_info
from utils.get_minecraft_info import get_minecraft_uuid, get_player_history
from utils.get_hypixel_info import get_hypixel_info
from utils.get_uapis import get_ip_info, get_ping_info, translate_domain_status, get_whois_info, get_hot_list, \
    format_hot_search

class HandleAtMessage:
    def __init__(self, client):
        self.client = client
        self.sendMessage = None
        self.sendFile = None

    def sendmessage(self, message, content):
        if isinstance(message, GroupMessage):
            self.client.api.post_group_message(
                group_openid=message.group_openid,
                msg_type=0,
                content=content,
                msg_id=message.id
            )
        if isinstance(message, Message):
            self.client.api.post_message(

            )
        if isinstance(message, DirectMessage):
            self.client.api.post_dms(

            )

    async def send_message(self, message):
        if isinstance(message, GroupMessage):
            self.sendMessage = self.client.api.post_group_message
            self.sendFile = self.client.api.post_group_file
        if isinstance(message, Message):
            self.sendMessage = self.client.api.post_message
        if isinstance(message, DirectMessage):
            self.sendMessage = self.client.api.post_dms

        if message.content.lstrip().startswith("/atinfo"):
            await self.atinfo(message)
        if message.content.lstrip().startswith("/mc"):
            await self.mc(message)
        if message.content.lstrip().startswith("/ping"):
            await self.ping(message)
        if message.content.lstrip().startswith("/ipinfo"):
            await self.ipinfo(message)
        if message.content.lstrip().startswith("/whois"):
            await self.whois(message)
        if message.content.lstrip().startswith("/hyp"):
            await self.hyp(message)
        if message.content.lstrip().startswith("/mc "):
            await self.mc_(message)
        if message.content.lstrip().startswith("#mchead"):
            await self.mchead(message)
        if message.content.lstrip().startswith("#mcbody"):
            await self.mcbody(message)
        if message.content.lstrip().startswith("#mcskin"):
            await self.mcskin(message)
        if message.content.lstrip().startswith("/ipinfo "):
            await self.ipinfo_(message)
        if message.content.lstrip().startswith("/ping "):
            await self.ping_(message)
        if message.content.lstrip().startswith("/whois "):
            await self.whois_(message)
        if message.content.lstrip().startswith("/icp "):
            await self.icp_(message)
        if message.content.lstrip().startswith("/hotlist "):
            await self.hotlist_(message)

    async def atinfo(self, message):
        info = get_system_info()
        content = "\nAxTBot Public v1.0\n" + \
                  "===============" + "\n" + \
                  "CPU: " + info["cpu_usage"] + "\n" + \
                  "RAM: " + info["ram_usage"] + "\n" + \
                  "收/发消息数: " + "\n" + \
                  "===============" + "\n" + \
                  "已正常运行" + "\n" + \
                  self.client.get_run_time() + "\n" + \
                  "===============" + "\n" + \
                  "官方社区群: 832275338" + "\n" + \
                  "==============="

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=content,
            msg_id=message.id
        )

    async def mc(self, message):
        contents = "\n======Minecraft查询菜单======" + "\n" + \
                   "/mc [ID] - 查询玩家UUID及历史用户名" + "\n" + \
                   "#mcskin [ID] - 查询玩家皮肤" + "\n" + \
                   "#mchead [ID] - 查询玩家皮肤Head" + "\n" + \
                   "#mcbody [ID] - 查询玩家皮肤Body" + "\n" + \
                   "==========================" + "\n" + \
                   "[ID]为玩家用户名" + "\n" + \
                   "=========================="

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=contents,
            msg_id=message.id
        )

    async def ping(self, message):
        contents = "\n========Ping查询菜单========" + "\n" + \
                   "/ping [IP] [查询节点] - 查询IP地址延迟及归属地" + "\n" + \
                   "可选的查询节点有:" + "\n" + \
                   "- cn | 中国湖北十堰/电信" + "\n" + \
                   "- hk | 中国香港/腾讯云" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ping 域名/IP cn" + "\n" + \
                   "=========================="

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=contents,
            msg_id=message.id
        )

    async def ipinfo(self, message):
        contents = "\n=======IPInfo查询菜单=======" + "\n" + \
                   "/ipinfo [IP] - 查询IP详细信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ipinfo IP" + "\n" + \
                   "=========================="

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=contents,
            msg_id=message.id
        )

    async def whois(self, message):
        contents = "\n=======Whois查询菜单=======" + "\n" + \
                   "/whois [域名] - 查询域名信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /whois 域名" + "\n" + \
                   "=========================="

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=contents,
            msg_id=message.id
        )

    async def hyp(self, message):
        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content="\n" + get_hypixel_info(message.content.lstrip(), message.id),
            msg_id=message.id
        )

    async def mc_(self, message):
        uuid = get_minecraft_uuid(message.content.lstrip().split(" ")[1])
        history_info = get_player_history(uuid)

        # 用于存储格式化的历史记录
        formatted_history = []

        for record in history_info:
            name = record.get("name", "")
            changed_to_at = record.get("changedToAt", "")
            formatted_history.append(f"{name} - {changed_to_at}")

        if uuid is None:
            await self.sendMessage(
                group_openid=message.group_openid,
                msg_type=0,
                content="未查询到该玩家的信息",
                msg_id=message.id
            )
            return

        if history_info is None:
            formatted_history = "未查询到当前玩家的历史用户名信息"

        contents = "\n===Minecraft玩家查询===" + "\n" + \
                   "| 玩家ID: " + message.content.lstrip().split(" ")[1] + "\n" + \
                   "| UUID: " + uuid + "\n" + \
                   "===历史用户名===\n" + "\n".join(formatted_history)

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=contents,
            msg_id=message.id
        )

    async def mchead(self, message):
        uuid = get_minecraft_uuid(message.content.lstrip().split(" ")[1])
        if uuid is None:
            await self.sendMessage(
                group_openid=message.group_openid,
                msg_type=0,
                content="未查询到该玩家的信息",
                msg_id=message.id
            )
            return

        upload_media = self.sendFile(
            group_openid=message.group_openid,
            file_type=1,
            url="https://crafatar.com/avatars/" + uuid
        )

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=7,
            msg_id=message.id,
            media=upload_media
        )

    async def mcbody(self, message):
        uuid = get_minecraft_uuid(message.content.lstrip().split(" ")[1])
        if uuid is None:
            await self.sendMessage(
                group_openid=message.group_openid,
                msg_type=0,
                content="未查询到该玩家的信息",
                msg_id=message.id
            )
            return

        upload_media = self.sendFile(
            group_openid=message.group_openid,
            file_type=1,
            url="https://crafatar.com/renders/body/" + uuid
        )

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=7,
            msg_id=message.id,
            media=upload_media
        )

    async def mcskin(self, message):
        uuid = get_minecraft_uuid(message.content.lstrip().split(" ")[1])
        if uuid is None:
            await self.sendMessage(
                group_openid=message.group_openid,
                msg_type=0,
                content="未查询到该玩家的信息",
                msg_id=message.id
            )
            return

        upload_media = self.sendFile(
            group_openid=message.group_openid,
            file_type=1,
            url="https://crafatar.com/skins/" + uuid
        )

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=7,
            msg_id=message.id,
            media=upload_media
        )

    async def ipinfo_(self, message):
        info = get_ip_info(message.content.lstrip().split(" ")[1])
        if info is None:
            await self.sendMessage(
                group_openid=message.group_openid,
                msg_type=0,
                content="未查询到该IP信息",
                msg_id=message.id
            )
            return
        else:
            content = "\n=====IP信息=====" + "\n" + \
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

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=content,
            msg_id=message.id
        )

    async def ping_(self, message):
        info = None
        checkpoint = None
        ipinfo = get_ip_info(message.content.lstrip().split(" ")[1])
        node = message.content.lstrip().split(" ")[2]
        if node == "cn":
            info = get_ping_info(ipinfo["ip"], "cn")
            checkpoint = "中国湖北十堰/电信"
        elif node == "hk":
            info = get_ping_info(ipinfo["ip"], "hk")
            checkpoint = "中国香港/腾讯云"

        content = "\n=====Ping信息=====" + "\n" + \
                  "主机名: " + info["host"] + "\n" + \
                  "| IP: " + info["ip"] + "\n" + \
                  "| 最大延迟: " + str(info["max"]) + "\n" + \
                  "| 平均延迟: " + str(info["avg"]) + "\n" + \
                  "| 最小延迟: " + str(info["min"]) + "\n" + \
                  "| 归属地: " + ipinfo["region"] + ipinfo["isp"] + "\n" + \
                  "| 检测点: " + checkpoint + "\n" + \
                  "=============="

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=content,
            msg_id=message.id
        )

    async def whois_(self, message):
        info = get_whois_info(message.content.lstrip().split(" ")[1])
        if info is None:
            await self.sendMessage(
                group_openid=message.group_openid,
                msg_type=0,
                content="未查询到该域名信息或暂不支持查询该格式",
                msg_id=message.id
            )
            return
        else:
            domain_status_translated = translate_domain_status(info["domain_status"])
            domain_status_str = "\n".join([status for status in domain_status_translated])
            dns_str = ", ".join([dns.replace(".", ",") for dns in info["dns"]])
            content = "\n=====Whois信息=====" + "\n" + \
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

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=content,
            msg_id=message.id
        )

    async def icp_(self, message):
        icp = None

        if message.content.lstrip().split(" ")[1] == "web":
            icp = get_icp_web_info()
        elif message.content.lstrip().split(" ")[1] == "app":
            icp = get_icp_app_info()
        elif message.content.lstrip().split(" ")[1] == "小程序":
            icp = get_icp_mapp_info()
        elif message.content.lstrip().split(" ")[1] == "快应用":
            icp = get_icp_kapp_info()

        if icp is None:
            content = error_message()
            await self.sendMessage(
                group_openid=message.group_openid,
                msg_type=0,
                content=content,
                msg_id=message.id
            )

    async def hotlist_(self, message):
        hot_list = None
        hot_type = None

        if message.content.lstrip().split(" ")[1] == "bilibili":
            hot_list = get_hot_list("bilibili")
            hot_type = "B站-日榜"
        elif message.content.lstrip().split(" ")[1] == "bilihot":
            hot_list = get_hot_list("bilihot")
            hot_type = "B站-热搜榜"
        elif message.content.lstrip().split(" ")[1] == "weibo":
            hot_list = get_hot_list("weibo")
            hot_type = "微博-热搜榜"
        elif message.content.lstrip().split(" ")[1] == "zhihu":
            hot_list = get_hot_list("zhihu")
            hot_type = "知乎-热搜榜"
        elif message.content.lstrip().split(" ")[1] == "douyin":
            hot_list = get_hot_list("douyin")
            hot_type = "抖音-热搜榜"

        if hot_list is None:
            await self.sendMessage(
                group_openid=message.group_openid,
                msg_type=0,
                content="未查询到该热搜信息",
                msg_id=message.id
            )
            return
        else:
            content = "\n===" + hot_type + "===" + "\n" + \
                      format_hot_search(hot_list) + "\n" + \
                      "=============" + "\n" + \
                      hot_list["update_time"] + "\n" + \
                      "============="

        await self.sendMessage(
            group_openid=message.group_openid,
            msg_type=0,
            content=content,
            msg_id=message.id
        )
