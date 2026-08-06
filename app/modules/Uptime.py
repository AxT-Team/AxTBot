"""
Module for Framework Uptime Calculation

Author: Shanshui2024
Organization: AxT-Team

从数据库读取启动时间戳，计算并返回运行时长字符串。
"""
import time

from app.modules.DataBase import get_db


def get_uptime() -> str:
    """
    返回框架自启动以来的运行时长。

    Returns:
        str: 形如 "3天 2小时 15分 42秒" 或 "0秒"（刚启动时）
             若启动时间未记录则返回 "未知"
    """
    db = get_db()
    config = db.get_frame_config_by_key("startup_time")
    if not config:
        return "未知"

    try:
        startup_ts = int(config.value)
    except (ValueError, TypeError):
        return "未知"

    elapsed = int(time.time()) - startup_ts
    if elapsed < 0:
        return "0秒"

    days = elapsed // 86400
    hours = (elapsed % 86400) // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60

    parts: list[str] = []
    if days > 0:
        parts.append(f"{days}天")
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}秒")

    return " ".join(parts)
