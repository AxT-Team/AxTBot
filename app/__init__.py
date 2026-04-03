"""
Entry File for the FastAPI Application

Author: Shanshui2024
Organization: AxT-Team
"""

from app.main import app
from app.service.AccessToken import get_access_token
import asyncio

asyncio.create_task(get_access_token())