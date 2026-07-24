"""
Class File For Plugin Model

Author: Shanshui2024
Organization: AxT-Team
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class PluginMeta:
    """插件元信息"""
    name: str
    version: str
    author: str
    description: str = ""
    dependencies: list[str] = field(default_factory=list)

class PluginBase(ABC):
    """所有插件必须继承的基类"""
    
    def __init__(self):
        self.meta: Optional[PluginMeta] = None
        self.context: Optional[Dict[str, Any]] = None
        self._is_running = False
    
    @abstractmethod
    def initialize(self, context: Dict[str, Any]) -> bool:
        """初始化插件，返回是否成功"""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """核心执行逻辑"""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """释放资源"""
        pass
    
    def get_meta(self) -> PluginMeta:
        """返回插件元信息，子类可重写"""
        return self.meta or PluginMeta(
            name=self.__class__.__name__,
            version="1.0.0",
            author="Unknown"
        )