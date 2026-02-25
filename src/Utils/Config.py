import yaml, asyncio
from pathlib import Path

from src.Utils.ConfigCli import load_config  # 导入配置加载函数
from src.Utils.ConfigClass import ConfigBase


asyncio.run(load_config(Path("config.yaml")))  # 确保配置已加载

def __init__ (self):
    """初始化配置"""
    self.load_config()  # 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    yaml_config = yaml.safe_load(f)

_config = ConfigBase(**yaml_config)

if _config.Advanced.debug:
    _config.Logger.level = "DEBUG"
else:
    _config.Logger.level = _config.Logger.level

config = _config