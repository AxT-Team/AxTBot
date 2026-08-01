"""
Message Processing Modules for Union Framework

Author: Shanshui2024
Organization: AxT-Team
"""

import inspect

handlers = {
    "command": [],    # 每个元素: {"name": cmd, "func": func, "event_type": <class>}
    "message": [],    # 每个元素: {"keyword": kw, "func": func, "event_type": <class>}
    "all": [],        # 全局消息
    "interaction": [] # 互动事件
}

def _get_event_annotation(func):
    """提取函数第一个参数（通常命名为 event）的类型注解，若没有则返回 object（通配）"""
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    
    # 如果没有参数，或者第一个参数没有注解，默认匹配所有事件
    if not params:
        return object
    
    first_param = params[0]
    # 如果注解是 inspect._empty（即没写 : type），也当作通配
    if first_param.annotation == inspect._empty:
        return object
    
    return first_param.annotation


def on_command(cmd_name):
    def decorator(func):
        event_type = _get_event_annotation(func)
        handlers["command"].append({
            "name": cmd_name,
            "func": func,
            "event_type": event_type  # 存下期望的事件类型
        })
        return func
    return decorator

def on_message(keyword=None):
    def decorator(func):
        event_type = _get_event_annotation(func)
        handlers["message"].append({
            "keyword": keyword,
            "func": func,
            "event_type": event_type
        })
        return func
    return decorator

def on_all_message():
    def decorator(func):
        event_type = _get_event_annotation(func)  # 复用之前的类型提取
        handlers["all"].append({
            "func": func,
            "event_type": event_type
        })
        return func
    return decorator

def on_interaction(interaction_type: int = None):
    """
    注册互动事件处理器
    :param interaction_type: 指定互动类型 (如 11)，为 None 则匹配所有
    """
    def decorator(func):
        event_type = _get_event_annotation(func)  # 复用之前的类型提取
        handlers["interaction"].append({
            "type": interaction_type,   # 存储整数类型
            "func": func,
            "event_type": event_type
        })
        return func
    return decorator