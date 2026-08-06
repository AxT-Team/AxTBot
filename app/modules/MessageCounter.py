"""
Module for In-Memory Message Statistics

Author: Shanshui2024
Organization: AxT-Team

每次框架重启后从 0 开始计数，分别统计群聊/私聊的收发消息数。
"""
from __future__ import annotations


class MessageCounter:
    """单例消息计数器，重启自动清零。"""

    def __init__(self):
        self.group_received: int = 0
        self.group_sent: int = 0
        self.private_received: int = 0
        self.private_sent: int = 0

    # ── 计数接口 ──

    def add_group_received(self, n: int = 1) -> None:
        self.group_received += n

    def add_group_sent(self, n: int = 1) -> None:
        self.group_sent += n

    def add_private_received(self, n: int = 1) -> None:
        self.private_received += n

    def add_private_sent(self, n: int = 1) -> None:
        self.private_sent += n

    # ── 查询接口 ──

    @property
    def total(self) -> int:
        """收发总数"""
        return self.group_received + self.group_sent + self.private_received + self.private_sent

    def get_stats(self) -> dict[str, int]:
        """返回各维度计数字典"""
        return {
            "group_received": self.group_received,
            "group_sent": self.group_sent,
            "private_received": self.private_received,
            "private_sent": self.private_sent,
            "total": self.total,
        }

    def get_summary(self) -> str:
        """返回人类可读的统计字符串"""
        return (
            f"📊 本轮统计 | "
            f"群收 {self.group_received} / 群发 {self.group_sent} | "
            f"私收 {self.private_received} / 私发 {self.private_sent}"
        )


# 全局单例
counter = MessageCounter()
