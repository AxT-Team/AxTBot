"""
Class for Session Management and Operations in Message Context

Author: Shanshui2024 & DeepSeek V4
Organization: AxT-Team
"""

import asyncio, time

class Session:
    def __init__(self, session_id, timeout=60):
        self.session_id = session_id
        self.timeout = timeout
        self.future = asyncio.Future()
        self.data = {}  # 存储临时数据
        self.create_time = time.time()

    async def wait_for_message(self):
        """等待用户回复，超时抛出 TimeoutError"""
        try:
            return await asyncio.wait_for(self.future, timeout=self.timeout)
        except asyncio.TimeoutError:
            raise TimeoutError("会话超时")

    def resolve(self, message):
        """当收到消息时，唤醒等待的协程"""
        if not self.future.done():
            self.future.set_result(message)

class SessionManager:
    _sessions = {}

    @classmethod
    def create(cls, session_id, timeout=60):
        """创建新会话，如果已存在则覆盖"""
        cls._sessions[session_id] = Session(session_id, timeout)
        return cls._sessions[session_id]

    @classmethod
    def get(cls, session_id):
        return cls._sessions.get(session_id)

    @classmethod
    def remove(cls, session_id):
        cls._sessions.pop(session_id, None)

    @classmethod
    async def cleanup(cls):
        """定期清理超时会话"""
        now = time.time()
        for sid, sess in list(cls._sessions.items()):
            if now - sess.create_time > sess.timeout:
                if not sess.future.done():
                    sess.future.set_exception(TimeoutError("会话已超时"))
                cls.remove(sid)