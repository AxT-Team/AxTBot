from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Dict, Any, get_origin, get_args
from pathlib import Path
import os
from dotenv import load_dotenv

class FrameworkConfig(BaseModel):
    """框架核心配置"""

    # 机器人相关
    appid: str | int
    bot_secret: str

    # 插件相关
    plugins_dir: str = "plugins"
    disable_plugins: List[str] = Field(default_factory=list)
    
    # 性能相关
    command_timeout: int = 10
    max_workers: int = 4
    
    # 日志相关
    log_level: str = "INFO"
    log_dir: Optional[str] = "logs"
    
    # 开发调试
    debug: bool = False
    reload_on_change: bool = False
    
    class Config:
        env_prefix = "FRAMEWORK_"
        env_file = ".env"


class ConfigLoader:
    """配置加载器，管理框架核心配置和插件配置"""
    
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
        """将字符串环境变量值转换为对应 Python 类型"""
        if not isinstance(raw_val, str):
            return raw_val
        
        origin = get_origin(annotation)
        args = get_args(annotation)
        
        # 处理 Optional[X] = Union[X, None]
        if origin is not None:  # Union or List or Optional
            if origin is list or origin is List:
                inner_type = args[0] if args else str
                s = raw_val.strip()
                if s in ("[]", ""):
                    return []
                items = [x.strip() for x in s.strip("[]").split(",") if x.strip()]
                return [ConfigLoader._coerce_value(item, inner_type) for item in items]
            else:
                # 可能是 Union (Optional)，取第一个非 None 的类型
                for arg in args:
                    if arg is not type(None):
                        return ConfigLoader._coerce_value(raw_val, arg)
                return raw_val
        else:
            # 简单类型
            if annotation is bool or annotation == bool:
                return raw_val.lower() in ("true", "1", "yes")
            elif annotation is int or annotation == int:
                return int(raw_val)
            elif annotation is float or annotation == float:
                return float(raw_val)
            else:
                return raw_val
    
    def _auto_init(self):
        """从 .env 文件和系统环境变量自动预加载配置"""
        for env_file in ("local.env", ".env"):
            if Path(env_file).exists():
                load_dotenv(env_file)
                break
        
        # 1. 收集带 FRAMEWORK_ 前缀的环境变量 → 去掉前缀，小写
        for key, value in os.environ.items():
            if key.startswith("FRAMEWORK_"):
                raw_key = key[len("FRAMEWORK_"):].lower()
                self._raw_data[raw_key] = value
        
        # 2. 收集其他环境变量（给插件用），保留原始大小写
        framework_fields_lower = {f.lower() for f in FrameworkConfig.model_fields}
        for key, value in os.environ.items():
            if key.startswith("FRAMEWORK_"):
                continue  # 已经处理过
            # 跳过已经是框架字段的（避免覆盖）
            if key.lower() in framework_fields_lower:
                if key.lower() not in self._raw_data:
                    self._raw_data[key.lower()] = value
                continue
            # 插件配置，保留原始 key
            self._raw_data[key] = value
        
        # 类型转换
        _converted = {}
        for field_name, field_info in FrameworkConfig.model_fields.items():
            if field_name in self._raw_data:
                _converted[field_name] = self._coerce_value(
                    self._raw_data[field_name], 
                    field_info.annotation
                )
        
        try:
            self._core_config = FrameworkConfig.model_validate(_converted)
        except ValidationError:
            pass

    
    def load(
        self, 
        env_file: str = ".env", 
        extra_config: Dict[str, Any] = None,
        **kwargs
    ):
        """加载配置（加载 .env 文件并合并覆盖）"""
        if Path(env_file).exists():
            load_dotenv(env_file)
        
        # 1. 收集带 FRAMEWORK_ 前缀的环境变量
        for key, value in os.environ.items():
            if key.startswith("FRAMEWORK_"):
                raw_key = key[len("FRAMEWORK_"):].lower()
                self._raw_data[raw_key] = value
        
        # 2. 收集其他环境变量（给插件用）
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
                _converted[field_name] = self._coerce_value(
                    self._raw_data[field_name],
                    field_info.annotation
                )
        
        try:
            self._core_config = FrameworkConfig.model_validate(_converted)
        except ValidationError as e:
            raise ValueError(f"框架核心配置校验失败: {e}") from e
        
        return self._core_config

    
    def get_core_config(self) -> FrameworkConfig:
        """获取框架核心配置"""
        if self._core_config is None:
            raise RuntimeError(
                "配置尚未加载，请先调用 config.load() 或确保设置了环境变量 "
                "(APPID/FRAMEWORK_APPID, BOT_SECRET/FRAMEWORK_BOT_SECRET)"
            )
        return self._core_config
    
    def get_raw_data(self) -> Dict[str, Any]:
        """获取所有原始配置数据（给插件用）"""
        return self._raw_data
    
    def __getattr__(self, name):
        if self._core_config is None:
            raise AttributeError(f"ConfigLoader 没有属性 '{name}'，配置尚未加载")
        return getattr(self._core_config, name, None)


# 全局单例
config_loader = ConfigLoader()
