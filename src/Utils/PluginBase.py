import sys, os, importlib.util
from typing import Dict, Callable, Optional
from pathlib import Path

from src.Utils.Logger import logger
from src.Utils.Config import config


# 全局命令注册表
COMMAND_REGISTRY: Dict[str, Dict] = {}
# 全局加群事件注册表
GROUP_ADD_REGISTRY: Dict[str, Dict] = {}
FRIEND_ADD_REGISTRY: Dict[str, Dict] = {}
INTERACTION_REGISTRY: Dict[str, Dict] = {}
PLUGIN_DIR: Optional[str] = None

def command(names, event_type: type = None):
    """命令注册装饰器（支持多个命令名）
    
    Args:
        names: 命令名或命令名列表
        event_type: 支持的事件类型
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        # 确保 names 是列表类型
        name_list = [names] if isinstance(names, str) else names
        
        # 获取当前模块名，用于日志记录
        module_name = func.__module__
        
        for name in name_list:
            if name in COMMAND_REGISTRY:
                # 检查是否是同一个模块的命令
                existing_module = COMMAND_REGISTRY[name]['handler'].__module__
                if existing_module == module_name:
                    # 同一模块重复注册，直接覆盖
                    logger.debug(f"插件管理器 >>> 更新命令: '{name}' 在模块 {module_name} 中")
                else:
                    # 不同模块的命令冲突，发出警告
                    logger.warning(f"⚠️ 命令冲突: '{name}' 已在模块 {existing_module} 中注册，现在被模块 {module_name} 覆盖")
            else:
                logger.debug(f"插件管理器 >>> 注册命令: '{name}' 在模块 {module_name} 中")
            
            # 为每个命令名注册相同的处理函数和事件类型
            COMMAND_REGISTRY[name] = {
                'handler': func,
                'event_type': event_type
            }
        return func
    return decorator

def group_add(func):
    """加群事件处理装饰器
    
    Args:
        func: 处理函数
        
    Returns:
        装饰器函数
    """
    # 获取当前模块名，用于日志记录
    module_name = func.__module__
    
    if "group_add" in GROUP_ADD_REGISTRY:
        # 检查是否是同一个模块的处理器
        existing_module = GROUP_ADD_REGISTRY["group_add"]['handler'].__module__
        if existing_module == module_name:
            # 同一模块重复注册，直接覆盖
            logger.debug(f"插件管理器 >>> 更新加群事件处理器在模块 {module_name} 中")
        else:
            # 不同模块的处理器冲突，发出警告
            logger.warning(f"⚠️ 加群事件处理器冲突: 已在模块 {existing_module} 中注册，现在被模块 {module_name} 覆盖")
    else:
        logger.debug(f"插件管理器 >>> 注册加群事件处理器在模块 {module_name} 中")
    
    # 注册加群事件处理函数
    GROUP_ADD_REGISTRY["group_add"] = {
        'handler': func
    }
    return func

def friend_add(func):
    """私聊加好友事件处理装饰器
    
    Args:
        func: 处理函数
        
    Returns:
        装饰器函数
    """
    # 获取当前模块名，用于日志记录
    module_name = func.__module__
    
    if "friend_add" in FRIEND_ADD_REGISTRY:
        # 检查是否是同一个模块的处理器
        existing_module = FRIEND_ADD_REGISTRY["friend_add"]['handler'].__module__
        if existing_module == module_name:
            # 同一模块重复注册，直接覆盖
            logger.debug(f"插件管理器 >>> 更新加好友事件处理器在模块 {module_name} 中")
        else:
            # 不同模块的处理器冲突，发出警告
            logger.warning(f"⚠️ 加好友事件处理器冲突: 已在模块 {existing_module} 中注册，现在被模块 {module_name} 覆盖")
    else:
        logger.debug(f"插件管理器 >>> 注册加好友事件处理器在模块 {module_name} 中")
    
    # 注册加群事件处理函数
    FRIEND_ADD_REGISTRY["friend_add"] = {
        'handler': func
    }
    return func

def interaction_add(func):
    """按钮互动事件处理装饰器
    
    Args:
        func: 处理函数
        
    Returns:
        装饰器函数
    """
    # 获取当前模块名，用于日志记录
    module_name = func.__module__
    
    if "interaction_add" in INTERACTION_REGISTRY:
        # 检查是否是同一个模块的处理器
        existing_module = INTERACTION_REGISTRY["interaction_add"]['handler'].__module__
        if existing_module == module_name:
            # 同一模块重复注册，直接覆盖
            logger.debug(f"插件管理器 >>> 更新按钮互动事件处理器在模块 {module_name} 中")
        else:
            # 不同模块的处理器冲突，发出警告
            logger.warning(f"⚠️ 按钮互动事件事件处理器冲突: 已在模块 {existing_module} 中注册，现在被模块 {module_name} 覆盖")
    else:
        logger.debug(f"插件管理器 >>> 注册按钮互动事件处理器在模块 {module_name} 中")
    
    # 注册按钮互动事件处理函数
    INTERACTION_REGISTRY["interaction_add"] = {
        'handler': func
    }
    return func

async def get_command_handler(cmd: str, event_class: type) -> Optional[Callable]:
    """获取命令处理函数（添加事件类型检查）"""
    if cmd not in COMMAND_REGISTRY:
        return None
    
    handler_info = COMMAND_REGISTRY[cmd]
    handler = handler_info['handler']
    supported_event = handler_info['event_type']
    
    # 检查事件类型是否匹配
    if supported_event is None or issubclass(event_class, supported_event):
        return handler
    
    return None  # 事件类型不匹配

async def get_group_add_handler() -> Optional[Callable]:
    """获取加群事件处理函数"""
    if "group_add" not in GROUP_ADD_REGISTRY:
        return None
    
    handler_info = GROUP_ADD_REGISTRY["group_add"]
    handler = handler_info['handler']
    return handler

async def get_interaction_handler() -> Optional[Callable]:
    """获取按钮INTERACTION事件处理函数"""
    if "interaction_add" not in INTERACTION_REGISTRY:
        return None
    
    handler_info = INTERACTION_REGISTRY["interaction_add"]
    handler = handler_info['handler']
    return handler

async def get_friend_add_handler() -> Optional[Callable]:
    """获取加好友事件处理函数"""
    if "friend_add" not in FRIEND_ADD_REGISTRY:
        return None
    
    handler_info = FRIEND_ADD_REGISTRY["friend_add"]
    handler = handler_info['handler']
    return handler



# 新增插件API处理函数
async def get_plugins_list():
    """获取插件列表"""
    global PLUGIN_DIR
    if PLUGIN_DIR is None:
        return {"code": 500, "data": {
            "title": "插件系统未初始化",
            "description": "插件系统尚未初始化，请稍后再试或检查配置。"
        }}
    
    plugins = []
    plugin_dir = Path(PLUGIN_DIR)
    
    # 遍历插件目录中的所有.py文件
    for file in plugin_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
            
        plugin_name = file.stem
        # 获取插件详细信息
        plugin_info = await _get_plugin_info(file)
        plugins.append(plugin_info)
    
    return {"code": 200, "data": {"plugins": plugins}}

async def _get_plugin_info(plugin_path: Path) -> dict:
    """获取单个插件的详细信息"""
    plugin_name = plugin_path.stem
    
    # 默认插件信息
    plugin_info = {
        "name": plugin_name,
        "version": "1.0.0",
        "description": "插件描述信息",
        "author": "未知作者",
        "enabled": plugin_name in sys.modules,  # 简单判断是否已加载
        "official": plugin_name in ["axt_plugin_"],  # 示例官方插件
        "installed": True,  # 本地插件默认已安装
        "file_name": plugin_name + ".py"
    }
    
    # 尝试从插件文件中读取元数据
    try:
        with open(plugin_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 简单解析插件元数据（可以从注释中提取）
        lines = content.split('\n')
        for line in lines[:10]:  # 只检查前10行
            if line.startswith('# VERSION:'):
                plugin_info["version"] = line.split(':', 1)[1].strip()
            elif line.startswith('# AUTHOR:'):
                plugin_info["author"] = line.split(':', 1)[1].strip()
            elif line.startswith('# DESCRIPTION:'):
                plugin_info["description"] = line.split(':', 1)[1].strip()
                
        # 解析模块中的__metadata__字段，但不实际加载模块
        # 使用正则表达式查找__metadata__定义
        import re
        metadata_match = re.search(r'__metadata__\s*=\s*({.*?})', content, re.DOTALL)
        if metadata_match:
            try:
                # 安全地评估metadata字典（仅限字面量）
                metadata_str = metadata_match.group(1)
                # 使用ast.literal_eval来安全地解析字典
                import ast
                metadata = ast.literal_eval(metadata_str)
                if isinstance(metadata, dict):
                    plugin_info.update(metadata)
            except (ValueError, SyntaxError):
                logger.debug(f"无法解析插件 {plugin_name} 的 __metadata__")
                
    except Exception as e:
        logger.debug(f"无法读取插件 {plugin_name} 的元数据: {e}")
    
    return plugin_info

async def toggle_plugin(name: str, enable: bool):
    """切换插件状态"""
    global PLUGIN_DIR, COMMAND_REGISTRY
    if PLUGIN_DIR is None:
        return {"code": 500, "data": {
            "title": "插件系统未初始化",
            "description": "插件系统尚未初始化，请稍后再试或检查配置。"

        }}
    
    try:
        if enable:
            # 启用插件逻辑（这里简化处理）
            plugin_path = Path(PLUGIN_DIR) / f"{name}.py"
            if not plugin_path.exists():
                return {"code": 404, "data": {
                    "title": "插件不存在",
                    "description": f"插件 {name} 不存在，请检查名称是否正确。"
                }}
            
            # 检查插件是否已经加载
            if name in sys.modules:
                return {"code": 200, "data": {
                    "title": "插件已启用",
                    "description": f"插件 {name} 已经启用，请勿重复启用。"
                }}
            
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            
            # 调用初始化函数（如果有）
            if hasattr(module, "initialize"):
                module.initialize()
        else:
            # 禁用插件逻辑
            if name in sys.modules:
                module = sys.modules[name]
                if hasattr(module, "shutdown"):
                    module.shutdown()
                
                # 清除该插件注册的命令
                commands_to_remove = []
                for cmd, info in COMMAND_REGISTRY.items():
                    if info['handler'].__module__ == name:
                        commands_to_remove.append(cmd)
                
                for cmd in commands_to_remove:
                    logger.info(f"插件管理器 >>> 移除命令: {cmd}")
                    del COMMAND_REGISTRY[cmd]
                
                del sys.modules[name]
        
        return {"code": 200, "data": {
            "title": "插件操作成功",
            "description": f"插件 {name} {'已启用' if enable else '已禁用'}。"
        }}
    except Exception as e:
        return {"code": 500, "data": {
            "title": "操作失败",
            "description": f"插件状态切换失败，错误信息为: {str(e)}"
        }}

async def install_plugin(url: str, version: str = None):
    """安装插件
    
    Args:
        url: 插件的远程URL
        version: 插件版本（可选）
    
    Returns:
        安装结果
    """
    global PLUGIN_DIR, COMMAND_REGISTRY
    if PLUGIN_DIR is None:
        return {"code": 500, "data": {
            "title": "插件系统未初始化",
            "description": "插件系统尚未初始化，请稍后再试或检查配置。"
        }}
    
    try:
        # 验证URL格式
        import requests
        from urllib.parse import urlparse
        
        # 检查URL是否有效
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return {"code": 400, "data": {
                "title": "无效的URL",
                "description": "请提供有效的远程URL地址。"
            }}
        
        # 解析URL获取文件名
        file_name = os.path.basename(parsed_url.path)
        if not file_name.endswith('.py'):
            return {"code": 400, "data": {
                "title": "无效的插件文件",
                "description": "插件文件必须是.py文件。"
            }}
        
        plugin_name = file_name[:-3]  # 去掉.py后缀
        
        # 检查插件是否已存在，如果存在则先卸载
        plugin_path = Path(PLUGIN_DIR) / file_name
        if plugin_path.exists():
            # 如果插件已加载，先卸载
            if plugin_name in sys.modules:
                # 清除该插件注册的命令
                commands_to_remove = []
                for cmd, info in COMMAND_REGISTRY.items():
                    if info['handler'].__module__ == plugin_name:
                        commands_to_remove.append(cmd)
                
                for cmd in commands_to_remove:
                    logger.info(f"插件管理器 >>> 移除命令: {cmd}")
                    del COMMAND_REGISTRY[cmd]
                
                # 调用插件的shutdown函数
                module = sys.modules[plugin_name]
                if hasattr(module, "shutdown"):
                    module.shutdown()
                
                del sys.modules[plugin_name]
        
        # 从远程URL下载插件文件
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # 如果请求失败则抛出异常
            
            # 将下载的内容写入插件文件
            with open(plugin_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"插件管理器 >>> 已从远程下载并安装插件: {file_name}")
        except requests.exceptions.RequestException as e:
            return {"code": 404, "data": {
                "title": "插件下载失败",
                "description": f"无法从远程URL下载插件: {str(e)}"
            }}
        
        # 加载新安装的插件
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            # 调用初始化函数（如果有）
            if hasattr(module, "initialize"):
                module.initialize()
                logger.info(f"插件管理器 >>> 插件 {plugin_name} 初始化完成")
        except Exception as e:
            # 加载失败，删除插件文件
            plugin_path.unlink(missing_ok=True)
            return {"code": 500, "data": {
                "title": "插件加载失败",
                "description": f"插件安装成功但加载失败: {str(e)}"
            }}
        
        return {"code": 200, "data": {
            "title": "插件安装成功",
            "description": f"插件 {plugin_name} 安装并加载成功。"
        }}
    except Exception as e:
        return {"code": 500, "data": {
            "title": "安装失败",
            "description": f"插件安装失败，错误信息为: {str(e)}"
        }}

async def uninstall_plugin(name: str):
    """卸载插件"""
    global PLUGIN_DIR, COMMAND_REGISTRY
    if PLUGIN_DIR is None:
        return {"code": 500, "data": {
            "title": "插件系统未初始化",
            "description": "插件系统尚未初始化，请稍后再试或检查配置。"
        }}
    
    try:
        # 先禁用插件
        if name in sys.modules:
            module = sys.modules[name]
            if hasattr(module, "shutdown"):
                module.shutdown()
            
            # 清除该插件注册的命令
            commands_to_remove = []
            for cmd, info in COMMAND_REGISTRY.items():
                if info['handler'].__module__ == name:
                    commands_to_remove.append(cmd)
            
            for cmd in commands_to_remove:
                logger.info(f"插件管理器 >>> 移除命令: {cmd}")
                del COMMAND_REGISTRY[cmd]
            
            del sys.modules[name]
        
        # 删除插件文件
        plugin_path = Path(PLUGIN_DIR) / f"{name}.py"
        if plugin_path.exists():
            plugin_path.unlink()
            logger.info(f"插件管理器 >>> 已删除插件文件: {name}.py")
        else:
            return {"code": 404, "data": {
                "title": "插件不存在",
                "description": f"插件 {name} 不存在，请检查名称是否正确。"
            }}
        
        return {"code": 200, "data": {
            "title": "插件卸载成功",
            "description": f"插件 {name} 卸载成功。"
        }}
    except Exception as e:
        return {"code": 500, "data": {
            "title": "卸载失败",
            "description": f"插件卸载失败，错误信息为: {str(e)}"
        }}

async def initialize_plugins():
    """初始化插件系统（只执行一次）"""
    global PLUGIN_DIR
    
    if PLUGIN_DIR is not None:
        return  # 已经初始化过
    
    # 获取插件目录路径

    plugin_dir = Path(config.Plugins.dir)
    PLUGIN_DIR = str(plugin_dir)
    
    # 确保插件目录存在
    os.makedirs(plugin_dir, exist_ok=True)
    
    # 加载所有插件
    logger.debug(f"插件管理器 >>> 从 {plugin_dir} 目录加载插件")
    
    for file in plugin_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
            
        plugin_name = file.stem
        logger.info(f"插件管理器 >>>   - 发现插件: {plugin_name}")
        
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(plugin_name, file)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            # 调用初始化函数（如果有）
            if hasattr(module, "initialize"):
                module.initialize()
                logger.info(f"插件管理器 >>>     插件初始化完成")
        except Exception as e:
            logger.error(f"插件管理器 >>>     加载失败: {str(e)}")
            raise
    logger.info(f"插件管理器 >>>     所有插件加载结束")

async def shutdown_plugins():
    """关闭插件系统"""
    logger.info("插件管理器 >>> 关闭插件系统")
    # 调用所有插件的shutdown函数
    for module in sys.modules.values():
        if hasattr(module, "shutdown"):
            try:
                if module.__name__ == "logging":
                    continue
                module.shutdown()
                logger.info(f"插件管理器 >>>   - 已关闭: {module.__name__}")
            except Exception as e:
                logger.error(f"插件管理器 >>>   - 关闭失败: {module.__name__} - {str(e)}")
    # 清理命令注册表
    COMMAND_REGISTRY.clear()
    # 清理加群事件注册表
    GROUP_ADD_REGISTRY.clear()