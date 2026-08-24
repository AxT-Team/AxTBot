"""
Module for Database Management and Operations in AxTBot

Author: Shanshui2024 & 猫娘工程师幽浮（AI） & DeepSeek V4
Organization: AxT-Team
"""
from __future__ import annotations
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, TypeVar, Type
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.orm import sessionmaker

# 类型变量
T = TypeVar('T', bound=SQLModel)


class User(SQLModel, table=True):
    """User model representing a user in the database."""
    id: int | None = Field(default=None, primary_key=True)
    user_openid: str
    message: int | None = None
    create_time: str
    update_time: str | None = None
    nickname: str | None = None


class Group(SQLModel, table=True):
    """Group model representing a group in the database."""
    id: int | None = Field(default=None, primary_key=True)
    group_id: str
    group_openid: str | None = None
    group_name: str | None = None
    message: int | None = None
    member_count: int | None = None
    bot_joined_at: str | None = None
    bot_allow_proactive_msg: bool | None = None
    bot_recv_msg_setting: str | None = None
    bot_member_role: str | None = None
    state_synced_at: str | None = None
    create_time: str
    update_time: str | None = None


class FrameConfig(SQLModel, table=True):
    """FrameConfig model representing a frame configuration in the database."""
    id: int | None = Field(default=None, primary_key=True)
    key: str
    value: str
    create_time: str
    update_time: str | None = None
    operator: str = "Console"


