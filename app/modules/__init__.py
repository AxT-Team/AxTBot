"""
Entry File for Client Modules

Author: Shanshui2024
Organization: AxT-Team
"""
from app.modules.DataBase import User, Group, FrameConfig, get_db
from app.modules.DataBase import db as database
from app.modules.Logger import logger
from app.modules.Config import config
from app.modules.MsgProcesser import handlers, on_command, on_message
from app.modules.PluginManager import dispatch, PluginManager as PM

__all__ = ["database", "User", "Group", "FrameConfig", "logger", "config", "get_db", "handlers", "dispatch", "PM", "on_command", "on_message"]
