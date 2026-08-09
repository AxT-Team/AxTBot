from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, get_args, get_origin

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError


class FrameworkConfig(BaseModel):
    """框架核心配置"""

    appid: str | int
    bot_secret: str

    plugins_dir: str = "plugins"
    disable_plugins: List[str] = Field(default_factory=list)

    command_timeout: int = 10
    max_workers: int = 4

    log_level: str = "INFO"
    log_dir: Optional[str] = "logs"

    host: str = "0.0.0.0"
    port: int = 8000

    debug: bool = False
    reload_on_change: bool = False

    class Config:
        env_prefix = "FRAMEWORK_"
        env_file = ".env"


class ConfigLoader:
    """配置加载器，管理框架核心配置和插件配置。"""

    _instance = None
    _core_config: FrameworkConfig = None
    _raw_data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._auto_init()
        return cls._instance

    @staticmethod
    def _coerce_value(raw_val: str, annotation) -> Any:
        if not isinstance(raw_val, str):
            return raw_val

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is not None:
            if origin is list or origin is List:
                inner_type = args[0] if args else str
                s = raw_val.strip()
                if s in ("[]", ""):
                    return []
                items = [x.strip() for x in s.strip("[]").split(",") if x.strip()]
                return [ConfigLoader._coerce_value(item, inner_type) for item in items]
            for arg in args:
                if arg is not type(None):
                    return ConfigLoader._coerce_value(raw_val, arg)
            return raw_val

        if annotation is bool or annotation == bool:
            return raw_val.lower() in ("true", "1", "yes")
        if annotation is int or annotation == int:
            return int(raw_val)
        if annotation is float or annotation == float:
            return float(raw_val)
        return raw_val

    def _auto_init(self):
        for env_file in ("local.env", ".env"):
            if Path(env_file).exists():
                load_dotenv(env_file)
                break

        for key, value in os.environ.items():
            if key.startswith("FRAMEWORK_"):
                raw_key = key[len("FRAMEWORK_") :].lower()
                self._raw_data[raw_key] = value

        framework_fields_lower = {f.lower() for f in FrameworkConfig.model_fields}
        for key, value in os.environ.items():
            if key.startswith("FRAMEWORK_"):
                continue
            if key.lower() in framework_fields_lower:
                if key.lower() not in self._raw_data:
                    self._raw_data[key.lower()] = value
                continue
            self._raw_data[key] = value

        _converted = {}
        for field_name, field_info in FrameworkConfig.model_fields.items():
            if field_name in self._raw_data:
                _converted[field_name] = self._coerce_value(self._raw_data[field_name], field_info.annotation)

        try:
            self._core_config = FrameworkConfig.model_validate(_converted)
        except ValidationError:
            pass

    def load(
        self,
        env_file: str = ".env",
        extra_config: Dict[str, Any] = None,
        **kwargs,
    ):
        if Path(env_file).exists():
            load_dotenv(env_file)

        for key, value in os.environ.items():
            if key.startswith("FRAMEWORK_"):
                raw_key = key[len("FRAMEWORK_") :].lower()
                self._raw_data[raw_key] = value

        framework_fields_lower = {f.lower() for f in FrameworkConfig.model_fields}
        for key, value in os.environ.items():
            if key.startswith("FRAMEWORK_"):
                continue
            if key.lower() in framework_fields_lower:
                if key.lower() not in self._raw_data:
                    self._raw_data[key.lower()] = value
                continue
            self._raw_data[key] = value

        if extra_config:
            self._raw_data.update(extra_config)

        _converted = {}
        for field_name, field_info in FrameworkConfig.model_fields.items():
            if field_name in self._raw_data:
                _converted[field_name] = self._coerce_value(self._raw_data[field_name], field_info.annotation)

        try:
            self._core_config = FrameworkConfig.model_validate(_converted)
        except ValidationError as e:
            raise ValueError(f"框架核心配置校验失败: {e}") from e

        return self._core_config

    def get_core_config(self) -> FrameworkConfig:
        if self._core_config is None:
            raise RuntimeError(
                "配置尚未加载，请先调用 config.load() 或确保设置了环境变量 "
                "(APPID/FRAMEWORK_APPID, BOT_SECRET/FRAMEWORK_BOT_SECRET)"
            )
        return self._core_config

    def get_raw_data(self) -> Dict[str, Any]:
        return self._raw_data

    def __getattr__(self, name):
        if self._core_config is None:
            raise AttributeError(f"ConfigLoader 没有属性 '{name}'，配置尚未加载")
        return getattr(self._core_config, name, None)


config_loader = ConfigLoader()
