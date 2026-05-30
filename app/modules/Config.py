"""
Module for Config File Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv("local.env")

class Config(BaseModel):
    """
    Config Class for AxTBot

    Attributes:
        appid (str): The App ID for the bot
        botsecret (str): The Secret Key for the bot
    """
    appid: str
    botsecret: str

config = Config(appid=os.getenv("APPID"), botsecret=os.getenv("BOT_SECRET"))