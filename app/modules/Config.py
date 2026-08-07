"""
Module for Config File Management in AxTBot

Author: Shanshui2024
Organization: AxT-Team
"""
import os
from dotenv import dotenv_values
from typing import Any, Dict, Type, TypeVar
from pydantic import BaseModel, ValidationError
from app.classes.framework.FConfig import config_loader

class GlobalConfig:
    """全局配置对象，存储所有配置项"""
    def __init__(self):
        self._data: Dict[str, Any] = {}

    def load_from_env(self, env_file: str = ".env"):
        """从 .env 文件加载"""
        try:
            self._data.update(dotenv_values(env_file))
        except ImportError:
            # 如果没有 python-dotenv，就只读系统环境变量
            for key, value in os.environ.items():
                self._data[key] = value

    def load_from_dict(self, data: Dict[str, Any]):
        self._data.update(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

global_config = GlobalConfig()



T = TypeVar('T', bound=BaseModel)

def get_plugin_config(
    config_model: Type[T], 
    prefix: str = None,          # 可选前缀
    strip_prefix: bool = True    # 是否去掉前缀
) -> T:
    """
    从框架的统一配置中提取插件配置
    """
    raw = config_loader.get_raw_data().copy()
    
    if prefix:
        prefix_lower = prefix.lower()  # 统一小写比较
        filtered = {}
        for key, value in raw.items():
            if key.lower().startswith(prefix_lower):
                new_key = key[len(prefix):] if strip_prefix else key
                filtered[new_key.lower()] = value
        raw = filtered
    
    try:
        return config_model.model_validate(raw)
    except ValidationError as e:
        raise ValueError(f"插件配置校验失败: {e}") from e