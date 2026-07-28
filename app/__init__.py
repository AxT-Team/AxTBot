"""
Entry File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""
import asyncio, threading
try:
    from app.service.qq_service.AccessToken import get_access_token
    def run_async_in_thread():
        asyncio.run(get_access_token())

    thread1 = threading.Thread(target=run_async_in_thread, name="AccessTokenThread", daemon=True)
    thread1.start()
except Exception as e:
    print("框架 >>> 未加载QQ服务框架，主框架将以终端模式运行")