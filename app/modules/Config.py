from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Type, TypeVar

import os
from dotenv import dotenv_values
from pydantic import BaseModel, ValidationError

from app.classes.framework.FConfig import config_loader


class GlobalConfig:
    """全局配置对象，存储所有配置项。"""

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def load_from_env(self, env_file: str = ".env"):
        """从 .env 文件加载，并回退到系统环境变量。"""
        self._data.update(os.environ)
        if Path(env_file).exists():
            self._data.update({key: value for key, value in dotenv_values(env_file).items() if value is not None})

    def load_from_dict(self, data: Dict[str, Any]):
        self._data.update(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data


global_config = GlobalConfig()

T = TypeVar("T", bound=BaseModel)


def get_plugin_config(
    config_model: Type[T],
    prefix: str | None = None,
    strip_prefix: bool = True,
) -> T:
    """从框架的统一配置中提取插件配置。"""
    raw = config_loader.get_raw_data().copy()

    if prefix:
        prefix_lower = prefix.lower()
        filtered = {}
        for key, value in raw.items():
            if key.lower().startswith(prefix_lower):
                new_key = key[len(prefix) :] if strip_prefix else key
                filtered[new_key.lower()] = value
        raw = filtered

    try:
        return config_model.model_validate(raw)
    except ValidationError as e:
        raise ValueError(f"插件配置校验失败: {e}") from e
