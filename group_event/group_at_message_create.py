from datetime import datetime

from botpy.message import GroupMessage

from utils.get_system_info import get_system_info
from utils.get_minecraft_info import get_minecraft_uuid, get_player_history
from utils.get_hypixel_info import get_hypixel_info
from utils.get_uapis import get_ip_info, get_ping_info, translate_domain_status, get_whois_info, get_hot_list, \
    format_hot_search, get_answer_book, get_touch_url, get_steamid_info
from utils.jrrp import get_jrrp
from utils.mcping import mcping
from utils.remake import remake
from datetime import datetime
from botpy.message import GroupMessage
from utils.message import post_group_message_decorator
import re

@post_group_message_decorator
async def handle_group_at_message_create(client, message: GroupMessage, post_group_message, post_group_file):
    msg = message.content.lstrip()
    print("[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]" + "[群消息]" + " | 群ID:" + message.group_openid + " | 消息ID:" + message.id + " | " + msg)

    # ------------------------------------菜单区域------------------------------------

    if msg == '/help' or msg == '/help ' or msg == "help" or msg == "help ":
        contents = "\n=======AxT社区机器人=======" + "\n" + \
                   "| help | - 获取帮助菜单" + "\n" + \
                   "| ping | - 显示Ping菜单" + "\n" + \
                   "| ipinfo | - 显示IPInfo菜单" + "\n" + \
                   "| whois | - 显示Whois菜单" + "\n" + \
                   "| hotlist | - 显示每日热榜菜单" + "\n" + \
                   "| mc | - 查询Minecraft相关内容" + "\n" + \
                   "| jrrp | - 获取今日人品" + "\n" + \
                   "| remake | - 重来一世 你会变成什么" + "\n" + \
                   "| ask | - 读赛博之书 品百味人生" + "\n" + \
                   "===============" + "\n" + \
                   "官方社区群: 832275338" + "\n" + \
                   "===============" + "\n" + \
                   "AxTBot Public v" + str(client.get_version())
        await post_group_message(client, message, contents)
        return

    if msg in [
        "/mc", "/mc ", "mc", "mc ", 
        "/mchead ", "/mchead", "mchead ", "mchead", 
        "/mcskin ", "/mcskin", "mcskin ","mcskin", 
        "/mcbody ", "/mcbody", "mcbody ", "mcbody"]:
        contents = "\n======Minecraft查询菜单======" + "\n" + \
                   "/mc [ID] - 查询玩家UUID及历史用户名" + "\n" + \
                   "/mcskin [ID] - 查询玩家皮肤" + "\n" + \
                   "/mchead [ID] - 查询玩家皮肤Head" + "\n" + \
                   "/mcbody [ID] - 查询玩家皮肤Body" + "\n" + \
                   "==========================" + "\n" + \
                   "[ID]为玩家用户名" + "\n" + \
                   "=========================="

        await post_group_message(client, message, contents)
        return

    if msg == "/ping" or msg == "/ping " or msg == "ping" or msg == "ping ":
        contents = "\n========Ping查询菜单========" + "\n" + \
                   "/ping [IP] [查询节点] - 查询IP地址延迟及归属地" + "\n" + \
                   "可选的查询节点有:" + "\n" + \
                   "- cn | 中国湖北十堰/电信" + "\n" + \
                   "- hk | 中国香港/腾讯云" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ping 域名/IP cn" + "\n" + \
                   "=========================="

        await post_group_message(client, message, contents)
        return

    if msg == "/ipinfo" or msg == "/ipinfo " or msg == "ipinfo" or msg == "ipinfo ":
        contents = "\n=======IPInfo查询菜单=======" + "\n" + \
                   "/ipinfo [IP] - 查询IP详细信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /ipinfo IP" + "\n" + \
                   "=========================="

        await post_group_message(client, message, contents)
        return

    if msg == "/whois" or msg == "/whois " or msg == "whois" or msg == "whois ":
        contents = "\n=======Whois查询菜单=======" + "\n" + \
                   "/whois [域名] - 查询域名信息" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /whois 域名" + "\n" + \
                   "=========================="

        await post_group_message(client, message, contents)
        return

    if msg == "/hotlist" or msg == "/hotlist " or msg == "hotlist" or msg == "hotlist ":
        contents = "\n=======每日热榜菜单=======" + "\n" + \
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

        await post_group_message(client, message, contents)
        return

    if msg == "/mcping" or msg == "/mcping " or msg == "mcping" or msg == "mcping ":
        contents = "\n=======服务器查询菜单=======" + "\n" + \
                   "/mcping [IP]:[端口] [服务器类型] - 请求该服务器信息" + "\n" + \
                   "可选的服务器类型有:" + "\n" + \
                   "- java | Java Edition服务器" + "\n" + \
                   "- be | BedRock 基岩服务器" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /mcping mc.hypixel.net" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，则可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "=========================="
        
        await post_group_message(client, message, contents)
        return

    if msg == '摸' or msg == '/摸' or msg == '/摸 ' or msg == '摸 ':
        contents = "\n=======摸一摸菜单=======" + "\n" + \
                   "/摸 [QQ号] - 生成摸一摸GIF" + "\n" + \
                   "==========================" + "\n" + \
                   "使用示例: /摸 3889003621" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "如果指令发送后提示被去重，则可能是QQ开放平台侧的问题，请等1分钟左右再重试一次" + "\n" + \
                   "=========================="
        
        await post_group_message(client, message, contents)
        return

    if msg == '/steam' or msg == '/steam ' or msg == 'steam' or msg == 'steam ':
        contents = "\n=======Steam账户查询=======" + "\n" + \
                   "/steam [昵称/ID] - 查询指定Steam账户信息" + "\n" + \
                   "=======================" + "\n" + \
                   "使用示例: /steam 114514" + "\n" + \
                   "注:如果指令发送后无返回且无获取错误信息，可能是请求出错或服务器错误，请重试或寻找管理员" + "\n" + \
                   "如果指令发送后提示被去重，则可能是QQ开放平台侧的问题，请等1分钟左右再重试一次" + "\n" + \
                   "======================="
        
        await post_group_message(client, message, contents)
        return

    # ------------------------------------功能区域------------------------------------
    if msg.startswith("/atinfo") or msg.startswith("atinfo"):
        info = await get_system_info()
        content = "\nAxTBot Public v" + str(client.get_version()) + "\n" + \
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

        await post_group_message(client, message, content)
        return
        
    if msg.startswith("/hyp") or msg.startswith("hyp"):
        await post_group_message(client, message, content="\n" + await get_hypixel_info(msg, message.id))
        return

    if msg.startswith(("/mc ","mc ")) and len(msg.split(" ")) > 1:
        player_name = msg.split(" ")[1]
        uuid = await get_minecraft_uuid(player_name)
        if uuid is None:
            await post_group_message(client, message, '未查询到该玩家的信息')
            return
        history_info = await get_player_history(uuid)
        if history_info is None:
            formatted_history = "\n".join([f"{name} - {changed_at}" for name, changed_at in history_info.items()])
        else:
            formatted_history = "未查询到当前玩家的历史用户名信息"
        contents = f"\n===Minecraft玩家查询===\n| 玩家名: {player_name}\n| UUID: {uuid}\n===历史用户名===\n{formatted_history}"
        await post_group_message(client, message, contents)
        return

    async def post_minecraft_image(client, message, avatar_type, content):
        player_name = msg.split(" ")[1]
        uuid = await get_minecraft_uuid(player_name)
        if uuid is None:
            await post_group_message(client, message, content='未查询到该玩家的信息')
            return
        image_url = f"https://crafatar.com/{avatar_type}{uuid}"
        await post_group_file(client, image_url)
        return

    if msg.startswith(("/mchead ","mchead ")) and len(msg.split(" ")) > 1:
        await post_minecraft_image(client, message, "avatars/", "未查询到该玩家的信息")
        return
    
    if msg.startswith(("/mcbody ","mcbody ")) and len(msg.split(" ")) > 1:
        await post_minecraft_image(client, message, "renders/body/", "未查询到该玩家的信息")
        return

    if msg.startswith(("/mcskin ","mcskin ")) and len(msg.split(" ")) > 1:
        await post_minecraft_image(client, message, "skins/", "未查询到该玩家的信息")
        return

    if msg.startswith(("/ipinfo ","ipinfo ")) and msg.split(" ")[1] is not None:
        info = await get_ip_info(msg.split(" ")[1])
        if info is None:
            await post_group_message(client, message, content='未查询到该IP的信息')
            return
        else:
            content = "\n=====IP信息=====" + "\n" + \
                      "IP: " + info["ip"] + "\n" + \
                      "| 开始 IP: " + info["start_ip"] + "\n" + \
                      "| 结束 IP: " + info["end_ip"] + "\n" + \
                      "| 归属地: " + info["country"] + " " + info["region"] + "\n" + \
                      "| 纬度: " + str(info["latitude"]) + "\n" + \
                      "| 经度: " + str(info["longitude"]) + "\n" + \
                      "| LLC: " + info["company"] + "\n" + \
                      "| ASN: " + 'AS' + str(info["asn"]) + "\n" + \
                      "=============="

        await post_group_message(client, message, content)
        return

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
                await post_group_message(client, message, content='未查询到该IP地址')
                return
        elif node == "hk":
            try:
                info = await get_ping_info(msg.split(" ")[1], "hk")
                checkpoint = "中国香港/腾讯云"
            except TypeError as e:
                await post_group_message(client, message, content='未查询到该IP地址')
                return

        content = "\n=====Ping信息=====" + "\n" + \
                  "主机名: " + info["host"].replace('.',',') + "\n" + \
                  "| IP: " + info["ip"] + "\n" + \
                  "| 最大延迟: " + str(info["max"]) + " ms\n" + \
                  "| 平均延迟: " + str(info["avg"]) + " ms\n" + \
                  "| 最小延迟: " + str(info["min"]) + " ms\n" + \
                  "| 归属地: " + str(info["location"]) + "\n" + \
                  "| 检测点: " + checkpoint + "\n" + \
                  "=============="

        await post_group_message(client, message, content)
        return

    if msg.startswith(("/whois ","whois ")) and msg.split(" ")[1] is not None:
        info = await get_whois_info(msg.split(" ")[1])
        if info is None:
            await post_group_message(client, message, content="未查询到该域名信息或暂不支持查询该格式")
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

        await post_group_message(client, message, content)
        return

    if msg.startswith(("/hotlist ","hotlist ")) and msg.split(" ")[1] is not None:
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
            await post_group_message(client, message, content='未查询到该热搜信息')
            return
        else:
            content = "\n===" + hot_type + "===" + "\n" + \
                      format_hot_search(hot_list) + "\n" + \
                      "=============" + "\n" + \
                      hot_list["update_time"] + "\n" + \
                      "============="

        await post_group_message(client, message, content)
        return

    if msg.startswith(("/mcping ","mcping ")):
        await post_group_message(client, message, content=await mcping(msg))
        return

    if msg.startswith(("/ask ","ask ")) and msg.split(" ")[1] is not None:
        info = await get_answer_book()
        content = "\n" + info
        await post_group_message(client, message, content)
        return

    if msg in ["jrrp","/jrrp"]:
        content1, msgtype = await get_jrrp(message)
        if msgtype == 0:
            await post_group_message(client, message, content1)
            return
        elif msgtype == 2:
            try:
                await client.api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=msgtype,
                    content=" ",
                    markdown=content1,
                    msg_id=message.id
                )
                return
            except Exception as e:
                print(f"出现错误：{e}")
                return
        else:
            return
        return
    
    if msg.startswith(("/steam ","steam ")):
        result = await get_steamid_info(msg)
        await post_group_message(client, message, content=result)
        return
    
    if msg.startswith("/摸") or msg.startswith("摸"):
        if re.match(r"(?:/)?摸\s*(\d+)", msg):
            try:
                qqid = int(re.match(r"(?:/)?摸\s*(\d+)", msg).group(1))
            except ValueError:
                await post_group_message(client, message, "输入值有误，请输入QQ号。")
                return
            await post_group_file(client, await get_touch_url(qqid))
            return
        
    if msg.startswith(("/remake","remake")):
        result = '\n' + await remake(str(message.author.member_openid))
        await post_group_message(client, message, content=result)