class DataBaseManager:
    """ORM manager for thread-safe database access."""

    def __init__(self, db_url: str = "sqlite:///data/default.db", echo: bool = False):
        # 将相对路径的 SQLite 数据库解析为项目根目录下的绝对路径，避免受当前工作目录影响
        if db_url.startswith("sqlite:///"):
            db_path = db_url.removeprefix("sqlite:///")
            if not os.path.isabs(db_path):
                project_root = Path(__file__).resolve().parents[2]
                db_path = str(project_root / db_path)
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            db_url = f"sqlite:///{Path(db_path).as_posix()}"
        self.db_url = db_url
        self.engine = create_engine(
            db_url,
            echo=echo,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
            future=True,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=Session,
            autoflush=False,
            expire_on_commit=False,
            future=True,
        )
        SQLModel.metadata.create_all(self.engine)
        self._migrate_groups()

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            from app.modules import logger
            logger.error(f"Database error: {e}! Rolling back ...")
            raise
        finally:
            session.close()

    # ==================== 通用 CRUD 方法 ====================

    def _add(self, instance: T) -> T:
        """通用添加方法"""
        with self.get_session() as session:
            session.add(instance)
            session.flush()
            session.refresh(instance)
            return instance

    def _get_by_field(self, model: Type[T], field: str, value: str) -> T | None:
        """通用按字段查询方法"""
        with self.get_session() as session:
            return session.exec(select(model).where(getattr(model, field) == value)).first()

    def _list_all(self, model: Type[T]) -> list[T]:
        """通用查询所有记录方法"""
        with self.get_session() as session:
            return session.exec(select(model)).all()

    def _update(self, model: Type[T], field: str, up_value: str, **kwargs) -> T | None:
        """通用更新方法"""
        with self.get_session() as session:
            instance = session.exec(select(model).where(getattr(model, field) == up_value)).first()
            if instance:
                for key, val in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, val)
                session.add(instance)
                return instance
            return None

    # ==================== User 方法 ====================

    def add_user(self, user: User) -> User | None:
        """Add a User record to the database. Rejects if user_openid already exists."""
        existing = self.get_user_by_openid(user.user_openid)
        if existing:
            from app.modules import logger
            logger.warning(f"数据库 >>> 拒绝创建重复 User: user_openid='{user.user_openid}' 已存在，跳过创建")
            return None
        return self._add(user)

    def get_user_by_openid(self, user_openid: str) -> User | None:
        """Fetch a user by openid."""
        return self._get_by_field(User, "user_openid", user_openid)

    def list_users(self) -> list[User]:
        """Return all users."""
        return self._list_all(User)

    def update_user(self, user: User) -> User | None:
        """Update a user record."""
        return self._update(
            User, "user_openid", user.user_openid,
            message=user.message,
            update_time=user.update_time,
            nickname=user.nickname
        )

    # ==================== Group 方法 ====================

    def add_group(self, group: Group) -> Group | None:
        """Add a Group record to the database. Rejects if group_id already exists."""
        existing = self.get_group_by_id(group.group_id)
        if existing:
            from app.modules import logger
            logger.warning(f"数据库 >>> 拒绝创建重复 Group: group_id='{group.group_id}' 已存在，跳过创建")
            return None
        return self._add(group)

    def get_group_by_id(self, group_id: str) -> Group | None:
        """Fetch a group by group_id."""
        return self._get_by_field(Group, "group_id", group_id)

    def list_groups(self) -> list[Group]:
        """Return all groups."""
        return self._list_all(Group)

    def update_group(self, group: Group) -> Group | None:
        """Update a group record. Fields left as None are not overwritten."""
        data = {
            "group_openid": group.group_openid,
            "group_name": group.group_name,
            "message": group.message,
            "member_count": group.member_count,
            "bot_joined_at": group.bot_joined_at,
            "bot_allow_proactive_msg": group.bot_allow_proactive_msg,
            "bot_recv_msg_setting": group.bot_recv_msg_setting,
            "bot_member_role": group.bot_member_role,
            "state_synced_at": group.state_synced_at,
            "update_time": group.update_time,
        }
        return self._update(
            Group, "group_id", group.group_id,
            **{key: value for key, value in data.items() if value is not None},
        )

    # ==================== FrameConfig 方法 ====================

    def add_frame_config(self, config: FrameConfig) -> FrameConfig | None:
        """Add a FrameConfig record to the database. Rejects if key already exists."""
        existing = self.get_frame_config_by_key(config.key)
        if existing:
            from app.modules import logger
            logger.warning(f"数据库 >>> 拒绝创建重复 FrameConfig: key='{config.key}' 已存在，跳过创建")
            return None
        return self._add(config)

    def get_frame_config_by_key(self, key: str) -> FrameConfig | None:
        """Fetch a frame config by key."""
        return self._get_by_field(FrameConfig, "key", key)

    def list_frame_configs(self) -> list[FrameConfig]:
        """Return all frame configs."""
        return self._list_all(FrameConfig)

    def update_frame_config(self, key: str, key_value: str, update_time: int | None = None, operator: str = "Console") -> FrameConfig | None:
        """Update a frame config by key."""
        data = {
            "value": key_value,
            "operator": operator,
            "update_time": str(update_time)
        }
        return self._update(
            FrameConfig, "key", key,
            **data
        )


    def _migrate_groups(self) -> None:
        """为已存在的 group 表补齐新字段（SQLite 不支持自动 ALTER）。"""
        expected = {
            "group_openid": "TEXT",
            "group_name": "TEXT",
            "member_count": "INTEGER",
            "bot_joined_at": "TEXT",
            "bot_allow_proactive_msg": "INTEGER",
            "bot_recv_msg_setting": "TEXT",
            "bot_member_role": "TEXT",
            "state_synced_at": "TEXT",
        }
        table = Group.__tablename__
        try:
            with self.engine.connect() as conn:
                rows = conn.exec_driver_sql(f'PRAGMA table_info("{table}")').fetchall()
                existing = {r[1] for r in rows}
                for col, ctype in expected.items():
                    if col not in existing:
                        conn.exec_driver_sql(f'ALTER TABLE "{table}" ADD COLUMN {col} {ctype}')
                        conn.commit()
            from app.modules import logger

            logger.debug("数据库 >>> group 表迁移完成")
        except Exception as e:
            from app.modules import logger

            logger.error(
                f"数据库 >>> group 表迁移失败: {e}。"
                f"表结构与模型不一致，继续运行将导致所有群聊数据操作报错，已中止启动。"
            )
            raise


# ==================== 单例管理 ====================

_db_instance = None


def get_db() -> DataBaseManager:
    """Get the singleton database manager instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DataBaseManager()
    return _db_instance


class _DBProxy:
    """代理类，用于向后兼容 db 属性访问"""
    def __getattr__(self, name):
        return getattr(get_db(), name)


db = _DBProxy()