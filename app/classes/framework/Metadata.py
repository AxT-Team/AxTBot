"""
Class file for Plugin Metadata

Author: Shanshui2024
Organization: AxT-Team
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str = ""
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    priority: int = 10  # 默认中等优先级
    module_name: str = ""
    
    def __post_init__(self):
        # 自动校验版本格式
        if not self.version.replace(".", "").isdigit():
            raise ValueError(f"版本号 {self.version} 格式不合法，请使用 '1.0.0' 格式")