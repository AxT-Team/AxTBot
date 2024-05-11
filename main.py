from datetime import datetime

import botpy
import toml
from botpy import logging
from botpy.message import DirectMessage, GroupMessage, C2CMessage, Message

from group_event.c2c_message_create import handle_c2c_message_create
from group_event.group_at_message_create import handle_group_at_message_create
from guild_event.guild_at_message_create import handle_guild_at_message_create
from guild_event.guild_c2c_message_create import handle_guild_c2c_message_create

_log = logging.get_logger()


class AxTBot(botpy.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 定义Bot版本
        self.version = "1.2"

        # 初始化计时器
        self.start_time = datetime.now()

        # 初始化消息计数器
        self.group_message_number = 0
        self.friend_message_number = 0
        self.guild_group_message_number = 0
        self.guild_friend_message_number = 0

    # 获取运行时间
    def get_run_time(self):
        current_time = datetime.now()
        elapsed = current_time - self.start_time
        seconds = elapsed.total_seconds()

        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)

        return f"{days}天 {hours}时 {minutes}分 {seconds}秒"

    def get_version(self):
        return self.version

    def get_group_message_number(self):
        return self.group_message_number

    def get_friend_message_number(self):
        return self.friend_message_number

    def get_guild_group_message_number(self):
        return self.guild_group_message_number

    def get_guild_friend_message_number(self):
        return self.guild_friend_message_number

    # 公域 | 原生 | 群聊at消息
    async def on_group_at_message_create(self, message: GroupMessage):
        self.group_message_number += 1
        await handle_group_at_message_create(self, message)

        # await self.handle_at_message.send_message(message)

    # 公域 | 原生 | 私聊消息
    async def on_c2c_message_create(self, message: C2CMessage):
        self.friend_message_number += 1
        await handle_c2c_message_create(self, message)

        # await self.handle_at_message.send_message(message)

    # 公域 | 频道 | at消息
    async def on_at_message_create(self, message: Message):
        self.guild_group_message_number += 1
        await handle_guild_at_message_create(self, message)

        # await self.handle_at_message.send_message(message)

    # 公域 | 频道 | 私聊消息
    async def on_direct_message_create(self, message: DirectMessage):
        self.guild_friend_message_number += 1
        await handle_guild_c2c_message_create(self, message)

        # await self.handle_at_message.send_message(message)


def run_client(appid, secret, sandbox):
    intents = botpy.Intents(
        public_messages=True,
        public_guild_messages=True,
        direct_message=True,
        guilds=True,
        guild_message_reactions=True,
        guild_messages=False,
        guild_members=False,
        interaction=False,
        message_audit=True
    )
    AxTBot(intents=intents, is_sandbox=sandbox).run(appid=appid, secret=secret)


if __name__ == '__main__':
    appid = toml.load("config.toml")['robot']['appid']
    secret = toml.load("config.toml")['robot']['secret']
    if toml.load("config.toml")['robot']['sandbox'] == "True":
        sandbox = True
    elif toml.load("config.toml")['robot']['sandbox'] == "False":
        sandbox = False
    run_client(appid, secret, sandbox)