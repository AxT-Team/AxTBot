"""
Module for Config File Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv("local.env")

class Config(BaseModel):
    """
    Config Class for AxTBot

    Attributes:
        appid (str): The App ID for the bot
        botsecret (str): The Secret Key for the bot
        plugins_dir (str): The Plugins Folder for the frame
    """
    appid: str
    botsecret: str
    plugins_dir: str = "plugins"

config = Config(
    appid=os.getenv("APPID"), 
    botsecret=os.getenv("BOT_SECRET"),
    plugins_dir=os.getenv("PLUGINS_DIR", "plugins"))