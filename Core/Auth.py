import nacl.signing
import nacl.encoding
import nacl.bindings
import nacl.exceptions
from fastapi import Request, HTTPException
import time
import requests
import json
import threading
from Core.Logger import logger
from datetime import timedelta

# 从 QQ 机器人控制台获取的 Bot Secret
BOT_SECRET = "您的BOTSecret"

# 从 QQ 机器人控制台获取的 App ID 和 Client Secret
APP_ID = "您的APPID"
# 全局变量存储 access_token 和过期时间
access_token = None
expires_at = 0

start_time = None

# 验证签名
def verify_signature(bot_secret: str, signature_hex: str, timestamp: str, http_body: bytes) -> bool:
    seed = bot_secret.encode("utf-8")
    while len(seed) < nacl.bindings.crypto_sign_SEEDBYTES:
        seed += seed
    seed = seed[:nacl.bindings.crypto_sign_SEEDBYTES]
    signing_key = nacl.signing.SigningKey(seed)
    verify_key = signing_key.verify_key

    msg = timestamp.encode("utf-8") + http_body
    try:
        signature = nacl.encoding.HexEncoder.decode(signature_hex)
        verify_key.verify(msg, signature)
        return True
    except nacl.exceptions.BadSignatureError:
        return False

# 生成签名
def generate_signature(bot_secret: str, plain_token: str, event_ts: str) -> str:
    seed = bot_secret.encode("utf-8")
    while len(seed) < nacl.bindings.crypto_sign_SEEDBYTES:
        seed += seed
    seed = seed[:nacl.bindings.crypto_sign_SEEDBYTES]
    signing_key = nacl.signing.SigningKey(seed)

    msg = event_ts.encode("utf-8") + plain_token.encode("utf-8")
    signed_msg = signing_key.sign(msg)
    signature = signed_msg.signature.hex()
    logger.debug(f"框架 >>> 生成签名: {signature}")
    return signature

# 验证回调请求
async def validate_callback(request: Request):
    signature_hex = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    http_body = await request.body()

    if not verify_signature(BOT_SECRET, signature_hex, timestamp, http_body):
        raise HTTPException(status_code=401, detail="Invalid signature")
# 获取 access_token 的函数
def get_access_token(app_id: str, client_secret: str) -> dict:
    url = "https://bots.qq.com/app/getAppAccessToken"
    headers = {"Content-Type": "application/json"}
    data = {"appId": app_id, "clientSecret": client_secret}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"框架 >>> 获取 access token 失败: {response.text}")
        raise Exception(f"Failed to get access token: {response.text}")

# 守护线程函数
def token_refresh_thread(app_id: str, client_secret: str):
    global access_token, expires_at, start_time
    start_time = time.time()
    while True:
        try:
            # 获取新的 access_token
            response = get_access_token(app_id, client_secret)
            access_token = response["access_token"]
            expires_in = int(response["expires_in"])
            expires_at = time.time() + int(expires_in) - 45  # 提前45s刷新 / 详见：https://bot.q.qq.com/wiki/develop/api-v2/dev-prepare/interface-framework/api-use.html#%E8%8E%B7%E5%8F%96%E8%B0%83%E7%94%A8%E5%87%AD%E8%AF%81
            logger.debug(f"框架 >>> Access token 已刷新: {access_token}, 将于 {expires_in} s 后过期")
        except Exception as e:
            logger.error(f"框架 >>> 刷新 access token 失败: {e}")
            raise e
        wait_time = expires_at - time.time() # 等待时间
        if wait_time > 0:
            time.sleep(wait_time)
        else:
            logger.warning("框架 >>> Access token 已失效...立即获取新token")
            pass

def start_token_refresh(app_id: str, client_secret: str):
    thread = threading.Thread(target=token_refresh_thread, args=(app_id, client_secret))
    thread.daemon = True  # 设置为守护线程
    thread.start()
    logger.debug("框架 >>> Access Token刷新线程启动")

def get_current_access_token():
    if access_token is None or time.time() >= expires_at:
        raise Exception("Access token is not available or has expired.")
    return access_token


def format_timedelta(delta: timedelta) -> str:
    """
    将 timedelta 对象格式化为 'XX天 XX时 XX分 XX秒' 的字符串
    """
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}天 {hours:02d}时 {minutes:02d}分 {seconds:02d}秒"

def get_current_run_time(string_out: bool = True) -> timedelta or str:
    """
    获取当前运行时间

    Args:
        string_out (bool): 是否返回格式化后的字符串。默认为 True，返回格式化后的字符串。
                           如果设置为 False，则返回 timedelta 对象。

    Returns:
        timedelta or str: 根据 string_out 参数返回 timedelta 对象或格式化后的字符串。
    """
    global start_time
    if start_time is None:
        start_time = time.time()
    now = time.time()
    elapsed_time = timedelta(seconds=int(now - start_time))

    if string_out:
        return format_timedelta(elapsed_time)
    else:
        return elapsed_time