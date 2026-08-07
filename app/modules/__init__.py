"""
Entry File for Client Modules

Author: Shanshui2024
Organization: AxT-Team
"""
from app.modules.DataBase import User, Group, FrameConfig, get_db
from app.modules.DataBase import db as database
from app.modules.Logger import logger
from app.modules.Config import get_plugin_config, config_loader
from app.modules.MsgProcesser import handlers, on_command, on_message, on_interaction, on_all_message
from app.modules.PluginManager import dispatch, PluginManager as PM, metadata_registry
from app.modules.Uptime import get_uptime
from app.modules.MessageCounter import counter

__all__ = ["database", "User", "Group", "FrameConfig", "logger", "get_plugin_config", "config_loader", "get_db", "get_uptime", "counter", "handlers", "metadata_registry", "on_all_message", "dispatch", "PM", "on_command", "on_message", "on_interaction"]
