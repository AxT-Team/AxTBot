import json
import requests
import time

# ------------------快速设置------------------
api_url = "https://api.wer.plus/api/ruad?url=" # 请修改成你的API
menu = f'''使用方法:
/摸 QQ号
''' # 如果只是/摸 时，发送这段消息
# ----------------快速设置结束-----------------

# ----------------主程序-----------------
async def meme(qqid, type) -> None:
    try:
        int(qqid)
    except ValueError:
        return "请输入正确的QQ号。"
    else:
        if qqid == 1:
            return menu
        elif qqid == "我":
            return "很抱歉，由于技术限制，暂时不能这么用，请直接输入您的QQ号。"
        else:
            if type == "摸" or type == "touch":
                api = api_url+ f"https://qlogo4.store.qq.com/qzone/{qqid}/{qqid}/100"
                response = requests.get(api)
                message = json.loads(response.text)
                if message['code'] == 429:
                    time.sleep(3)
                    response = requests.get(api)
                    message = json.loads(response.text)
                return message['url']
            #暂未实现 吃
            elif type == "吃" or type == "eat":
                api = api_url+ f"https://qlogo4.store.qq.com/qzone/{qqid}/{qqid}/100"
                response = requests.get(api)
                message = json.loads(response.text)
                if message['code'] == 429:
                    time.sleep(3)
                    response = requests.get(api)
        
# ----------------主程序-----------------