"""
Module for Database Management and Operations in AxTBot

Author: Shanshui2024 & 猫娘工程师幽浮（AI）
Organization: AxT-Team
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.orm import sessionmaker

class User(SQLModel, table=True):
    """
    User model representing a user in the database.
    """
    id: int | None = Field(default=None, primary_key=True)
    user_openid: str
    message: int | None = None
    create_time: str
    update_time: str | None = None

class Group(SQLModel, table=True):
    """
    Group model representing a group in the database.
    """
    id: int | None = Field(default=None, primary_key=True)
    group_id: str
    message: int | None = None
    create_time: str
    update_time: str | None = None

class FrameConfig(SQLModel, table=True):
    """
    FrameConfig model representing a frame configuration in the database.
    """
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
        self.create_all()

    def create_all(self) -> None:
        """Create database tables for all SQLModel models."""
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        from app.modules import logger
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
            logger.debug(f"Database commit successful.")
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}! Rolling back ...")
            raise
        finally:
            session.close()

    def add_user(self, user: User) -> User:
        """Add a User record to the database."""
        with self.get_session() as session:
            session.add(user)
            session.flush()
            session.refresh(user)
            return user

    def get_user_by_openid(self, user_openid: str) -> User | None:
        """Fetch a user by openid."""
        with self.get_session() as session:
            return session.exec(select(User).where(User.user_openid == user_openid)).first()

    def list_users(self) -> list[User]:
        """Return all users."""
        with self.get_session() as session:
            return session.exec(select(User)).all()

    def add_group(self, group: Group) -> Group:
        """Add a Group record to the database."""
        with self.get_session() as session:
            session.add(group)
            session.flush()
            session.refresh(group)
            return group

    def get_group_by_id(self, group_id: str) -> Group | None:
        """Fetch a group by group_id."""
        with self.get_session() as session:
            return session.exec(select(Group).where(Group.group_id == group_id)).first()

    def list_groups(self) -> list[Group]:
        """Return all groups."""
        with self.get_session() as session:
            return session.exec(select(Group)).all()

    def add_frame_config(self, config: FrameConfig) -> FrameConfig:
        """Add a FrameConfig record to the database."""
        with self.get_session() as session:
            session.add(config)
            session.flush()
            session.refresh(config)
            return config

    def get_frame_config_by_key(self, key: str) -> FrameConfig | None:
        """Fetch a frame config by key."""
        with self.get_session() as session:
            return session.exec(select(FrameConfig).where(FrameConfig.key == key)).first()

    def list_frame_configs(self) -> list[FrameConfig]:
        """Return all frame configs."""
        with self.get_session() as session:
            return session.exec(select(FrameConfig)).all()

    def update_frame_config(self, key: str, value: str, operator: str = "Console") -> FrameConfig | None:
        """Update a frame config by key."""
        with self.get_session() as session:
            config = session.exec(select(FrameConfig).where(FrameConfig.key == key)).first()
            if config:
                config.value = value
                config.operator = operator
                config.update_time = "2026-05-04 00:00:00"  # 示例时间戳
                session.add(config)
                return config
            return None

# singleton manager for import convenience
_db_instance = None

def get_db() -> DataBaseManager:
    """Get the singleton database manager instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DataBaseManager()
    return _db_instance

# For backward compatibility, provide db as a property
class _DBProxy:
    def __getattr__(self, name):
        return getattr(get_db(), name)

db = _DBProxy()