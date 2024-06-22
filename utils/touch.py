import json
import requests
import time

# ------------------快速设置------------------
api_url = "https://uapis.cn/api/mt.php?qq=" # 请修改成你的API
menu = '''使用方法:
/摸 QQ号''' # 如果只是/摸 时，发送这段消息
# ----------------快速设置结束-----------------

# ----------------主程序-----------------
async def touch(qqid) -> None:
    if qqid == "help":
        return menu
    elif qqid == "我":
        return "很抱歉，请直接输入您的QQ号。"
    else:
        try:
            qqid = int(qqid)
        except ValueError:
            return "输入值有误，请输入QQ号。"
        api = api_url+ str(qqid)
        return api