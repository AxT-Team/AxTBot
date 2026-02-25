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
        """欢迎使用AxT社区机器人2.1.0
===============
| 在开始之前，请阅读以下协议和政策。
| 使用该机器人，即代表您同意将用户数据等上报团队进行数据分析。
| 请注意：AxT、思茶科技及相关团队不会对用户数据进行任何形式的修改、公开、分享、出售、转让，仅用于分析、生成报告等。
| 有关隐私数据：开放平台限制，用户隐私仅包含您上传的文本信息。
| 如果您对此有任何异议，请联系admin@axtrk,com。
===============
| 弧塔科技服务条款：https://www.axtrk.com/terms
| UApi 服务条款：https://uapis.cn/docs/getting-started/privacy-policy
| 思茶科技服务条款：https://sicha.ltd/axt_bot_terms/""")
