from src.Utils.PluginBase import group_add
from src.Utils.Logger import logger
from src.Utils.EventClass import GroupEvent

__metadata__ = {
    "name": "[官方插件]进群提示服务协议和用户政策",
    "version": "1.0.0",
    "author": "AxT-Team",
    "description": "用来告知用户数据使用权",
    "official": True,
}


@group_add
async def handle_hello(event: GroupEvent) -> None:
    """处理群消息事件
    
    Args:
        event: 群消息事件对象
    """

    await event.reply(
        """欢迎使用AxT机器人2.1.0
===============
| 在开始之前，请务必阅读以下协议和用户政策。
| 继续使用机器人，即代表您同意将当前聊天环境对机器人的用户数据、信息等上报给AxT进行数据分析。
| 请注意：AxT将不会对用户数据进行任何的修改、公开、分享、出售、转让，仅用于分析用户数据，并生成报告等。
| 有关于隐私数据的使用：由于QQ开放平台限制，用户隐私仅包含您上传的富文本和文本信息。
| 如果您对此有任何异议，请联系admin@axtrk,com。
===============
| AxT服务条款：https://www.axtrk.com/terms
| 思茶科技服务条款：https://sicha.ltd/terms""")
