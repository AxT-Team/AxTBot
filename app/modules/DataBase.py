"""
Module for Database Management and Operations in AxTBot

Author: Shanshui2024 & 猫娘工程师幽浮（AI） & DeepSeek V4
Organization: AxT-Team
"""
from __future__ import annotations
from contextlib import contextmanager
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
    message: int | None = None
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
        """Update a group record."""
        return self._update(
            Group, "group_id", group.group_id,
            message=group.message,
            update_time=group.update_time
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