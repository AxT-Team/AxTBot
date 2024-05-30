import json
import requests
import time

# ------------------快速设置------------------
api_url = "https://api.wer.plus/api/ruad?url=" # 请修改成你的API
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
        api = api_url+ f"https://qlogo4.store.qq.com/qzone/{qqid}/{qqid}/100"
        response = requests.get(api)
        message = json.loads(response.text)
        if message['code'] == 429:
            time.sleep(3)
            response = requests.get(api)
            message = json.loads(response.text)
        return message['data']['image_url']
