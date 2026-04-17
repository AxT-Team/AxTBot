"""
Entry File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""

from app.main import app
from app.service.AccessToken import get_access_token, shutdown_token_service
import asyncio, threading


def run_async_in_thread():
    asyncio.run(get_access_token())

thread = threading.Thread(target=run_async_in_thread, name="AccessTokenThread", daemon=True)
thread.start()

@app.on_event("shutdown")
def shutdown_event():
    shutdown_token_service()