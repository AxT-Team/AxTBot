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
from Core.Config import config
from datetime import timedelta


class Auth:
    def __init__(self, Bot_Secret: str, AppId: str):
        self.BOTSECRET = Bot_Secret
        self.APPID = AppId
        self.access_token = None
        self.expires_at = 0
        self.start_time = None

    def verify_signature(self, signature_hex: str, timestamp: str, http_body: bytes) -> bool:
        seed = self.BOTSECRET.encode("utf-8")
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

    def generate_signature(self, plain_token: str, event_ts: str) -> str:
        seed = self.BOTSECRET.encode("utf-8")
        while len(seed) < nacl.bindings.crypto_sign_SEEDBYTES:
            seed +=seed
        seed = seed[:nacl.bindings.crypto_sign_SEEDBYTES]
        signing_key = nacl.signing.SigningKey(seed)

        msg = event_ts.encode("utf-8") + plain_token.encode("utf-8")
        signed_msg = signing_key.sign(msg)
        signature = signed_msg.signature.hex()
        logger.debug(f"框架 >>> 生成签名: {signature}")
        return signature

    async def validate_callback(self, request: Request):
        signature_hex = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")
        http_body = await request.body()

        if not self.verify_signature(signature_hex, timestamp, http_body):
            raise HTTPException(status_code=401, detail="Invalid signature")

    def get_access_token(self) -> dict:
        url = "https://bots.qq.com/app/getAppAccessToken"
        headers = {"Content-Type": "application/json"}
        data = {"appId": self.APPID, "clientSecret": self.BOTSECRET}
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"框架 >>> 获取 access token 失败: {response.text}")
            raise Exception(f"Failed to access get token: {response.text}")

    def token_refresh_thread(self):
        self.start_time = time.time()
        while True:
            try:
                response = self.get_access_token()
                logger.debug(f'框架 >>> 获得返回内容：{response}')
                self.access_token = response["access_token"]
                expires_in = int(response["expires_in"])
                self.expires_at = time.time() + int(expires_in) - 45
                logger.debug(f"框架 >>> Access token 已刷新: {self.access_token}, 将于 {expires_in} s 后过期")
            except Exception as e:
                logger.error(f"框架 >>> 刷新 access token 失败: {e}")
                raise e
            wait_time = self.expires_at - time.time()
            if wait_time > 0:
                time.sleep(wait_time)
            else:
                logger.warning("框架 >>> Access token 已失效...立即获取新token")

    def start_token_refresh(self):
        thread = threading.Thread(target=self.token_refresh_thread)
        thread.daemon = True
        thread.start()
        logger.debug("框架 >>> Access Token刷新线程启动")

    def get_current_access_token(self):
        if self.access_token is None or time.time() >= self.expires_at:
            raise Exception("Access token is not available or has expired.")
        return self.access_token

    def format_timedelta(self, delta: timedelta) -> str:
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}天 {hours:02d}时 {minutes:02d}分 {seconds:02d}秒"

    def get_current_run_time(self, string_out: bool = True):
        if self.start_time is None:
            self.start_time = time.time()
        now = time.time()
        elapsed_time = timedelta(seconds=int(now - self.start_time))

        if string_out:
            return self.format_timedelta(elapsed_time)
        else:
            return elapsed_time


# 实例化 Auth 类
auth = Auth(config.bot_secret, str(config.appid))