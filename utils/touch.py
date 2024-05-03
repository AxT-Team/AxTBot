import json
import requests

# ------------------快速设置------------------
api_url = "https://api.wer.plus/api/ruad?url=" # 请修改成你的API
menu = '''使用方法:
/摸 QQ号''' # 如果只是/摸 时，发送这段消息
# ----------------快速设置结束-----------------

# ----------------主程序-----------------
async def touch(qqid) -> None:
    if qqid == "help":
        return menu
    else:
        api = api_url+ f"https://qlogo4.store.qq.com/qzone/{qqid}/{qqid}/100"
        response = requests.get(api)
        message = json.loads(response.text)
        return message['url']
