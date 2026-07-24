"""
Entry File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""
import asyncio, threading

from app.service.AccessToken import get_access_token

def run_async_in_thread():
    asyncio.run(get_access_token())

thread1 = threading.Thread(target=run_async_in_thread, name="AccessTokenThread", daemon=True)
thread1.start()