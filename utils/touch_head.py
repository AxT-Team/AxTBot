import json
import requests

# ------------------快速设置------------------
api_url = "https://api.wer.plus/api/ruad?url=" # 请修改成你的API
menu = '''使用方法:
/touch QQ号''' # 如果只是/touch 时，发送这段消息
# ----------------快速设置结束-----------------

# ----------------主程序-----------------
async def touch(qqid) -> None:
    api = api_url+ f"https://qlogo4.store.qq.com/qzone/{qqid}/{qqid}/100"
    response = requests.get(api)
    message = json.loads(response.text)
    return message['url']